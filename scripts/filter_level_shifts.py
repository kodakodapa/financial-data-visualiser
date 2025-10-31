#!/usr/bin/env python3
"""
Filter and remove data segments with persistent level shifts.
Handles cases where entire series segments are at wrong levels (unit changes, etc.).
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

def filter_level_shifts(db_path, threshold_pct=20.0, metric='real_gdp', dry_run=False):
    """
    Identify and remove data segments with persistent level shifts.

    Strategy:
    1. Detect extreme changes that create new "levels"
    2. If a series has multiple extreme jumps/drops in the same direction,
       it likely has bad segments
    3. Keep the longest consistent segment and remove others

    Args:
        db_path: Path to the SQLite database
        threshold_pct: Percentage threshold for extreme changes
        metric: Metric to filter
        dry_run: If True, only report what would be deleted

    Returns:
        Number of datapoints removed
    """
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        return 0

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"\n{'=' * 80}")
    print(f"LEVEL SHIFT FILTER")
    print(f"{'=' * 80}")
    print(f"Metric: {metric}")
    print(f"Threshold: ±{threshold_pct}%")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")

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

    deletion_candidates = []

    for country, data_points in country_data.items():
        # Sort by time period
        data_points.sort(key=lambda x: parse_quarter(x['time_period']))

        if len(data_points) < 10:
            continue

        # Find all extreme changes
        extreme_changes = []
        for i in range(1, len(data_points)):
            prev_val = data_points[i-1]['value']
            curr_val = data_points[i]['value']

            if prev_val > 0:
                pct_change = ((curr_val - prev_val) / prev_val) * 100
                if abs(pct_change) > threshold_pct:
                    extreme_changes.append({
                        'index': i,
                        'period': data_points[i]['time_period'],
                        'pct_change': pct_change
                    })

        # If there are multiple extreme changes, analyze segments
        if len(extreme_changes) >= 2:
            # Create segments between extreme changes
            segments = []
            start_idx = 0

            for change in extreme_changes:
                if change['index'] > start_idx:
                    segment_data = data_points[start_idx:change['index']]
                    avg_value = sum(p['value'] for p in segment_data) / len(segment_data)
                    segments.append({
                        'start_idx': start_idx,
                        'end_idx': change['index'],
                        'length': len(segment_data),
                        'avg_value': avg_value,
                        'periods': [p['time_period'] for p in segment_data]
                    })
                start_idx = change['index']

            # Add final segment
            if start_idx < len(data_points):
                segment_data = data_points[start_idx:]
                avg_value = sum(p['value'] for p in segment_data) / len(segment_data)
                segments.append({
                    'start_idx': start_idx,
                    'end_idx': len(data_points),
                    'length': len(segment_data),
                    'avg_value': avg_value,
                    'periods': [p['time_period'] for p in segment_data]
                })

            # Find the dominant (longest) segment
            segments.sort(key=lambda s: s['length'], reverse=True)
            if len(segments) > 1:
                main_segment = segments[0]
                main_avg = main_segment['avg_value']

                # Mark segments that are at very different levels for deletion
                for segment in segments[1:]:
                    level_diff_pct = abs((segment['avg_value'] - main_avg) / main_avg * 100)

                    # If segment average differs by > 40% from main segment, delete it
                    if level_diff_pct > 40:
                        for period in segment['periods']:
                            deletion_candidates.append({
                                'country': country,
                                'time_period': period,
                                'reason': f'Wrong level: {level_diff_pct:.1f}% from main series'
                            })

    print(f"Found {len(deletion_candidates)} datapoints in wrong-level segments\n")

    if deletion_candidates:
        # Group by country for display
        by_country = defaultdict(list)
        for d in deletion_candidates:
            by_country[d['country']].append(d)

        print("Deletions by country:")
        print(f"{'Country':<25} {'Count':>6} {'Sample Periods':<30}")
        print("-" * 65)
        for country in sorted(by_country.keys()):
            periods = by_country[country]
            sample_periods = ', '.join([p['time_period'] for p in periods[:3]])
            if len(periods) > 3:
                sample_periods += f", ... (+{len(periods)-3} more)"
            print(f"{country:<25} {len(periods):>6} {sample_periods:<30}")

    total_deleted = 0

    if not dry_run and deletion_candidates:
        print(f"\nDeleting {len(deletion_candidates)} datapoints...")

        for deletion in deletion_candidates:
            cursor.execute('''
                DELETE FROM economic_data
                WHERE metric_name = ? AND country = ? AND time_period = ?
            ''', (metric, deletion['country'], deletion['time_period']))
            total_deleted += 1

            if total_deleted % 50 == 0:
                print(f"  Deleted {total_deleted} records...")

        conn.commit()
        print(f"\nDeletion complete: {total_deleted} records removed")

    elif dry_run:
        print(f"\nDRY RUN - Would delete {len(deletion_candidates)} records")

    conn.close()
    return total_deleted if not dry_run else len(deletion_candidates)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Filter level shifts from economic database')
    parser.add_argument(
        '--threshold',
        type=float,
        default=20.0,
        help='Percentage threshold for extreme changes (default: 20.0)'
    )
    parser.add_argument(
        '--metric',
        type=str,
        default='real_gdp',
        help='Metric to filter (default: real_gdp)'
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

    filter_level_shifts(args.db, args.threshold, args.metric, args.dry_run)
