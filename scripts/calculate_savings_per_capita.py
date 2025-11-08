#!/usr/bin/env python3
"""
Calculate Nominal Savings Per Capita

Calculates nominal savings per capita from savings rate and disposable income per capita.

Formula:
    savings_per_capita = (savings_rate / 100) * disposable_income_per_capita

This provides the actual amount saved per person in USD PPP terms.

Prerequisites:
    - savings_rate: Household net saving rate (% of disposable income)
    - disposable_income_per_capita: Household disposable income per capita

Usage:
    python calculate_savings_per_capita.py [--dry-run]
"""

import sqlite3
import argparse
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description='Calculate nominal savings per capita from savings rate and disposable income'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be calculated without writing to database'
    )
    parser.add_argument(
        '--db-path',
        default='data/economic_data.db',
        help='Path to database (default: data/economic_data.db)'
    )
    return parser.parse_args()


def calculate_savings_per_capita(conn, dry_run=False):
    """
    Calculate nominal savings per capita.

    Args:
        conn: Database connection
        dry_run: If True, only print what would be done

    Returns:
        int: Number of records calculated
    """
    cursor = conn.cursor()

    # Get savings rate and disposable income data joined by country and time period
    cursor.execute("""
        SELECT
            sr.country,
            sr.time_period,
            sr.value as savings_rate,
            di.value as disposable_income_per_capita
        FROM economic_data sr
        INNER JOIN economic_data di
            ON sr.country = di.country
            AND sr.time_period = di.time_period
        WHERE sr.metric_name = 'savings_rate'
          AND di.metric_name = 'disposable_income_per_capita'
        ORDER BY sr.country, sr.time_period
    """)

    data = cursor.fetchall()

    if not data:
        print("ERROR: No matching savings rate and disposable income data found!")
        print("\nPlease ensure both metrics are available in the database:")
        print("  - savings_rate")
        print("  - disposable_income_per_capita")
        return 0

    print(f"Found {len(data)} matching records")

    # Calculate savings per capita
    savings_records = []
    for country, time_period, savings_rate, disposable_income in data:
        # Calculate: savings = (rate / 100) * income
        savings_per_capita = (savings_rate / 100) * disposable_income
        savings_records.append((country, time_period, savings_per_capita))

    print(f"Calculated {len(savings_records)} savings per capita values")

    if dry_run:
        print("\n[DRY RUN] Would insert records but not committing")

        # Show sample data
        print("\nSample calculations (first 10):")
        print(f"{'Country':<30} {'Period':<12} {'Savings/capita':<15}")
        print("-"*80)
        for record in savings_records[:10]:
            print(f"{record[0]:<30} {record[1]:<12} ${record[2]:>12,.2f}")

        # Show some statistics
        if savings_records:
            values = [r[2] for r in savings_records]
            print(f"\nStatistics:")
            print(f"  Min: ${min(values):,.2f}")
            print(f"  Max: ${max(values):,.2f}")
            print(f"  Avg: ${sum(values)/len(values):,.2f}")

        return len(savings_records)

    # Insert into database
    timestamp = datetime.utcnow().isoformat()

    cursor.executemany("""
        INSERT INTO economic_data (country, time_period, value, metric_name, unit, source, last_updated)
        VALUES (?, ?, ?, 'savings_per_capita', 'USD_PPP', 'Calculated', ?)
        ON CONFLICT(country, time_period, metric_name)
        DO UPDATE SET
            value = excluded.value,
            last_updated = excluded.last_updated
    """, [(c, t, v, timestamp) for c, t, v in savings_records])

    print(f"✓ Inserted {len(savings_records)} savings per capita records")

    conn.commit()
    print("✓ Changes committed to database")

    return len(savings_records)


def verify_results(conn):
    """Verify the calculated metrics."""
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)

    # Check record count
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM economic_data
        WHERE metric_name = 'savings_per_capita'
    """)

    count = cursor.fetchone()[0]
    print(f"\nTotal savings_per_capita records: {count}")

    # Show sample data for USA
    print("\nSample data for United States (last 5 quarters):")
    cursor.execute("""
        SELECT time_period,
               (SELECT value FROM economic_data e2
                WHERE e2.country = e1.country
                  AND e2.time_period = e1.time_period
                  AND e2.metric_name = 'disposable_income_per_capita') as disp_income,
               (SELECT value FROM economic_data e2
                WHERE e2.country = e1.country
                  AND e2.time_period = e1.time_period
                  AND e2.metric_name = 'savings_rate') as savings_rate,
               (SELECT value FROM economic_data e2
                WHERE e2.country = e1.country
                  AND e2.time_period = e1.time_period
                  AND e2.metric_name = 'savings_per_capita') as savings_pc
        FROM economic_data e1
        WHERE e1.country = 'United States'
          AND e1.metric_name = 'disposable_income_per_capita'
        ORDER BY time_period DESC
        LIMIT 5
    """)

    print(f"\n{'Period':<12} {'Disp Income':<15} {'Savings %':<12} {'Savings/capita':<15}")
    print("-"*80)
    for row in cursor.fetchall():
        period, income, rate, savings = row
        income_str = f"${income:,.0f}" if income else "N/A"
        rate_str = f"{rate:.2f}%" if rate else "N/A"
        savings_str = f"${savings:,.0f}" if savings else "N/A"
        print(f"{period:<12} {income_str:<15} {rate_str:<12} {savings_str:<15}")

    # Show countries with data
    cursor.execute("""
        SELECT DISTINCT country
        FROM economic_data
        WHERE metric_name = 'savings_per_capita'
        ORDER BY country
    """)

    countries = [row[0] for row in cursor.fetchall()]
    print(f"\nCountries with savings per capita data ({len(countries)}):")
    for i in range(0, len(countries), 5):
        batch = countries[i:i+5]
        print("  " + ", ".join(batch))


def main():
    args = parse_args()

    print("="*80)
    print("SAVINGS PER CAPITA CALCULATION")
    print("="*80)
    print(f"\nDatabase: {args.db_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    # Connect to database
    conn = sqlite3.connect(args.db_path)

    try:
        # Calculate savings per capita
        count = calculate_savings_per_capita(conn, args.dry_run)

        if count == 0:
            print("\n⚠ No data calculated. Please fetch the required metrics first:")
            print("  python scripts/fetch_oecd_data.py savings_rate --latest 10")
            print("  python scripts/fetch_oecd_data.py disposable_income_per_capita --latest 10")
            return 1

        if not args.dry_run:
            # Verify results
            verify_results(conn)

        print("\n" + "="*80)
        print("✓ Savings per capita calculation complete!")
        print("="*80)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        conn.close()

    return 0


if __name__ == '__main__':
    exit(main())
