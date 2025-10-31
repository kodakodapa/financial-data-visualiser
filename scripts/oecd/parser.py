"""
OECD Data Parser

Parses OECD CSV responses into structured data for database insertion.
"""

import csv
import io
import logging
from .data_configs import get_config, COUNTRY_NAMES

logger = logging.getLogger(__name__)


class OECDDataParser:
    """Parse OECD API responses."""

    def __init__(self):
        pass

    def parse_csv(self, csv_text, config_name, filter_status=True, allowed_statuses=None):
        """
        Parse OECD CSV response into structured data.

        Args:
            csv_text: CSV text from OECD API
            config_name: Name of the data configuration
            filter_status: If True, filter by observation status (default: True)
            allowed_statuses: List of allowed status codes (default: ['A', 'E'])
                            A = Normal value, E = Estimated value
                            P = Provisional, F = Forecast (excluded by default)

        Returns:
            list: List of dicts with keys: country, time_period, value

        Raises:
            ValueError: If CSV parsing fails or required columns missing
        """
        config = get_config(config_name)

        # Default allowed statuses if not specified
        if filter_status and allowed_statuses is None:
            allowed_statuses = ['A', 'E']  # Normal and Estimated only

        # Column names from config
        country_col = config['country_column']
        time_col = config['time_column']
        value_col = config['value_column']

        logger.info(f"Parsing CSV with columns: {country_col}, {time_col}, {value_col}")
        if filter_status:
            logger.info(f"Filtering by status: allowing {allowed_statuses}")

        try:
            # Parse CSV
            csv_file = io.StringIO(csv_text)
            reader = csv.DictReader(csv_file)

            # Verify required columns exist
            if not reader.fieldnames:
                raise ValueError("CSV has no header row")

            missing_cols = []
            for col in [country_col, time_col, value_col]:
                if col not in reader.fieldnames:
                    missing_cols.append(col)

            if missing_cols:
                available = ', '.join(reader.fieldnames[:10])
                raise ValueError(
                    f"Missing required columns: {missing_cols}. "
                    f"Available columns: {available}..."
                )

            # Parse rows
            data_points = []
            rows_parsed = 0
            rows_skipped = 0
            rows_filtered_by_status = 0
            status_counts = {}

            for row in reader:
                rows_parsed += 1

                # Extract values
                country_raw = row.get(country_col, '').strip()
                time_period = row.get(time_col, '').strip()
                value_str = row.get(value_col, '').strip()
                obs_status = row.get('OBS_STATUS', '').strip()

                # Track status counts
                status_counts[obs_status] = status_counts.get(obs_status, 0) + 1

                # Skip if any required field is missing
                if not country_raw or not time_period or not value_str:
                    rows_skipped += 1
                    continue

                # Filter by observation status if enabled
                if filter_status and obs_status not in allowed_statuses:
                    rows_filtered_by_status += 1
                    continue

                # Parse value
                try:
                    value = float(value_str)
                except ValueError:
                    logger.warning(f"Invalid value '{value_str}' for {country_raw} {time_period}, skipping")
                    rows_skipped += 1
                    continue

                # Map country name to standard name if available
                country = self._standardize_country_name(country_raw)

                data_points.append({
                    'country': country,
                    'time_period': time_period,
                    'value': value,
                    'status': obs_status
                })

            # Log parsing results
            logger.info(
                f"Parsed {len(data_points)} data points "
                f"(processed {rows_parsed} rows, skipped {rows_skipped}, "
                f"filtered by status {rows_filtered_by_status})"
            )

            # Log status breakdown
            if filter_status and status_counts:
                logger.info("Observation status breakdown:")
                status_names = {
                    'A': 'Normal',
                    'E': 'Estimated',
                    'P': 'Provisional',
                    'F': 'Forecast',
                    'M': 'Missing'
                }
                for status in sorted(status_counts.keys()):
                    count = status_counts[status]
                    name = status_names.get(status, 'Unknown')
                    kept = 'KEPT' if status in allowed_statuses else 'FILTERED'
                    logger.info(f"  {status or '(none)'} ({name}): {count} [{kept}]")

            return data_points

        except csv.Error as e:
            raise ValueError(f"CSV parsing error: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error parsing CSV: {e}")

    def _standardize_country_name(self, country_raw):
        """
        Standardize country names to match database format.

        Args:
            country_raw: Raw country name from OECD

        Returns:
            str: Standardized country name
        """
        # OECD often returns full names, but we want consistent naming
        # Try to find a match in our country names mapping
        country_raw_clean = country_raw.strip()

        # Direct match in our mapping
        for code, name in COUNTRY_NAMES.items():
            if country_raw_clean == name:
                return name
            if country_raw_clean == code:
                return name

        # If no match, return as-is
        return country_raw_clean

    def validate_data(self, data_points, min_points=1):
        """
        Validate parsed data.

        Args:
            data_points: List of data point dicts
            min_points: Minimum number of points required (default: 1)

        Returns:
            bool: True if validation passes

        Raises:
            ValueError: If validation fails
        """
        if not data_points:
            raise ValueError("No data points found")

        if len(data_points) < min_points:
            raise ValueError(f"Too few data points: {len(data_points)} < {min_points}")

        # Check all points have required fields
        for i, point in enumerate(data_points):
            if not all(key in point for key in ['country', 'time_period', 'value']):
                raise ValueError(f"Data point {i} missing required fields: {point}")

            if not isinstance(point['value'], (int, float)):
                raise ValueError(f"Data point {i} has non-numeric value: {point['value']}")

        logger.info(f"Validation passed: {len(data_points)} data points are valid")
        return True

    def get_summary(self, data_points):
        """
        Get summary statistics of parsed data.

        Args:
            data_points: List of data point dicts

        Returns:
            dict: Summary with countries, periods, and value ranges
        """
        if not data_points:
            return {
                'total_points': 0,
                'countries': [],
                'periods': [],
                'value_range': (None, None)
            }

        countries = sorted(set(p['country'] for p in data_points))
        periods = sorted(set(p['time_period'] for p in data_points))
        values = [p['value'] for p in data_points]

        return {
            'total_points': len(data_points),
            'unique_countries': len(countries),
            'unique_periods': len(periods),
            'countries': countries,
            'period_range': (periods[0], periods[-1]) if periods else (None, None),
            'value_range': (min(values), max(values)) if values else (None, None)
        }
