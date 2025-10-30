#!/usr/bin/env python3
"""
Calculate cumulative return metrics from existing time series data.
Indexes the first data point to 100 for each country and calculates subsequent values.
"""

import sqlite3
import os
import sys
from datetime import datetime
from collections import defaultdict

def parse_quarter(quarter_str):
    """Parse quarter string (e.g., '1995-Q2') for sorting."""
    try:
        year, quarter = quarter_str.split('-Q')
        return (int(year), int(quarter))
    except:
        return (0, 0)

def calculate_cumulative_return(source_metric, target_metric, db_path):
    """
    Calculate cumulative return indexed to 100 from a source metric.

    Args:
        source_metric: Name of the source metric (e.g., 'gdp_per_capita')
        target_metric: Name for the cumulative return metric (e.g., 'gdp_cumulative_return')
        db_path: Path to the SQLite database

    The calculation:
    - First value for each country = 100
    - Subsequent values = previous_indexed_value * (current_value / previous_value)
    """
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Verify source metric exists
        cursor.execute(
            'SELECT COUNT(*) as count FROM economic_data WHERE metric_name = ?',
            (source_metric,)
        )
        if cursor.fetchone()['count'] == 0:
            print(f"Error: Source metric '{source_metric}' not found in database")
            return False

        # Get all data for the source metric
        cursor.execute('''
            SELECT country, time_period, value, unit, source
            FROM economic_data
            WHERE metric_name = ?
            ORDER BY country, time_period
        ''', (source_metric,))

        # Organize data by country
        country_data = defaultdict(list)
        source_unit = None
        source_source = None

        for row in cursor.fetchall():
            country_data[row['country']].append({
                'time_period': row['time_period'],
                'value': row['value']
            })
            if source_unit is None:
                source_unit = row['unit']
                source_source = row['source']

        print(f"\n{'=' * 60}")
        print(f"CALCULATING CUMULATIVE RETURN")
        print(f"{'=' * 60}")
        print(f"Source metric: {source_metric} ({source_unit})")
        print(f"Target metric: {target_metric}")
        print(f"Countries: {len(country_data)}")
        print(f"Base index: 100\n")

        # Calculate cumulative return for each country
        cumulative_data = []
        timestamp = datetime.now().isoformat()

        for country, data_points in country_data.items():
            # Sort by time period
            data_points.sort(key=lambda x: parse_quarter(x['time_period']))

            if len(data_points) == 0:
                continue

            # First value is always 100
            base_value = data_points[0]['value']
            cumulative_value = 100.0

            for i, point in enumerate(data_points):
                if i == 0:
                    cumulative_value = 100.0
                else:
                    # Calculate return: (current / previous) * previous_cumulative
                    previous_value = data_points[i-1]['value']
                    current_value = point['value']
                    cumulative_value = cumulative_value * (current_value / previous_value)

                cumulative_data.append({
                    'country': country,
                    'time_period': point['time_period'],
                    'value': cumulative_value
                })

        print(f"Calculated {len(cumulative_data)} cumulative return data points\n")

        # Check if target metric already exists
        cursor.execute(
            'SELECT COUNT(*) as count FROM economic_data WHERE metric_name = ?',
            (target_metric,)
        )
        existing_count = cursor.fetchone()['count']

        if existing_count > 0:
            print(f"Warning: Target metric '{target_metric}' already exists ({existing_count} records)")
            response = input("Do you want to replace it? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Operation cancelled")
                return False

            # Delete existing data
            cursor.execute(
                'DELETE FROM economic_data WHERE metric_name = ?',
                (target_metric,)
            )
            print(f"Deleted {existing_count} existing records\n")

        # Insert cumulative return data
        upsert_sql = '''
            INSERT INTO economic_data
                (country, time_period, metric_name, value, unit, source, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(country, time_period, metric_name)
            DO UPDATE SET
                value = excluded.value,
                unit = excluded.unit,
                source = excluded.source,
                last_updated = excluded.last_updated
        '''

        rows_inserted = 0
        for data_point in cumulative_data:
            cursor.execute(upsert_sql, (
                data_point['country'],
                data_point['time_period'],
                target_metric,
                data_point['value'],
                'index (base=100)',
                f"Calculated from {source_metric}",
                timestamp
            ))
            rows_inserted += 1

            # Progress indicator
            if rows_inserted % 500 == 0:
                print(f"Inserted {rows_inserted} records...")

        conn.commit()

        print(f"\n{'=' * 60}")
        print(f"CALCULATION COMPLETE")
        print(f"{'=' * 60}")
        print(f"Rows inserted: {rows_inserted}")

        # Show sample data for verification
        print(f"\nSample data (first 5 records):")
        cursor.execute('''
            SELECT country, time_period, value
            FROM economic_data
            WHERE metric_name = ?
            ORDER BY country, time_period
            LIMIT 5
        ''', (target_metric,))

        for row in cursor.fetchall():
            print(f"  {row['country']}: {row['time_period']} = {row['value']:.2f}")

        # Show database stats
        cursor.execute('SELECT COUNT(*) as total FROM economic_data')
        total_count = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(DISTINCT metric_name) as count FROM economic_data')
        metric_count = cursor.fetchone()['count']

        print(f"\nDatabase totals:")
        print(f"  Total records: {total_count}")
        print(f"  Unique metrics: {metric_count}")

        # Show which countries have the new metric
        cursor.execute('''
            SELECT country, COUNT(*) as periods, MIN(value) as min_val, MAX(value) as max_val
            FROM economic_data
            WHERE metric_name = ?
            GROUP BY country
            ORDER BY country
        ''', (target_metric,))

        print(f"\nCumulative return by country:")
        for row in cursor.fetchall():
            print(f"  {row['country']}: {row['periods']} periods, "
                  f"range: {row['min_val']:.2f} - {row['max_val']:.2f}")

        print(f"{'=' * 60}")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Default values
    db_path = os.path.join("data", "economic_data.db")

    if len(sys.argv) < 2:
        print("Usage: python calculate_cumulative_return.py <source_metric> [target_metric]")
        print("\nExample:")
        print("  python scripts/calculate_cumulative_return.py gdp_per_capita gdp_cumulative_return")
        print("\nAvailable metrics in database:")

        # Show available metrics
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT metric_name FROM economic_data ORDER BY metric_name')
            for row in cursor.fetchall():
                print(f"  - {row[0]}")
            conn.close()

        sys.exit(1)

    source_metric = sys.argv[1]
    target_metric = sys.argv[2] if len(sys.argv) > 2 else f"{source_metric}_cumulative_return"

    success = calculate_cumulative_return(source_metric, target_metric, db_path)
    sys.exit(0 if success else 1)
