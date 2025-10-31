"""
Calculate GDP level from GDP per capita and population data.
GDP Level = GDP per capita * Population
"""

import sqlite3
from datetime import datetime

def calculate_gdp_level():
    conn = sqlite3.connect('data/economic_data.db')
    cursor = conn.cursor()

    # Get all GDP per capita and population data
    # GDP data is quarterly (e.g., 2024-Q1), population data is annual (e.g., 2024)
    # We match by extracting the year from the quarter
    cursor.execute("""
        SELECT
            gdp.country,
            gdp.time_period,
            gdp.value as gdp_per_capita,
            pop.value as population
        FROM economic_data gdp
        JOIN economic_data pop
            ON gdp.country = pop.country
            AND substr(gdp.time_period, 1, 4) = pop.time_period
        WHERE gdp.metric_name = 'gdp_per_capita'
            AND pop.metric_name = 'population'
            AND gdp.value IS NOT NULL
            AND pop.value IS NOT NULL
    """)

    rows = cursor.fetchall()
    print(f"Found {len(rows)} matching records to calculate GDP level from")

    # Calculate GDP level and prepare for insertion
    gdp_level_records = []
    for country, time_period, gdp_per_capita, population in rows:
        # GDP level = GDP per capita * Population
        # Population is typically in thousands or millions, need to check units
        gdp_level = gdp_per_capita * population
        gdp_level_records.append((country, time_period, gdp_level))

    # First, delete any existing GDP level data to avoid duplicates
    cursor.execute("DELETE FROM economic_data WHERE metric_name = 'gdp_level'")
    deleted_count = cursor.rowcount
    print(f"Deleted {deleted_count} existing GDP level records")

    # Insert new GDP level data
    cursor.executemany("""
        INSERT INTO economic_data
        (country, time_period, metric_name, value, unit, source, last_updated)
        VALUES (?, ?, 'gdp_level', ?, 'USD', 'Calculated from OECD data', ?)
    """, [(country, time_period, gdp_level, datetime.now())
          for country, time_period, gdp_level in gdp_level_records])

    conn.commit()
    print(f"Inserted {len(gdp_level_records)} GDP level records")

    # Show sample data
    cursor.execute("""
        SELECT country, time_period, value
        FROM economic_data
        WHERE metric_name = 'gdp_level'
        ORDER BY country, time_period
        LIMIT 10
    """)

    print("\nSample GDP level data:")
    for row in cursor.fetchall():
        print(f"  {row[0]:20s} {row[1]:10s} {row[2]:20,.2f}")

    # Show statistics
    cursor.execute("""
        SELECT
            COUNT(*) as record_count,
            COUNT(DISTINCT country) as country_count,
            MIN(value) as min_gdp,
            MAX(value) as max_gdp,
            AVG(value) as avg_gdp
        FROM economic_data
        WHERE metric_name = 'gdp_level'
    """)

    stats = cursor.fetchone()
    print(f"\nStatistics:")
    print(f"  Total records: {stats[0]}")
    print(f"  Countries: {stats[1]}")
    if stats[2] is not None:
        print(f"  Min GDP: {stats[2]:,.2f}")
        print(f"  Max GDP: {stats[3]:,.2f}")
        print(f"  Avg GDP: {stats[4]:,.2f}")

    conn.close()

if __name__ == '__main__':
    calculate_gdp_level()
