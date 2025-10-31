"""
Verify that cumulative return calculations for GDP level are correct.
"""

import sqlite3

def verify_cumulative_return():
    conn = sqlite3.connect('data/economic_data.db')
    cursor = conn.cursor()

    # Get sample data to verify calculations
    cursor.execute("""
        SELECT country, time_period, value
        FROM economic_data
        WHERE metric_name = 'gdp_cumulative_return_level'
        AND country = 'Australia'
        ORDER BY time_period
        LIMIT 10
    """)

    print("Sample Cumulative Return Index for Australia (GDP Level):")
    print(f"{'Period':<12} {'Index Value':>15} {'Change %':>12}")
    print("-" * 42)

    prev_value = None
    for row in cursor.fetchall():
        period, value = row[1], row[2]
        if prev_value is not None:
            change_pct = ((value / prev_value) - 1) * 100
            print(f"{period:<12} {value:15.2f} {change_pct:11.2f}%")
        else:
            print(f"{period:<12} {value:15.2f} {'(base)':>12}")
        prev_value = value

    # Verify the calculation is correct by comparing with source data
    cursor.execute("""
        SELECT
            gdp.time_period,
            gdp.value as gdp_level,
            cum.value as cumulative_return
        FROM economic_data gdp
        JOIN economic_data cum
            ON gdp.country = cum.country
            AND gdp.time_period = cum.time_period
        WHERE gdp.metric_name = 'gdp_level'
            AND cum.metric_name = 'gdp_cumulative_return_level'
            AND gdp.country = 'United States'
        ORDER BY gdp.time_period
        LIMIT 5
    """)

    print("\n\nVerification: Calculate cumulative return manually for United States")
    print(f"{'Period':<12} {'GDP Level':>20} {'Cumulative Index':>20} {'Calculated Index':>20} {'Match'}")
    print("-" * 82)

    rows = cursor.fetchall()
    first_gdp = rows[0][1]
    calculated_index = 100.0

    for i, row in enumerate(rows):
        period, gdp_level, cumulative_return = row

        if i == 0:
            calculated_index = 100.0
        else:
            # Calculate: previous_index * (current_gdp / previous_gdp)
            previous_gdp = rows[i-1][1]
            calculated_index = calculated_index * (gdp_level / previous_gdp)

        match = abs(calculated_index - cumulative_return) < 0.01
        match_str = "OK" if match else "MISMATCH"

        print(f"{period:<12} {gdp_level:20,.2f} {cumulative_return:20.2f} {calculated_index:20.2f} {match_str}")

    # Show all available metrics
    cursor.execute("""
        SELECT metric_name, COUNT(*) as count, COUNT(DISTINCT country) as countries
        FROM economic_data
        GROUP BY metric_name
        ORDER BY metric_name
    """)

    print("\n\nAll Available Metrics:")
    print(f"{'Metric Name':<45} {'Records':>10} {'Countries':>12}")
    print("-" * 70)
    for row in cursor.fetchall():
        print(f"{row[0]:<45} {row[1]:10d} {row[2]:12d}")

    conn.close()

if __name__ == '__main__':
    verify_cumulative_return()
