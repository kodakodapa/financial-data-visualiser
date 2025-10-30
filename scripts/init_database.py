#!/usr/bin/env python3
"""
Initialize the SQLite database for economic data storage.
Creates the schema with proper indexes for efficient querying.
"""

import sqlite3
import os
import sys

def init_database(db_path):
    """
    Initialize the economic data database.

    Args:
        db_path: Path to the SQLite database file
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Check if database already exists
    db_exists = os.path.exists(db_path)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if db_exists:
            print(f"Database already exists at: {db_path}")
            print("Verifying schema...")
        else:
            print(f"Creating new database at: {db_path}")

        # Create the main economic_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS economic_data (
                country TEXT NOT NULL,
                time_period TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                source TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (country, time_period, metric_name)
            )
        ''')

        # Create indexes for efficient querying
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_country
            ON economic_data(country)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metric
            ON economic_data(metric_name)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_time
            ON economic_data(time_period)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_country_metric
            ON economic_data(country, metric_name)
        ''')

        conn.commit()

        # Verify the schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()

        print("\n" + "=" * 60)
        print("DATABASE INITIALIZED SUCCESSFULLY")
        print("=" * 60)
        print(f"\nLocation: {os.path.abspath(db_path)}")
        print(f"\nTables: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")

        print(f"\nIndexes: {len(indexes)}")
        for index in indexes:
            print(f"  - {index[0]}")

        # Show current row count
        cursor.execute("SELECT COUNT(*) FROM economic_data")
        count = cursor.fetchone()[0]
        print(f"\nCurrent records: {count}")

        if count > 0:
            # Show some stats
            cursor.execute("SELECT COUNT(DISTINCT metric_name) FROM economic_data")
            metric_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT country) FROM economic_data")
            country_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT time_period) FROM economic_data")
            period_count = cursor.fetchone()[0]

            print(f"  - Unique metrics: {metric_count}")
            print(f"  - Unique countries: {country_count}")
            print(f"  - Unique time periods: {period_count}")

        print("=" * 60)

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Default database path
    db_path = os.path.join("data", "economic_data.db")

    # Allow command line argument
    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    success = init_database(db_path)
    sys.exit(0 if success else 1)
