#!/usr/bin/env python3
"""
Ingest economic data from CSV files into the SQLite database.
Supports upsert operations (insert or update existing records).
"""

import sqlite3
import csv
import os
import sys
from datetime import datetime

def ingest_data(csv_file, metric_name, unit, source, db_path):
    """
    Ingest data from a CSV file into the database.

    Args:
        csv_file: Path to the CSV file (expected format: Country, Quarter, Value)
        metric_name: Name of the metric (e.g., 'gdp_per_capita')
        unit: Unit of measurement (e.g., 'USD_PPP')
        source: Data source (e.g., 'OECD')
        db_path: Path to the SQLite database
    """
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        return False

    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        print("Please run 'python scripts/init_database.py' first")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Read CSV file
        rows_processed = 0
        rows_inserted = 0
        rows_updated = 0

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Verify expected columns
            expected_columns = {'Country', 'Quarter', 'GDP_Value'}
            actual_columns = set(reader.fieldnames)

            # Try alternative column names
            if 'Country' not in actual_columns:
                print(f"Error: CSV must have 'Country' column")
                print(f"Found columns: {', '.join(actual_columns)}")
                return False

            # Detect value column name
            value_column = None
            for col in ['GDP_Value', 'Value', 'OBS_VALUE']:
                if col in actual_columns:
                    value_column = col
                    break

            if not value_column:
                print(f"Error: Could not find value column")
                print(f"Expected one of: GDP_Value, Value, OBS_VALUE")
                return False

            # Detect time period column
            time_column = None
            for col in ['Quarter', 'TIME_PERIOD', 'Time_Period']:
                if col in actual_columns:
                    time_column = col
                    break

            if not time_column:
                print(f"Error: Could not find time period column")
                print(f"Expected one of: Quarter, TIME_PERIOD, Time_Period")
                return False

            print(f"\nIngesting data from: {csv_file}")
            print(f"Metric: {metric_name}")
            print(f"Unit: {unit}")
            print(f"Source: {source}")
            print(f"Using columns: Country, {time_column}, {value_column}\n")

            # Prepare upsert statement
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

            timestamp = datetime.now().isoformat()

            for row in reader:
                country = row['Country'].strip()
                time_period = row[time_column].strip()
                value_str = row[value_column].strip()

                if not country or not time_period or not value_str:
                    continue

                try:
                    value = float(value_str)
                except ValueError:
                    print(f"Warning: Invalid value '{value_str}' for {country} {time_period}, skipping")
                    continue

                # Check if record exists
                cursor.execute(
                    'SELECT value FROM economic_data WHERE country=? AND time_period=? AND metric_name=?',
                    (country, time_period, metric_name)
                )
                existing = cursor.fetchone()

                # Execute upsert
                cursor.execute(upsert_sql, (
                    country, time_period, metric_name, value, unit, source, timestamp
                ))

                rows_processed += 1
                if existing:
                    rows_updated += 1
                else:
                    rows_inserted += 1

                # Progress indicator
                if rows_processed % 1000 == 0:
                    print(f"Processed {rows_processed} rows...")

        conn.commit()

        print("\n" + "=" * 60)
        print("INGESTION COMPLETE")
        print("=" * 60)
        print(f"Rows processed: {rows_processed}")
        print(f"Rows inserted: {rows_inserted}")
        print(f"Rows updated: {rows_updated}")

        # Show database stats
        cursor.execute("SELECT COUNT(*) FROM economic_data")
        total_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT metric_name) FROM economic_data")
        metric_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT country) FROM economic_data")
        country_count = cursor.fetchone()[0]

        print(f"\nDatabase totals:")
        print(f"  Total records: {total_count}")
        print(f"  Unique metrics: {metric_count}")
        print(f"  Unique countries: {country_count}")
        print("=" * 60)

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
        print("Usage: python ingest_data.py <csv_file> [metric_name] [unit] [source]")
        print("\nExample:")
        print("  python scripts/ingest_data.py data/processed/gdp-data-extracted.csv gdp_per_capita USD_PPP OECD")
        sys.exit(1)

    csv_file = sys.argv[1]
    metric_name = sys.argv[2] if len(sys.argv) > 2 else "gdp_per_capita"
    unit = sys.argv[3] if len(sys.argv) > 3 else "USD_PPP"
    source = sys.argv[4] if len(sys.argv) > 4 else "OECD"

    success = ingest_data(csv_file, metric_name, unit, source, db_path)
    sys.exit(0 if success else 1)
