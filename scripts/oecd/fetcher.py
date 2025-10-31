"""
OECD Data Fetcher

Orchestrates the complete workflow:
1. Build API URLs
2. Fetch data from OECD
3. Parse responses
4. Upsert to database
"""

import sqlite3
import logging
from datetime import datetime
from .query_builder import OECDQueryBuilder
from .api_client import OECDAPIClient
from .parser import OECDDataParser
from .data_configs import get_config

logger = logging.getLogger(__name__)


class OECDDataFetcher:
    """Orchestrate OECD data fetching and database upsert."""

    def __init__(self, db_path='data/economic_data.db'):
        """
        Initialize the fetcher.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.query_builder = OECDQueryBuilder()
        self.api_client = OECDAPIClient()
        self.parser = OECDDataParser()

    def fetch_and_upsert(
        self,
        config_name,
        start_period,
        end_period,
        dry_run=False,
        batch_size=30,
        filter_status=True,
        include_provisional=False
    ):
        """
        Fetch data from OECD and upsert to database.

        Args:
            config_name: Name of data configuration (e.g., 'gdp_per_capita')
            start_period: Start period (e.g., '2024-Q1')
            end_period: End period (e.g., '2025-Q3')
            dry_run: If True, fetch and parse but don't write to database
            batch_size: Number of countries per batch (default: 30)
            filter_status: If True, filter by observation status (default: True)
            include_provisional: If True, include provisional data (default: False)

        Returns:
            dict: Summary of operation (points fetched, inserted, updated)
        """
        logger.info(f"=" * 70)
        logger.info(f"FETCHING OECD DATA: {config_name}")
        logger.info(f"=" * 70)
        logger.info(f"Period: {start_period} to {end_period}")
        logger.info(f"Dry run: {dry_run}")
        logger.info(f"Status filtering: {filter_status}")
        if filter_status:
            allowed = ['A', 'E', 'P'] if include_provisional else ['A', 'E']
            logger.info(f"Allowed statuses: {allowed}")
        logger.info("")

        config = get_config(config_name)

        # Determine allowed statuses
        if filter_status:
            allowed_statuses = ['A', 'E', 'P'] if include_provisional else ['A', 'E']
        else:
            allowed_statuses = None

        # Build URLs (with batching for many countries)
        logger.info("Building API URLs...")
        batched_urls = self.query_builder.build_batched_urls(
            config_name=config_name,
            start_period=start_period,
            end_period=end_period,
            batch_size=batch_size
        )

        logger.info(f"Created {len(batched_urls)} batches of countries")

        # Fetch and parse data from all batches
        all_data_points = []

        for batch_num, url, countries in batched_urls:
            logger.info(f"\nProcessing batch {batch_num}/{len(batched_urls)}")
            logger.info(f"  Countries: {', '.join(countries[:5])}{'...' if len(countries) > 5 else ''}")

            try:
                # Fetch CSV
                csv_text = self.api_client.fetch_csv(url)

                # Parse CSV with status filtering
                data_points = self.parser.parse_csv(
                    csv_text,
                    config_name,
                    filter_status=filter_status,
                    allowed_statuses=allowed_statuses
                )

                logger.info(f"  Fetched {len(data_points)} data points")

                all_data_points.extend(data_points)

            except Exception as e:
                logger.error(f"  Error processing batch {batch_num}: {e}")
                # Continue with other batches
                continue

        if not all_data_points:
            logger.warning("No data points fetched")
            return {
                'success': False,
                'points_fetched': 0,
                'points_inserted': 0,
                'points_updated': 0,
                'error': 'No data points fetched'
            }

        # Validate data
        logger.info(f"\nValidating {len(all_data_points)} total data points...")
        self.parser.validate_data(all_data_points)

        # Show summary
        summary = self.parser.get_summary(all_data_points)
        logger.info(f"\nData summary:")
        logger.info(f"  Total points: {summary['total_points']}")
        logger.info(f"  Countries: {summary['unique_countries']}")
        logger.info(f"  Periods: {summary['period_range']}")
        logger.info(f"  Value range: {summary['value_range']}")

        # Upsert to database (unless dry run)
        if dry_run:
            logger.info("\nDRY RUN - Skipping database upsert")
            return {
                'success': True,
                'points_fetched': len(all_data_points),
                'points_inserted': 0,
                'points_updated': 0,
                'dry_run': True
            }

        logger.info("\nUpserting to database...")
        insert_count, update_count = self._upsert_to_database(
            data_points=all_data_points,
            metric_name=config['metric_name'],
            unit=config['unit'],
            source=config['source']
        )

        logger.info(f"\nUpsert complete:")
        logger.info(f"  Inserted: {insert_count}")
        logger.info(f"  Updated: {update_count}")
        logger.info(f"=" * 70)

        return {
            'success': True,
            'points_fetched': len(all_data_points),
            'points_inserted': insert_count,
            'points_updated': update_count
        }

    def _upsert_to_database(self, data_points, metric_name, unit, source):
        """
        Upsert data points to the database.

        Args:
            data_points: List of data point dicts
            metric_name: Metric name for database
            unit: Unit of measurement
            source: Data source

        Returns:
            tuple: (insert_count, update_count)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

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
        insert_count = 0
        update_count = 0

        for point in data_points:
            # Check if exists
            cursor.execute(
                'SELECT value FROM economic_data WHERE country=? AND time_period=? AND metric_name=?',
                (point['country'], point['time_period'], metric_name)
            )
            existing = cursor.fetchone()

            # Execute upsert
            cursor.execute(upsert_sql, (
                point['country'],
                point['time_period'],
                metric_name,
                point['value'],
                unit,
                source,
                timestamp
            ))

            if existing:
                update_count += 1
            else:
                insert_count += 1

        conn.commit()
        conn.close()

        return insert_count, update_count

    def close(self):
        """Clean up resources."""
        self.api_client.close()
