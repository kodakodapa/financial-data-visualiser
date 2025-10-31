#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('data/economic_data.db')
cursor = conn.cursor()

cursor.execute('SELECT country, metric_name FROM economic_data WHERE time_period = ? ORDER BY country, metric_name', ('2025-Q3',))
bad_records = cursor.fetchall()

print(f'Found {len(bad_records)} records with 2025-Q3:\n')

for country, metric in bad_records:
    cursor.execute('SELECT COUNT(*) FROM economic_data WHERE country = ? AND metric_name = ? AND time_period = ?',
                   (country, metric, '2005-Q4'))
    has_2005q4 = cursor.fetchone()[0]
    status = 'HAS 2005-Q4' if has_2005q4 else 'MISSING 2005-Q4'
    print(f'{country:<40} {metric:<35} {status}')

conn.close()
