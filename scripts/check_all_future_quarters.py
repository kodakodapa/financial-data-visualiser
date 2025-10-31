#!/usr/bin/env python3
"""
Check for any suspiciously future-dated quarters.
"""

import sqlite3

conn = sqlite3.connect('data/economic_data.db')
cursor = conn.cursor()

# Check for any quarters beyond 2025-Q2 or Q3
cursor.execute('''
    SELECT DISTINCT time_period
    FROM economic_data
    ORDER BY time_period DESC
    LIMIT 10
''')

print("Most recent quarters in database:\n")
for row in cursor.fetchall():
    print(f"  {row[0]}")

# Check specifically for 2025-Q4, 2026, etc.
cursor.execute('''
    SELECT country, metric_name, time_period, value
    FROM economic_data
    WHERE time_period >= '2025-Q3'
    ORDER BY time_period, country
''')

future_records = cursor.fetchall()

if future_records:
    print(f"\n{'=' * 70}")
    print(f"Records with time_period >= 2025-Q3:")
    print(f"{'=' * 70}\n")
    print(f"{'Country':<30} {'Metric':<25} {'Period':<10} {'Value':>15}")
    print("-" * 85)

    for country, metric, period, value in future_records:
        print(f"{country:<30} {metric:<25} {period:<10} {value:>15,.1f}")
else:
    print("\nNo records found with time_period >= 2025-Q3")

conn.close()
