#!/usr/bin/env python3
"""
Check specific quarters identified as potentially incorrect.
"""

import sqlite3

def check_quarters(country, periods, context_before=2, context_after=2):
    """Check specific quarters with context."""
    conn = sqlite3.connect('data/economic_data.db')
    cursor = conn.cursor()

    print(f"\n{'=' * 70}")
    print(f"Checking {country}")
    print(f"{'=' * 70}\n")

    for period in periods:
        year, quarter = period.split('-Q')
        year = int(year)
        quarter = int(quarter)

        # Get surrounding quarters
        cursor.execute('''
            SELECT time_period, value
            FROM economic_data
            WHERE metric_name = 'real_gdp' AND country = ?
            ORDER BY time_period
        ''', (country,))

        all_data = cursor.fetchall()

        # Find the index of our target period
        target_idx = None
        for i, (tp, val) in enumerate(all_data):
            if tp == period:
                target_idx = i
                break

        if target_idx is None:
            print(f"  {period}: NOT FOUND")
            continue

        # Show context
        start_idx = max(0, target_idx - context_before)
        end_idx = min(len(all_data), target_idx + context_after + 1)

        print(f"Context around {period}:")
        print(f"{'Period':<12} {'Value':>15} {'Change %':>12}")
        print("-" * 42)

        prev_val = None
        for i in range(start_idx, end_idx):
            tp, val = all_data[i]
            change = ""
            if prev_val is not None and prev_val > 0:
                pct = ((val - prev_val) / prev_val) * 100
                change = f"{pct:+.1f}%"

            marker = " <-- SUSPECT" if tp == period else ""
            print(f"{tp:<12} {val:>15,.0f} {change:>12}{marker}")
            prev_val = val

        print()

    conn.close()

if __name__ == "__main__":
    # Check Austria 2005-Q4
    check_quarters("Austria", ["2005-Q4"])

    # Check Poland quarters
    check_quarters("Poland", ["2010-Q2", "2013-Q2", "2014-Q4"])
