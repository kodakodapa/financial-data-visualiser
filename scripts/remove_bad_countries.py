#!/usr/bin/env python3
"""
Remove real_gdp data for countries with persistent data quality issues.
"""

import sqlite3

# Countries with systematic data quality issues in real_gdp
BAD_COUNTRIES = [
    'Colombia',
    'Greece',
    'South Africa',
    'Romania',
    'Luxembourg',
    'Saudi Arabia',
    'Ireland'
]

conn = sqlite3.connect('data/economic_data.db')
cursor = conn.cursor()

total_deleted = 0

print("Deleting real_gdp data for countries with quality issues:\n")

for country in BAD_COUNTRIES:
    cursor.execute(
        'DELETE FROM economic_data WHERE metric_name = ? AND country = ?',
        ('real_gdp', country)
    )
    deleted = cursor.rowcount
    total_deleted += deleted
    print(f"  {country}: {deleted} records deleted")

conn.commit()
conn.close()

print(f"\nTotal records deleted: {total_deleted}")
