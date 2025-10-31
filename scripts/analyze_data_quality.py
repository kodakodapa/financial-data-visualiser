#!/usr/bin/env python3
"""
Analyze data quality by detecting extreme quarter-over-quarter changes.
Identifies potential data errors in GDP metrics.
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

def analyze_data_quality(db_path, threshold_pct=20.0):
    """
    Analyze data quality by detecting extreme quarter-over-quarter changes.

    Args:
        db_path: Path to the SQLite database
        threshold_pct: Percentage threshold for flagging extreme changes (default 20%)

    Returns:
        Dictionary with analysis results
    """
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        return None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Analyze base metrics only (not cumulative returns)
    base_metrics = ['gdp_per_capita', 'real_gdp']

    print(f"\n{'=' * 80}")
    print(f"DATA QUALITY ANALYSIS")
    print(f"{'=' * 80}")
    print(f"Threshold for extreme changes: ±{threshold_pct}% quarter-over-quarter\n")

    all_extreme_changes = []

    for metric in base_metrics:
        print(f"\n{'=' * 80}")
        print(f"Analyzing: {metric}")
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

        extreme_changes = []

        for country, data_points in country_data.items():
            # Sort by time period
            data_points.sort(key=lambda x: parse_quarter(x['time_period']))

            # Check quarter-over-quarter changes
            for i in range(1, len(data_points)):
                prev_point = data_points[i-1]
                curr_point = data_points[i]

                prev_val = prev_point['value']
                curr_val = curr_point['value']

                if prev_val > 0:  # Avoid division by zero
                    pct_change = ((curr_val - prev_val) / prev_val) * 100

                    if abs(pct_change) > threshold_pct:
                        extreme_changes.append({
                            'metric': metric,
                            'country': country,
                            'from_period': prev_point['time_period'],
                            'to_period': curr_point['time_period'],
                            'from_value': prev_val,
                            'to_value': curr_val,
                            'pct_change': pct_change
                        })

        # Sort by absolute percentage change
        extreme_changes.sort(key=lambda x: abs(x['pct_change']), reverse=True)

        print(f"Found {len(extreme_changes)} extreme changes (>{threshold_pct}%)\n")

        if extreme_changes:
            print("Top 20 most extreme changes:")
            print(f"{'Country':<25} {'From':<10} {'To':<10} {'From Value':>15} {'To Value':>15} {'Change %':>12}")
            print("-" * 100)

            for change in extreme_changes[:20]:
                print(f"{change['country']:<25} "
                      f"{change['from_period']:<10} "
                      f"{change['to_period']:<10} "
                      f"{change['from_value']:>15,.1f} "
                      f"{change['to_value']:>15,.1f} "
                      f"{change['pct_change']:>11.1f}%")

        all_extreme_changes.extend(extreme_changes)

    # Summary statistics
    print(f"\n{'=' * 80}")
    print(f"SUMMARY")
    print(f"{'=' * 80}\n")

    print(f"Total extreme changes detected: {len(all_extreme_changes)}")

    # Count by country
    country_counts = defaultdict(int)
    for change in all_extreme_changes:
        country_counts[change['country']] += 1

    print(f"\nCountries with most extreme changes:")
    sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    for country, count in sorted_countries[:10]:
        print(f"  {country}: {count} extreme changes")

    # Count by magnitude
    extreme_50 = sum(1 for c in all_extreme_changes if abs(c['pct_change']) > 50)
    extreme_100 = sum(1 for c in all_extreme_changes if abs(c['pct_change']) > 100)

    print(f"\nBy magnitude:")
    print(f"  Changes > 50%: {extreme_50}")
    print(f"  Changes > 100%: {extreme_100}")

    conn.close()

    return {
        'extreme_changes': all_extreme_changes,
        'threshold': threshold_pct,
        'total_count': len(all_extreme_changes)
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Analyze data quality in economic database')
    parser.add_argument(
        '--threshold',
        type=float,
        default=20.0,
        help='Percentage threshold for flagging extreme changes (default: 20.0)'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='data/economic_data.db',
        help='Path to database (default: data/economic_data.db)'
    )

    args = parser.parse_args()

    analyze_data_quality(args.db, args.threshold)
