"""
Verify that GDP level calculations are correct.
"""

import sqlite3

def verify_gdp_level():
    conn = sqlite3.connect('data/economic_data.db')
    cursor = conn.cursor()

    # Get sample data to verify calculations
    cursor.execute("""
        SELECT
            gdp.country,
            gdp.time_period,
            gdp.value as gdp_per_capita,
            pop.value as population,
            level.value as gdp_level
        FROM economic_data gdp
        JOIN economic_data pop
            ON gdp.country = pop.country
            AND substr(gdp.time_period, 1, 4) = pop.time_period
        JOIN economic_data level
            ON gdp.country = level.country
            AND gdp.time_period = level.time_period
        WHERE gdp.metric_name = 'gdp_per_capita'
            AND pop.metric_name = 'population'
            AND level.metric_name = 'gdp_level'
        ORDER BY gdp.country, gdp.time_period
        LIMIT 10
    """)

    print("Verification: GDP Per Capita * Population = GDP Level")
    print(f"{'Country':<20} {'Period':<10} {'Per Capita':>15} {'Population':>15} {'GDP Level':>20} {'Calculated':>20} {'Match'}")
    print("-" * 120)

    all_match = True
    for row in cursor.fetchall():
        country, period, per_capita, population, gdp_level = row
        calculated = per_capita * population
        match = abs(calculated - gdp_level) / gdp_level < 0.0001 if gdp_level else False
        match_str = "OK" if match else "MISMATCH"
        if not match:
            all_match = False

        print(f"{country:<20} {period:<10} {per_capita:15,.2f} {population:15,.0f} {gdp_level:20,.2f} {calculated:20,.2f} {match_str}")

    if all_match:
        print("\nAll calculations verified successfully!")
    else:
        print("\nWARNING: Some calculations don't match!")

    # Show metrics summary
    cursor.execute("""
        SELECT metric_name, COUNT(*) as count, COUNT(DISTINCT country) as countries
        FROM economic_data
        GROUP BY metric_name
        ORDER BY metric_name
    """)

    print("\nMetrics summary:")
    for row in cursor.fetchall():
        print(f"  {row[0]:<40} Records: {row[1]:6d}  Countries: {row[2]:3d}")

    conn.close()

if __name__ == '__main__':
    verify_gdp_level()
