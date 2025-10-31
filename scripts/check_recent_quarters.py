#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('data/economic_data.db')
cursor = conn.cursor()

countries = ['Chile', 'Belgium', 'Canada']

for country in countries:
    cursor.execute('''
        SELECT time_period, value
        FROM economic_data
        WHERE metric_name = 'gdp_per_capita' AND country = ?
        AND time_period >= '2024-Q1'
        ORDER BY time_period
    ''', (country,))

    print(f'\n{country} gdp_per_capita (2024+):')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]:,.2f}')

conn.close()
