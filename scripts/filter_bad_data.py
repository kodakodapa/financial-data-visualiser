#!/usr/bin/env python3
"""
Filter and remove bad datapoints from the economic database.
Removes datapoints with extreme quarter-over-quarter changes that indicate data errors.
"""

import sqlite3
import os
from collections import defaultdict
from datetime import datetime

def parse_quarter(quarter_str):
    """Parse quarter string (e.g., '1995-Q2') for sorting."""
    try:
        year, quarter = quarter_str.split('-Q')
        return (int(year), int(quarter))
    except:
        return (0, 0)

def filter_bad_data(db_path, threshold_pct=20.0, metrics=None, dry_run=False):
    """
    Filter and remove bad datapoints with extreme quarter-over-quarter changes.

    Strategy:
    1. Detect extreme changes (> threshold_pct)
    2. For consecutive datapoints with extreme changes, keep the one that's more consistent
       with surrounding data
    3. Remove obvious outliers

    Args:
        db_path: Path to the SQLite database
        threshold_pct: Percentage threshold for flagging extreme changes (default 20%)
        metrics: List of metrics to filter (default: ['real_gdp'])
        dry_run: If True, only report what would be deleted without actually deleting

    Returns:
        Number of datapoints removed
    """
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        return 0

    if metrics is None:
        metrics = ['real_gdp']

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"\n{'=' * 80}")
    print(f"DATA QUALITY FILTER")
    print(f"{'=' * 80}")
    print(f"Threshold: ±{threshold_pct}% quarter-over-quarter")
    print(f"Metrics: {', '.join(metrics)}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will delete data)'}\n")

    total_deleted = 0
    deletion_candidates = []

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
                continue  # Need at least 3 points to detect outliers

            # Identify extreme changes and mark for deletion
            i = 1
            while i < len(data_points):
                prev_point = data_points[i-1]
                curr_point = data_points[i]

                prev_val = prev_point['value']
                curr_val = curr_point['value']

                if prev_val > 0:
                    pct_change = ((curr_val - prev_val) / prev_val) * 100

                    if abs(pct_change) > threshold_pct:
                        # Found extreme change - determine which point to delete

                        # Check if there's a next point
                        if i + 1 < len(data_points):
                            next_point = data_points[i+1]
                            next_val = next_point['value']

                            # Calculate change from current to next
                            pct_change_next = ((next_val - curr_val) / curr_val) * 100

                            # If both changes are extreme and opposite direction,
                            # current point is likely the outlier
                            if abs(pct_change_next) > threshold_pct and (pct_change * pct_change_next < 0):
                                # Current point is an outlier - mark for deletion
                                metric_deletions.append({
                                    'country': country,
                                    'time_period': curr_point['time_period'],
                                    'value': curr_val,
                                    'reason': f'Outlier: {pct_change:+.1f}% from prev, {pct_change_next:+.1f}% to next'
                                })
                                i += 2  # Skip the deleted point
                                continue

                            # Check if next point returns to normal
                            if i >= 2:
                                point_before = data_points[i-2]
                                avg_neighbors = (point_before['value'] + next_val) / 2

                                # If current is far from average of neighbors but prev is close
                                dev_curr = abs((curr_val - avg_neighbors) / avg_neighbors * 100)
                                dev_prev = abs((prev_val - avg_neighbors) / avg_neighbors * 100)

                                if dev_curr > 30 and dev_prev < 15:
                                    # Current is likely the outlier
                                    metric_deletions.append({
                                        'country': country,
                                        'time_period': curr_point['time_period'],
                                        'value': curr_val,
                                        'reason': f'Deviates {dev_curr:.1f}% from neighbors vs {dev_prev:.1f}%'
                                    })
                                    i += 2
                                    continue

                i += 1

        print(f"Found {len(metric_deletions)} datapoints to delete\n")

        if metric_deletions:
            print("Sample deletions (first 10):")
            print(f"{'Country':<25} {'Period':<10} {'Value':>15} {'Reason':<50}")
            print("-" * 105)
            for deletion in metric_deletions[:10]:
                print(f"{deletion['country']:<25} "
                      f"{deletion['time_period']:<10} "
                      f"{deletion['value']:>15,.1f} "
                      f"{deletion['reason']:<50}")

            if len(metric_deletions) > 10:
                print(f"... and {len(metric_deletions) - 10} more")

        deletion_candidates.extend([{**d, 'metric': metric} for d in metric_deletions])

    # Execute deletions
    print(f"\n{'=' * 80}")
    print(f"SUMMARY")
    print(f"{'=' * 80}\n")
    print(f"Total datapoints to delete: {len(deletion_candidates)}\n")

    if not dry_run and deletion_candidates:
        print("Deleting datapoints...")

        for deletion in deletion_candidates:
            cursor.execute('''
                DELETE FROM economic_data
                WHERE metric_name = ? AND country = ? AND time_period = ?
            ''', (deletion['metric'], deletion['country'], deletion['time_period']))
            total_deleted += 1

            if total_deleted % 50 == 0:
                print(f"  Deleted {total_deleted} records...")

        conn.commit()
        print(f"\n{'=' * 80}")
        print(f"DELETION COMPLETE")
        print(f"{'=' * 80}")
        print(f"Total records deleted: {total_deleted}")

        # Show updated database stats
        cursor.execute('SELECT COUNT(*) as total FROM economic_data')
        total_count = cursor.fetchone()['total']
        print(f"Remaining records in database: {total_count}")

    elif dry_run:
        print("DRY RUN - No changes made to database")
        print(f"Would delete {len(deletion_candidates)} records")

    conn.close()

    return total_deleted if not dry_run else len(deletion_candidates)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Filter bad data from economic database')
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
        help='Metric to filter (can be specified multiple times, default: real_gdp)'
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

    metrics = args.metrics if args.metrics else ['real_gdp']

    filter_bad_data(args.db, args.threshold, metrics, args.dry_run)
