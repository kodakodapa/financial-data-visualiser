#!/usr/bin/env python3
"""
Fetch OECD Data - Manual/Periodic Update Tool

Usage:
    # Fetch latest 2 quarters for GDP per capita
    python scripts/fetch_oecd_data.py gdp_per_capita --latest 2

    # Fetch specific period
    python scripts/fetch_oecd_data.py gdp_per_capita --start 2025-Q2 --end 2025-Q3

    # Fetch all configured datasets
    python scripts/fetch_oecd_data.py --all --latest 1

    # Dry run (fetch but don't save to database)
    python scripts/fetch_oecd_data.py gdp_per_capita --latest 1 --dry-run
"""

import argparse
import logging
import sys
import os
from datetime import datetime
from oecd import OECDDataFetcher, list_configs

# Ensure logs directory exists (relative to project root)
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'oecd_fetch.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def calculate_latest_periods(lookback_quarters=2):
    """
    Calculate start and end periods for fetching latest data.

    Args:
        lookback_quarters: Number of quarters to look back from current

    Returns:
        tuple: (start_period, end_period) as strings (e.g., '2025-Q2')
    """
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Determine current quarter
    current_quarter = (current_month - 1) // 3 + 1

    # Calculate start period
    start_quarter = current_quarter - lookback_quarters + 1
    start_year = current_year

    while start_quarter < 1:
        start_quarter += 4
        start_year -= 1

    start_period = f"{start_year}-Q{start_quarter}"
    end_period = f"{current_year}-Q{current_quarter}"

    return start_period, end_period


def main():
    parser = argparse.ArgumentParser(
        description='Fetch economic data from OECD API and upsert to database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'config',
        nargs='?',
        help='Data configuration name (e.g., gdp_per_capita, real_gdp)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Fetch all configured datasets'
    )

    parser.add_argument(
        '--latest',
        type=int,
        metavar='N',
        help='Fetch latest N quarters (e.g., --latest 2)'
    )

    parser.add_argument(
        '--start',
        metavar='PERIOD',
        help='Start period (e.g., 2025-Q1)'
    )

    parser.add_argument(
        '--end',
        metavar='PERIOD',
        help='End period (e.g., 2025-Q3)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Fetch and parse but do not write to database'
    )

    parser.add_argument(
        '--include-provisional',
        action='store_true',
        help='Include provisional data (status P). By default, only Normal (A) and Estimated (E) data is included.'
    )

    parser.add_argument(
        '--no-filter-status',
        action='store_true',
        help='Disable status filtering (accept all data regardless of observation status)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available data configurations and exit'
    )

    args = parser.parse_args()

    # List configs and exit
    if args.list:
        configs = list_configs()
        print("Available data configurations:")
        for config in configs:
            print(f"  - {config}")
        return 0

    # Determine which configs to fetch
    if args.all:
        configs_to_fetch = list_configs()
    elif args.config:
        configs_to_fetch = [args.config]
    else:
        parser.error("Must specify either a config name or --all")
        return 1

    # Determine time period
    if args.latest:
        start_period, end_period = calculate_latest_periods(args.latest)
        logger.info(f"Fetching latest {args.latest} quarters: {start_period} to {end_period}")
    elif args.start and args.end:
        start_period = args.start
        end_period = args.end
        logger.info(f"Fetching period: {start_period} to {end_period}")
    else:
        parser.error("Must specify either --latest N or both --start and --end")
        return 1

    # Initialize fetcher
    fetcher = OECDDataFetcher()

    # Fetch each config
    results = {}
    for config_name in configs_to_fetch:
        try:
            logger.info(f"\n{'=' * 70}")
            logger.info(f"Processing: {config_name}")
            logger.info(f"{'=' * 70}")

            result = fetcher.fetch_and_upsert(
                config_name=config_name,
                start_period=start_period,
                end_period=end_period,
                dry_run=args.dry_run,
                filter_status=not args.no_filter_status,
                include_provisional=args.include_provisional
            )

            results[config_name] = result

        except Exception as e:
            logger.error(f"Failed to fetch {config_name}: {e}", exc_info=True)
            results[config_name] = {'success': False, 'error': str(e)}

    # Print summary
    print("\n" + "=" * 70)
    print("FETCH SUMMARY")
    print("=" * 70)

    for config_name, result in results.items():
        if result.get('success'):
            print(f"\n{config_name}:")
            print(f"  [OK] Fetched: {result['points_fetched']} points")
            if not args.dry_run:
                print(f"  [OK] Inserted: {result['points_inserted']}")
                print(f"  [OK] Updated: {result['points_updated']}")
        else:
            print(f"\n{config_name}:")
            print(f"  [FAIL] Error: {result.get('error', 'Unknown error')}")

    # Cleanup
    fetcher.close()

    # Return exit code
    all_success = all(r.get('success', False) for r in results.values())
    return 0 if all_success else 1


if __name__ == '__main__':
    sys.exit(main())
