#!/usr/bin/env python3
"""
Check which countries have missing quarters compared to the complete timeline.
"""

import sqlite3
from collections import defaultdict

def parse_quarter(quarter_str):
    """Parse quarter string for sorting."""
    try:
        year, quarter = quarter_str.split('-Q')
        return (int(year), int(quarter))
    except:
        return (0, 0)

conn = sqlite3.connect('data/economic_data.db')
cursor = conn.cursor()

metrics = ['gdp_per_capita', 'real_gdp']

for metric in metrics:
    print(f"\n{'=' * 80}")
    print(f"Checking: {metric}")
    print(f"{'=' * 80}\n")

    # Get all countries and their data
    cursor.execute('''
        SELECT country, time_period
        FROM economic_data
        WHERE metric_name = ?
        ORDER BY country, time_period
    ''', (metric,))

    country_periods = defaultdict(set)
    all_periods = set()

    for country, period in cursor.fetchall():
        country_periods[country].add(period)
        all_periods.add(period)

    # Sort periods
    sorted_periods = sorted(list(all_periods), key=parse_quarter)
    min_period = sorted_periods[0]
    max_period = sorted_periods[-1]

    print(f"Timeline: {min_period} to {max_period}")
    print(f"Total possible quarters: {len(sorted_periods)}")
    print(f"\nCountries with missing quarters:\n")

    print(f"{'Country':<40} {'Count':>6} {'Missing':>8} {'Missing Quarters'}")
    print("-" * 100)

    countries_with_gaps = []

    for country in sorted(country_periods.keys()):
        periods = country_periods[country]
        count = len(periods)
        missing_count = len(all_periods) - count

        if missing_count > 0:
            # Find which quarters are missing
            missing = sorted(list(all_periods - periods), key=parse_quarter)
            missing_str = ', '.join(missing[:5])
            if len(missing) > 5:
                missing_str += f' (+{len(missing)-5} more)'

            print(f"{country:<40} {count:>6} {missing_count:>8} {missing_str}")
            countries_with_gaps.append((country, missing_count, missing))

    if not countries_with_gaps:
        print("  (All countries have complete data)")

    print(f"\nSummary: {len(countries_with_gaps)} countries have missing quarters")

conn.close()
