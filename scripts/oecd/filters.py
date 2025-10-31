"""
Data Filters for OECD Data

Filters to apply to fetched data to ensure quality and consistency.
"""

import logging

logger = logging.getLogger(__name__)


class OECDDataFilter:
    """Filter OECD data based on observation status and other criteria."""

    # OECD Observation Status codes
    # See: https://sdmx.org/wp-content/uploads/CL_OBS_STATUS_v2_1.docx
    OBS_STATUS_CODES = {
        'A': 'Normal value',
        'B': 'Break',
        'E': 'Estimated value',
        'F': 'Forecast value',
        'I': 'Imputed value',
        'M': 'Missing value',
        'P': 'Provisional value',
        'S': 'Strike',
        '': 'Not available (no status code)',
    }

    def __init__(self):
        pass

    def filter_by_status(self, data_points, allowed_statuses=None, csv_rows=None):
        """
        Filter data points by observation status.

        Args:
            data_points: List of parsed data point dicts
            allowed_statuses: List of allowed status codes (e.g., ['A', 'E'])
                            If None, allows all statuses
            csv_rows: Original CSV rows (if available) with status info

        Returns:
            tuple: (filtered_data_points, filter_stats)
        """
        if allowed_statuses is None:
            # No filtering
            return data_points, {'total': len(data_points), 'filtered': 0}

        if not csv_rows:
            logger.warning("No CSV rows provided, cannot filter by status")
            return data_points, {'total': len(data_points), 'filtered': 0}

        # Build lookup: (country, time_period) -> status
        status_lookup = {}
        for row in csv_rows:
            country = row.get('Reference area', '').strip()
            time_period = row.get('TIME_PERIOD', '').strip()
            status = row.get('OBS_STATUS', '').strip()
            if country and time_period:
                status_lookup[(country, time_period)] = status

        # Filter data points
        filtered_points = []
        status_counts = {}

        for point in data_points:
            key = (point['country'], point['time_period'])
            status = status_lookup.get(key, '')

            # Count statuses
            status_counts[status] = status_counts.get(status, 0) + 1

            # Check if allowed
            if status in allowed_statuses:
                filtered_points.append(point)

        # Log statistics
        logger.info(f"Status filter: {len(data_points)} -> {len(filtered_points)} points")
        for status, count in sorted(status_counts.items()):
            status_name = self.OBS_STATUS_CODES.get(status, 'Unknown')
            kept = 'KEPT' if status in allowed_statuses else 'FILTERED'
            logger.info(f"  {status or '(none)'} ({status_name}): {count} points [{kept}]")

        filter_stats = {
            'total': len(data_points),
            'filtered': len(filtered_points),
            'removed': len(data_points) - len(filtered_points),
            'status_counts': status_counts
        }

        return filtered_points, filter_stats

    def filter_incomplete_periods(self, data_points, min_countries=30):
        """
        Filter out time periods that have too few countries reporting.

        This helps identify periods where data is incomplete/preliminary.

        Args:
            data_points: List of parsed data point dicts
            min_countries: Minimum number of countries required for a period

        Returns:
            tuple: (filtered_data_points, filter_stats)
        """
        # Count countries per period
        period_counts = {}
        for point in data_points:
            period = point['time_period']
            period_counts[period] = period_counts.get(period, 0) + 1

        # Identify periods to keep
        valid_periods = {p for p, count in period_counts.items() if count >= min_countries}

        # Filter
        filtered_points = [p for p in data_points if p['time_period'] in valid_periods]

        logger.info(f"Period completeness filter: {len(data_points)} -> {len(filtered_points)} points")
        for period in sorted(period_counts.keys()):
            count = period_counts[period]
            kept = 'KEPT' if period in valid_periods else 'REMOVED'
            logger.info(f"  {period}: {count} countries [{kept}]")

        filter_stats = {
            'total': len(data_points),
            'filtered': len(filtered_points),
            'removed': len(data_points) - len(filtered_points),
            'period_counts': period_counts,
            'removed_periods': [p for p in period_counts.keys() if p not in valid_periods]
        }

        return filtered_points, filter_stats

    def get_recommended_filters(self, data_type='gdp'):
        """
        Get recommended filter settings for a data type.

        Args:
            data_type: Type of data ('gdp', 'employment', etc.)

        Returns:
            dict: Filter configuration
        """
        recommendations = {
            'gdp': {
                'allowed_statuses': ['A', 'E'],  # Normal and Estimated (exclude Provisional/Forecast)
                'min_countries_per_period': 30,
                'description': 'Exclude provisional and forecast values, require 30+ countries per period'
            },
            'strict': {
                'allowed_statuses': ['A'],  # Only normal values
                'min_countries_per_period': 35,
                'description': 'Only finalized data with high country coverage'
            },
            'permissive': {
                'allowed_statuses': ['A', 'E', 'P'],  # Include provisional
                'min_countries_per_period': 20,
                'description': 'Include provisional data, lower country threshold'
            }
        }

        return recommendations.get(data_type, recommendations['gdp'])
