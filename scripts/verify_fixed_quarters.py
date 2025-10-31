#!/usr/bin/env python3
"""
Verify the fixed quarters show smooth progression.
"""

import sqlite3

def verify_quarters(country, start_period, end_period):
    """Verify quarters around the fixed areas."""
    conn = sqlite3.connect('data/economic_data.db')
    cursor = conn.cursor()

    print(f"\n{'=' * 70}")
    print(f"{country} - {start_period} to {end_period}")
    print(f"{'=' * 70}\n")

    cursor.execute('''
        SELECT time_period, value
        FROM economic_data
        WHERE metric_name = 'real_gdp' AND country = ?
        AND time_period >= ? AND time_period <= ?
        ORDER BY time_period
    ''', (country, start_period, end_period))

    print(f"{'Period':<12} {'Value':>15} {'Change %':>12}")
    print("-" * 42)

    prev_val = None
    for row in cursor.fetchall():
        tp, val = row
        change = ""
        if prev_val is not None and prev_val > 0:
            pct = ((val - prev_val) / prev_val) * 100
            change = f"{pct:+.1f}%"

        print(f"{tp:<12} {val:>15,.0f} {change:>12}")
        prev_val = val

    conn.close()

if __name__ == "__main__":
    verify_quarters("Austria", "2005-Q1", "2006-Q2")
    verify_quarters("Poland", "2009-Q4", "2011-Q1")
    verify_quarters("Poland", "2012-Q4", "2014-Q1")
    verify_quarters("Poland", "2014-Q2", "2015-Q3")
