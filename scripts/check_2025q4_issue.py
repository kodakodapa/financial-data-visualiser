#!/usr/bin/env python3
"""
Check for 2025-Q4 mislabeling issues.
"""

import sqlite3

conn = sqlite3.connect('data/economic_data.db')
cursor = conn.cursor()

# Find all records with 2025-Q4
cursor.execute('''
    SELECT country, metric_name, value
    FROM economic_data
    WHERE time_period = '2025-Q4'
    ORDER BY country, metric_name
''')

records_2025q4 = cursor.fetchall()

print(f"Found {len(records_2025q4)} records with time_period = 2025-Q4\n")

if records_2025q4:
    print("Records with 2025-Q4:")
    print(f"{'Country':<40} {'Metric':<35} {'Value':>15}")
    print("-" * 95)

    for country, metric, value in records_2025q4:
        # Check if this country has 2005-Q4
        cursor.execute('''
            SELECT COUNT(*) FROM economic_data
            WHERE country = ? AND metric_name = ? AND time_period = '2005-Q4'
        ''', (country, metric))
        has_2005q4 = cursor.fetchone()[0] > 0
        status = ' [has 2005-Q4]' if has_2005q4 else ' [MISSING 2005-Q4]'

        print(f"{country:<40} {metric:<35} {value:>15,.1f}{status}")

# Check Sweden specifically around 2005-Q4
print("\n" + "=" * 70)
print("Sweden timeline around 2005-Q4:")
print("=" * 70 + "\n")

cursor.execute('''
    SELECT time_period, value
    FROM economic_data
    WHERE metric_name = 'real_gdp' AND country = 'Sweden'
    AND time_period >= '2005-Q1' AND time_period <= '2006-Q2'
    ORDER BY time_period
''')

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
