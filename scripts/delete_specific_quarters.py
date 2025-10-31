#!/usr/bin/env python3
"""
Delete specific quarters identified as incorrect.
"""

import sqlite3

def delete_quarters(bad_points):
    """Delete specific quarter datapoints."""
    conn = sqlite3.connect('data/economic_data.db')
    cursor = conn.cursor()

    print(f"\n{'=' * 70}")
    print(f"DELETING SPECIFIC BAD QUARTERS")
    print(f"{'=' * 70}\n")

    deleted_total = 0

    for country, period in bad_points:
        cursor.execute('''
            DELETE FROM economic_data
            WHERE country = ? AND time_period = ?
        ''', (country, period))

        deleted = cursor.rowcount
        deleted_total += deleted
        print(f"Deleted {country} {period}: {deleted} records")

    conn.commit()

    print(f"\n{'=' * 70}")
    print(f"Total records deleted: {deleted_total}")
    print(f"{'=' * 70}")

    conn.close()

    return deleted_total

if __name__ == "__main__":
    bad_points = [
        ('Austria', '2005-Q4'),
        ('Poland', '2010-Q2'),
        ('Poland', '2013-Q2'),
        ('Poland', '2014-Q4'),
    ]

    delete_quarters(bad_points)
