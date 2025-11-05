#!/usr/bin/env python3
"""
Calculate Productivity Growth Metrics

Calculates quarterly productivity growth (both nominal and percentage) from GDP per capita data.
Productivity growth = Change in GDP per capita from quarter to quarter.

This provides:
1. productivity_growth: Nominal change in USD PPP (Q_t - Q_{t-1})
2. productivity_growth_pct: Percentage change ((Q_t - Q_{t-1}) / Q_{t-1} * 100)

Usage:
    python calculate_productivity_growth.py [--dry-run]
"""

import sqlite3
import argparse
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description='Calculate productivity growth metrics from GDP per capita'
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


def calculate_productivity_growth(conn, dry_run=False):
    """
    Calculate productivity growth metrics.

    Args:
        conn: Database connection
        dry_run: If True, only print what would be done

    Returns:
        tuple: (nominal_records, pct_records) number of records calculated
    """
    cursor = conn.cursor()

    # Get all GDP per capita data, sorted by country and time
    cursor.execute("""
        SELECT country, time_period, value
        FROM economic_data
        WHERE metric_name = 'gdp_per_capita'
        ORDER BY country, time_period
    """)

    gdp_data = cursor.fetchall()

    if not gdp_data:
        print("ERROR: No GDP per capita data found!")
        return 0, 0

    print(f"Found {len(gdp_data)} GDP per capita records")

    # Calculate growth by country
    nominal_growth = []
    pct_growth = []

    current_country = None
    previous_value = None
    previous_period = None

    for country, time_period, value in gdp_data:
        if country != current_country:
            # New country - reset
            current_country = country
            previous_value = value
            previous_period = time_period
            continue

        # Calculate growth
        nominal_change = value - previous_value
        pct_change = (nominal_change / previous_value) * 100 if previous_value != 0 else 0

        nominal_growth.append((country, time_period, nominal_change))
        pct_growth.append((country, time_period, pct_change))

        previous_value = value
        previous_period = time_period

    print(f"\nCalculated growth for:")
    print(f"  - {len(nominal_growth)} nominal growth records")
    print(f"  - {len(pct_growth)} percentage growth records")

    if dry_run:
        print("\n[DRY RUN] Would insert records but not committing")

        # Show sample data
        print("\nSample nominal growth (first 5):")
        for record in nominal_growth[:5]:
            print(f"  {record[0]:<30} {record[1]:<15} {record[2]:>12.2f} USD PPP")

        print("\nSample percentage growth (first 5):")
        for record in pct_growth[:5]:
            print(f"  {record[0]:<30} {record[1]:<15} {record[2]:>12.4f}%")

        return len(nominal_growth), len(pct_growth)

    # Insert nominal growth
    timestamp = datetime.utcnow().isoformat()

    cursor.executemany("""
        INSERT INTO economic_data (country, time_period, value, metric_name, unit, source, last_updated)
        VALUES (?, ?, ?, 'productivity_growth', 'USD_PPP', 'Calculated', ?)
        ON CONFLICT(country, time_period, metric_name)
        DO UPDATE SET
            value = excluded.value,
            last_updated = excluded.last_updated
    """, [(c, t, v, timestamp) for c, t, v in nominal_growth])

    print(f"✓ Inserted {len(nominal_growth)} nominal growth records")

    # Insert percentage growth
    cursor.executemany("""
        INSERT INTO economic_data (country, time_period, value, metric_name, unit, source, last_updated)
        VALUES (?, ?, ?, 'productivity_growth_pct', 'percent', 'Calculated', ?)
        ON CONFLICT(country, time_period, metric_name)
        DO UPDATE SET
            value = excluded.value,
            last_updated = excluded.last_updated
    """, [(c, t, v, timestamp) for c, t, v in pct_growth])

    print(f"✓ Inserted {len(pct_growth)} percentage growth records")

    conn.commit()
    print("\n✓ Changes committed to database")

    return len(nominal_growth), len(pct_growth)


def verify_results(conn):
    """Verify the calculated metrics."""
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)

    # Check record counts
    cursor.execute("""
        SELECT metric_name, COUNT(*) as count
        FROM economic_data
        WHERE metric_name IN ('productivity_growth', 'productivity_growth_pct')
        GROUP BY metric_name
        ORDER BY metric_name
    """)

    print("\nRecord counts:")
    for metric, count in cursor.fetchall():
        print(f"  {metric:<35} {count:>6} records")

    # Show sample data for USA
    print("\nSample data for United States (last 5 quarters):")
    cursor.execute("""
        SELECT time_period,
               (SELECT value FROM economic_data e2
                WHERE e2.country = e1.country
                  AND e2.time_period = e1.time_period
                  AND e2.metric_name = 'gdp_per_capita') as gdp_pc,
               (SELECT value FROM economic_data e2
                WHERE e2.country = e1.country
                  AND e2.time_period = e1.time_period
                  AND e2.metric_name = 'productivity_growth') as nom_growth,
               (SELECT value FROM economic_data e2
                WHERE e2.country = e1.country
                  AND e2.time_period = e1.time_period
                  AND e2.metric_name = 'productivity_growth_pct') as pct_growth
        FROM economic_data e1
        WHERE e1.country = 'United States'
          AND e1.metric_name = 'gdp_per_capita'
        ORDER BY time_period DESC
        LIMIT 5
    """)

    print(f"\n{'Period':<12} {'GDP/capita':<15} {'Growth (nom)':<15} {'Growth (%)':<12}")
    print("-"*80)
    for row in cursor.fetchall():
        period, gdp, nom, pct = row
        gdp_str = f"${gdp:,.0f}" if gdp else "N/A"
        nom_str = f"${nom:,.0f}" if nom else "N/A"
        pct_str = f"{pct:.2f}%" if pct else "N/A"
        print(f"{period:<12} {gdp_str:<15} {nom_str:<15} {pct_str:<12}")


def main():
    args = parse_args()

    print("="*80)
    print("PRODUCTIVITY GROWTH CALCULATION")
    print("="*80)
    print(f"\nDatabase: {args.db_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    # Connect to database
    conn = sqlite3.connect(args.db_path)

    try:
        # Calculate growth metrics
        nominal_count, pct_count = calculate_productivity_growth(conn, args.dry_run)

        if not args.dry_run:
            # Verify results
            verify_results(conn)

        print("\n" + "="*80)
        print("✓ Productivity growth calculation complete!")
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
