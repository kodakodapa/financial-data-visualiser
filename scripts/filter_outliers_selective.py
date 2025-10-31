#!/usr/bin/env python3
"""
Selectively filter outlier datapoints from economic data.
Removes individual quarters that are clearly erroneous, preserving the rest of the series.
"""

import sqlite3
import os
from collections import defaultdict

def parse_quarter(quarter_str):
    """Parse quarter string (e.g., '1995-Q2') for sorting."""
    try:
        year, quarter = quarter_str.split('-Q')
        return (int(year), int(quarter))
    except:
        return (0, 0)

def filter_outliers_selective(db_path, threshold_pct=20.0, metrics=None, dry_run=False):
    """
    Selectively remove individual outlier datapoints.

    Strategy for identifying outliers:
    1. Spike-and-revert: Value jumps >threshold% then drops >threshold% next quarter
    2. Drop-and-recover: Value drops >threshold% then jumps >threshold% next quarter
    3. Isolated spike: Value differs greatly from both neighbors

    Args:
        db_path: Path to the SQLite database
        threshold_pct: Percentage threshold for extreme changes (default 20%)
        metrics: List of metrics to filter (default: ['real_gdp', 'gdp_per_capita'])
        dry_run: If True, only report what would be deleted

    Returns:
        Number of datapoints removed
    """
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        return 0

    if metrics is None:
        metrics = ['real_gdp', 'gdp_per_capita']

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"\n{'=' * 80}")
    print(f"SELECTIVE OUTLIER FILTER")
    print(f"{'=' * 80}")
    print(f"Threshold: ±{threshold_pct}% quarter-over-quarter")
    print(f"Metrics: {', '.join(metrics)}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will delete data)'}\n")

    all_deletions = []

    for metric in metrics:
        print(f"\n{'=' * 80}")
        print(f"Processing: {metric}")
        print(f"{'=' * 80}\n")

        # Get all data for this metric
        cursor.execute('''
            SELECT country, time_period, value
            FROM economic_data
            WHERE metric_name = ?
            ORDER BY country, time_period
        ''', (metric,))

        # Organize by country
        country_data = defaultdict(list)
        for row in cursor.fetchall():
            country_data[row['country']].append({
                'time_period': row['time_period'],
                'value': row['value']
            })

        metric_deletions = []

        for country, data_points in country_data.items():
            # Sort by time period
            data_points.sort(key=lambda x: parse_quarter(x['time_period']))

            if len(data_points) < 3:
                continue

            # Check each point for outlier patterns
            for i in range(1, len(data_points) - 1):
                prev_point = data_points[i-1]
                curr_point = data_points[i]
                next_point = data_points[i+1]

                prev_val = prev_point['value']
                curr_val = curr_point['value']
                next_val = next_point['value']

                if prev_val <= 0 or curr_val <= 0 or next_val <= 0:
                    continue

                # Calculate changes
                pct_change_to_curr = ((curr_val - prev_val) / prev_val) * 100
                pct_change_from_curr = ((next_val - curr_val) / curr_val) * 100

                # Pattern 1: Spike-and-revert (V-shape up)
                # Current value spikes up, then drops back down
                if (pct_change_to_curr > threshold_pct and
                    pct_change_from_curr < -threshold_pct):
                    metric_deletions.append({
                        'country': country,
                        'time_period': curr_point['time_period'],
                        'value': curr_val,
                        'reason': f'Spike-revert: +{pct_change_to_curr:.1f}% then {pct_change_from_curr:.1f}%'
                    })
                    continue

                # Pattern 2: Drop-and-recover (V-shape down)
                # Current value drops down, then recovers
                if (pct_change_to_curr < -threshold_pct and
                    pct_change_from_curr > threshold_pct):
                    metric_deletions.append({
                        'country': country,
                        'time_period': curr_point['time_period'],
                        'value': curr_val,
                        'reason': f'Drop-recover: {pct_change_to_curr:.1f}% then +{pct_change_from_curr:.1f}%'
                    })
                    continue

                # Pattern 3: Isolated extreme outlier
                # Current value is far from BOTH neighbors
                if abs(pct_change_to_curr) > threshold_pct and abs(pct_change_from_curr) > threshold_pct:
                    # Check if neighbors are more consistent with each other
                    neighbor_avg = (prev_val + next_val) / 2
                    dev_from_avg = abs((curr_val - neighbor_avg) / neighbor_avg * 100)

                    # If current deviates >30% from average of neighbors, it's likely an outlier
                    if dev_from_avg > 30:
                        metric_deletions.append({
                            'country': country,
                            'time_period': curr_point['time_period'],
                            'value': curr_val,
                            'reason': f'Isolated outlier: {dev_from_avg:.1f}% from neighbors'
                        })

        print(f"Found {len(metric_deletions)} outlier datapoints to delete\n")

        if metric_deletions:
            # Group by country for display
            by_country = defaultdict(list)
            for d in metric_deletions:
                by_country[d['country']].append(d)

            print(f"Outliers by country (showing first 20):")
            print(f"{'Country':<30} {'Count':>6} {'Sample Periods':<40}")
            print("-" * 80)

            sorted_countries = sorted(by_country.items(), key=lambda x: len(x[1]), reverse=True)
            for country, deletions in sorted_countries[:20]:
                sample = ', '.join([d['time_period'] for d in deletions[:3]])
                if len(deletions) > 3:
                    sample += f" (+{len(deletions)-3} more)"
                print(f"{country:<30} {len(deletions):>6} {sample:<40}")

            if len(sorted_countries) > 20:
                print(f"... and {len(sorted_countries) - 20} more countries")

        all_deletions.extend([{**d, 'metric': metric} for d in metric_deletions])

    # Summary and deletion
    print(f"\n{'=' * 80}")
    print(f"SUMMARY")
    print(f"{'=' * 80}\n")
    print(f"Total outlier datapoints to delete: {len(all_deletions)}\n")

    if not dry_run and all_deletions:
        print("Deleting outlier datapoints...")

        deleted_count = 0
        for deletion in all_deletions:
            cursor.execute('''
                DELETE FROM economic_data
                WHERE metric_name = ? AND country = ? AND time_period = ?
            ''', (deletion['metric'], deletion['country'], deletion['time_period']))
            deleted_count += 1

            if deleted_count % 100 == 0:
                print(f"  Deleted {deleted_count} records...")

        conn.commit()

        print(f"\n{'=' * 80}")
        print(f"DELETION COMPLETE")
        print(f"{'=' * 80}")
        print(f"Total records deleted: {deleted_count}")

        # Show updated database stats
        cursor.execute('SELECT COUNT(*) as total FROM economic_data')
        total_count = cursor.fetchone()['total']
        print(f"Remaining records in database: {total_count}")

    elif dry_run:
        print("DRY RUN - No changes made to database")
        print(f"Would delete {len(all_deletions)} records")

    conn.close()

    return len(all_deletions) if not dry_run else len(all_deletions)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Selectively filter outliers from economic database')
    parser.add_argument(
        '--threshold',
        type=float,
        default=20.0,
        help='Percentage threshold for extreme changes (default: 20.0)'
    )
    parser.add_argument(
        '--metric',
        type=str,
        action='append',
        dest='metrics',
        help='Metric to filter (can be specified multiple times)'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='data/economic_data.db',
        help='Path to database (default: data/economic_data.db)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )

    args = parser.parse_args()

    metrics = args.metrics if args.metrics else ['real_gdp', 'gdp_per_capita']

    filter_outliers_selective(args.db, args.threshold, metrics, args.dry_run)
