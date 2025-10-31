#!/usr/bin/env python3
"""
Analyze GDP data completeness across countries.
Identifies countries with missing quarters and shows which quarters are missing.
"""

import csv
import sys
from collections import defaultdict
from datetime import datetime

def parse_quarter(quarter_str):
    """Parse quarter string (e.g., '1995-Q2') for sorting."""
    try:
        year, quarter = quarter_str.split('-Q')
        return (int(year), int(quarter))
    except:
        return (0, 0)

def analyze_gdp_completeness(input_file):
    """
    Analyze GDP data completeness across countries.

    Args:
        input_file: Path to the extracted GDP CSV file
    """
    # Dictionary to store quarters for each country
    country_quarters = defaultdict(set)
    all_quarters = set()

    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            # Collect all data
            for row in reader:
                country = row['Country']
                quarter = row['Quarter']

                country_quarters[country].add(quarter)
                all_quarters.add(quarter)

        # Convert all_quarters to sorted list
        all_quarters_sorted = sorted(list(all_quarters), key=parse_quarter)
        max_quarters = len(all_quarters_sorted)

        print("=" * 80)
        print("GDP DATA COMPLETENESS ANALYSIS")
        print("=" * 80)
        print(f"\nTotal unique quarters in dataset: {max_quarters}")
        print(f"Quarter range: {all_quarters_sorted[0]} to {all_quarters_sorted[-1]}")
        print(f"Total countries: {len(country_quarters)}\n")

        # Analyze each country
        countries_with_complete_data = []
        countries_with_missing_data = []

        for country in sorted(country_quarters.keys()):
            quarters_count = len(country_quarters[country])
            missing_count = max_quarters - quarters_count

            if missing_count == 0:
                countries_with_complete_data.append((country, quarters_count))
            else:
                # Find which quarters are missing
                missing_quarters = sorted(
                    [q for q in all_quarters_sorted if q not in country_quarters[country]],
                    key=parse_quarter
                )
                countries_with_missing_data.append((country, quarters_count, missing_count, missing_quarters))

        # Print summary
        print("-" * 80)
        print(f"SUMMARY")
        print("-" * 80)
        print(f"Countries with complete data ({max_quarters} quarters): {len(countries_with_complete_data)}")
        print(f"Countries with missing data: {len(countries_with_missing_data)}\n")

        # Print countries with complete data
        if countries_with_complete_data:
            print("=" * 80)
            print("COUNTRIES WITH COMPLETE DATA")
            print("=" * 80)
            for country, count in countries_with_complete_data:
                print(f"  {country}: {count} quarters")
            print()

        # Print countries with missing data
        if countries_with_missing_data:
            print("=" * 80)
            print("COUNTRIES WITH MISSING DATA")
            print("=" * 80)
            for country, present, missing, missing_quarters in countries_with_missing_data:
                print(f"\n{country}:")
                print(f"  Present: {present}/{max_quarters} quarters")
                print(f"  Missing: {missing} quarters ({missing/max_quarters*100:.1f}%)")

                # Show missing quarters (limit to first 10 if too many)
                if missing <= 20:
                    print(f"  Missing quarters: {', '.join(missing_quarters)}")
                else:
                    print(f"  Missing quarters (first 20): {', '.join(missing_quarters[:20])}")
                    print(f"  ... and {missing - 20} more")

        print("\n" + "=" * 80)

        # Additional statistics
        print("\nADDITIONAL STATISTICS")
        print("-" * 80)
        coverage_percentages = [(country, len(quarters)/max_quarters*100)
                                for country, quarters in country_quarters.items()]
        coverage_percentages.sort(key=lambda x: x[1])

        avg_coverage = sum(pct for _, pct in coverage_percentages) / len(coverage_percentages)
        print(f"Average data coverage: {avg_coverage:.1f}%")
        print(f"\nCountries with lowest coverage:")
        for country, pct in coverage_percentages[:5]:
            print(f"  {country}: {pct:.1f}%")

        print(f"\nCountries with highest coverage:")
        for country, pct in coverage_percentages[-5:]:
            print(f"  {country}: {pct:.1f}%")

    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Default file name
    input_file = "gdp-data-extracted.csv"

    # Allow command line argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    analyze_gdp_completeness(input_file)
