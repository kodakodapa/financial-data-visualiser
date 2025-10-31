#!/usr/bin/env python3
"""
Backfill OECD Data - Historical Data Import Tool

Usage:
    # Backfill GDP per capita from 1995
    python scripts/backfill_oecd_data.py gdp_per_capita --start 1995-Q1 --end 2025-Q3

    # Backfill in 5-year batches (safer for large ranges)
    python scripts/backfill_oecd_data.py gdp_per_capita --start 1995-Q1 --end 2025-Q3 --batch-years 5

    # Backfill all datasets
    python scripts/backfill_oecd_data.py --all --start 2020-Q1 --end 2025-Q3

    # Dry run to see what would be fetched
    python scripts/backfill_oecd_data.py gdp_per_capita --start 2020-Q1 --end 2020-Q4 --dry-run
"""

import argparse
import logging
import sys
import os
from oecd import OECDDataFetcher, OECDQueryBuilder, list_configs

# Ensure logs directory exists (relative to project root)
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'oecd_backfill.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def split_into_batches(start_period, end_period, batch_years=5):
    """
    Split a large time range into smaller batches.

    Args:
        start_period: Start period (e.g., '1995-Q1')
        end_period: End period (e.g., '2025-Q3')
        batch_years: Number of years per batch

    Returns:
        list: List of (batch_start, batch_end) tuples
    """
    # Parse periods
    start_year, start_q = start_period.split('-Q')
    start_year = int(start_year)
    start_quarter = int(start_q)

    end_year, end_q = end_period.split('-Q')
    end_year = int(end_year)
    end_quarter = int(end_q)

    batches = []
    current_year = start_year
    current_quarter = start_quarter

    while current_year < end_year or (current_year == end_year and current_quarter <= end_quarter):
        batch_start = f"{current_year}-Q{current_quarter}"

        # Calculate batch end (batch_years later)
        batch_end_year = current_year + batch_years
        batch_end_quarter = current_quarter

        # Don't exceed the overall end period
        if batch_end_year > end_year or (batch_end_year == end_year and batch_end_quarter > end_quarter):
            batch_end_year = end_year
            batch_end_quarter = end_quarter

        batch_end = f"{batch_end_year}-Q{batch_end_quarter}"
        batches.append((batch_start, batch_end))

        # Move to next batch
        current_year = batch_end_year
        current_quarter = batch_end_quarter + 1
        if current_quarter > 4:
            current_quarter = 1
            current_year += 1

    return batches


def main():
    parser = argparse.ArgumentParser(
        description='Backfill historical OECD data',
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
        help='Backfill all configured datasets'
    )

    parser.add_argument(
        '--start',
        required=True,
        metavar='PERIOD',
        help='Start period (e.g., 1995-Q1)'
    )

    parser.add_argument(
        '--end',
        required=True,
        metavar='PERIOD',
        help='End period (e.g., 2025-Q3)'
    )

    parser.add_argument(
        '--batch-years',
        type=int,
        metavar='N',
        help='Split into batches of N years (recommended for large ranges)'
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

    # Determine which configs to backfill
    if args.all:
        configs_to_fetch = list_configs()
    elif args.config:
        configs_to_fetch = [args.config]
    else:
        parser.error("Must specify either a config name or --all")
        return 1

    # Determine batches
    if args.batch_years:
        batches = split_into_batches(args.start, args.end, args.batch_years)
        logger.info(f"Split into {len(batches)} batches of {args.batch_years} years each")
    else:
        batches = [(args.start, args.end)]
        logger.info("Processing as single batch")

    # Initialize fetcher
    fetcher = OECDDataFetcher()

    # Process each config
    overall_results = {}

    for config_name in configs_to_fetch:
        logger.info(f"\n{'=' * 70}")
        logger.info(f"BACKFILLING: {config_name}")
        logger.info(f"{'=' * 70}")

        config_results = []

        # Process each batch
        for i, (batch_start, batch_end) in enumerate(batches, 1):
            try:
                logger.info(f"\nBatch {i}/{len(batches)}: {batch_start} to {batch_end}")

                result = fetcher.fetch_and_upsert(
                    config_name=config_name,
                    start_period=batch_start,
                    end_period=batch_end,
                    dry_run=args.dry_run,
                    filter_status=not args.no_filter_status,
                    include_provisional=args.include_provisional
                )

                config_results.append(result)

                # Log batch result
                if result.get('success'):
                    logger.info(f"  ✓ Batch complete: {result['points_fetched']} points fetched")
                else:
                    logger.error(f"  ✗ Batch failed: {result.get('error', 'Unknown error')}")
                    # Continue with next batch instead of stopping

            except Exception as e:
                logger.error(f"  ✗ Batch failed with exception: {e}", exc_info=True)
                config_results.append({'success': False, 'error': str(e)})

        # Aggregate results for this config
        total_fetched = sum(r.get('points_fetched', 0) for r in config_results)
        total_inserted = sum(r.get('points_inserted', 0) for r in config_results)
        total_updated = sum(r.get('points_updated', 0) for r in config_results)
        all_success = all(r.get('success', False) for r in config_results)

        overall_results[config_name] = {
            'success': all_success,
            'total_fetched': total_fetched,
            'total_inserted': total_inserted,
            'total_updated': total_updated,
            'batches_processed': len(config_results),
            'batches_succeeded': sum(1 for r in config_results if r.get('success', False))
        }

    # Print summary
    print("\n" + "=" * 70)
    print("BACKFILL SUMMARY")
    print("=" * 70)

    for config_name, result in overall_results.items():
        print(f"\n{config_name}:")
        print(f"  Batches: {result['batches_succeeded']}/{result['batches_processed']} succeeded")
        print(f"  Fetched: {result['total_fetched']} points")
        if not args.dry_run:
            print(f"  Inserted: {result['total_inserted']}")
            print(f"  Updated: {result['total_updated']}")
        print(f"  Status: {'✓ SUCCESS' if result['success'] else '✗ PARTIAL/FAILED'}")

    # Cleanup
    fetcher.close()

    # Return exit code
    all_success = all(r['success'] for r in overall_results.values())
    return 0 if all_success else 1


if __name__ == '__main__':
    sys.exit(main())
