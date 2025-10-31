#!/usr/bin/env python3
"""
Check for issues in gdp_per_capita and gdp_cumulative_return_per_capita.
"""

import sqlite3

def check_country_timeline(country, metric, context_years=1):
    """Check a country's timeline for issues."""
    conn = sqlite3.connect('data/economic_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT time_period, value
        FROM economic_data
        WHERE metric_name = ? AND country = ?
        ORDER BY time_period
    ''', (metric, country))

    data = cursor.fetchall()

    print(f"\n{'=' * 70}")
    print(f"{country} - {metric}")
    print(f"{'=' * 70}\n")

    if not data:
        print("No data found")
        return

    print(f"{'Period':<12} {'Value':>15} {'Change %':>12}")
    print("-" * 42)

    prev_val = None
    issues = []

    for i, (tp, val) in enumerate(data):
        change = ""
        if prev_val is not None and prev_val > 0:
            pct = ((val - prev_val) / prev_val) * 100
            change = f"{pct:+.1f}%"

            # Flag extreme changes
            if abs(pct) > 15:
                issues.append((i, tp, val, pct))

        print(f"{tp:<12} {val:>15,.2f} {change:>12}")
        prev_val = val

    if issues:
        print(f"\n⚠ Found {len(issues)} extreme changes (>15%):")
        for idx, tp, val, pct in issues:
            print(f"  {tp}: {pct:+.1f}%")

    conn.close()

if __name__ == "__main__":
    countries = ["Chile", "Belgium", "Canada"]

    for country in countries:
        check_country_timeline(country, "gdp_per_capita")
        check_country_timeline(country, "gdp_cumulative_return_per_capita")
