#!/usr/bin/env python3
"""
Fix quarter mislabeling issue where 2005-Q4 was incorrectly stored as 2025-Q3.
"""

import sqlite3

def fix_quarter_mislabeling(db_path='data/economic_data.db'):
    """
    Fix the issue where 2025-Q3 should actually be 2005-Q4 for certain countries.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find all records with 2025-Q3 that should be 2005-Q4
    cursor.execute('''
        SELECT country, metric_name, value
        FROM economic_data
        WHERE time_period = '2025-Q3'
    ''')

    records = cursor.fetchall()

    print(f"Found {len(records)} records with time_period = 2025-Q3\n")

    if not records:
        print("No records to fix!")
        conn.close()
        return

    print("Updating records:")
    print(f"{'Country':<40} {'Metric':<30} {'Value':>15}")
    print("-" * 90)

    updated_count = 0

    for country, metric_name, value in records:
        # Check if 2005-Q4 already exists
        cursor.execute('''
            SELECT COUNT(*) FROM economic_data
            WHERE country = ? AND metric_name = ? AND time_period = '2005-Q4'
        ''', (country, metric_name))

        has_2005q4 = cursor.fetchone()[0] > 0

        if has_2005q4:
            # Delete the erroneous 2025-Q3 record (duplicate)
            print(f"{country:<40} {metric_name:<30} {value:>15,.1f} [DELETE - has 2005-Q4]")
            cursor.execute('''
                DELETE FROM economic_data
                WHERE country = ? AND metric_name = ? AND time_period = '2025-Q3'
            ''', (country, metric_name))
        else:
            # Update to correct period (2005-Q4 missing)
            print(f"{country:<40} {metric_name:<30} {value:>15,.1f} [UPDATE to 2005-Q4]")
            cursor.execute('''
                UPDATE economic_data
                SET time_period = '2005-Q4'
                WHERE country = ? AND metric_name = ? AND time_period = '2025-Q3'
            ''', (country, metric_name))

        updated_count += cursor.rowcount

    conn.commit()

    print(f"\n{'=' * 90}")
    print(f"CORRECTION COMPLETE")
    print(f"{'=' * 90}")
    print(f"Updated {updated_count} records from 2025-Q3 to 2005-Q4")

    # Verify the fix
    cursor.execute("SELECT COUNT(*) FROM economic_data WHERE time_period = '2025-Q3'")
    remaining = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM economic_data WHERE time_period = '2005-Q4'")
    fixed = cursor.fetchone()[0]

    print(f"\nVerification:")
    print(f"  Records with 2025-Q3: {remaining}")
    print(f"  Records with 2005-Q4: {fixed}")

    conn.close()

if __name__ == "__main__":
    fix_quarter_mislabeling()
