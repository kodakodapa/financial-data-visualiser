#!/usr/bin/env python3
"""
Extract meaningful GDP data from OECD CSV file.
Extracts: Country, Time Period, and GDP Value
"""

import csv
import sys

def extract_gdp_data(input_file, output_file):
    """
    Extract country, time period, and GDP value from OECD GDP CSV.

    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file
    """
    rows_processed = 0
    rows_extracted = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:

            reader = csv.DictReader(infile)
            writer = csv.writer(outfile)

            # Write header
            writer.writerow(['Country', 'Quarter', 'GDP_Value'])

            # Process each row
            for row in reader:
                rows_processed += 1

                # Extract the meaningful fields
                country = row.get('Reference area', '').strip()
                time_period = row.get('TIME_PERIOD', '').strip()
                gdp_value = row.get('OBS_VALUE', '').strip()

                # Only write rows that have all three values
                if country and time_period and gdp_value:
                    writer.writerow([country, time_period, gdp_value])
                    rows_extracted += 1

                # Progress indicator for large files
                if rows_processed % 10000 == 0:
                    print(f"Processed {rows_processed} rows, extracted {rows_extracted} data points...")

        print(f"\nExtraction complete!")
        print(f"Total rows processed: {rows_processed}")
        print(f"Total data points extracted: {rows_extracted}")
        print(f"Output saved to: {output_file}")

    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Default file names
    input_file = "gdp-data.csv"
    output_file = "gdp-data-extracted.csv"

    # Allow command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    print(f"Extracting GDP data from: {input_file}")
    print(f"Output will be saved to: {output_file}\n")

    extract_gdp_data(input_file, output_file)
