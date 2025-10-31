"""
OECD API Client

Handles HTTP requests to the OECD SDMX API with retry logic and error handling.
"""

import requests
import time
import logging

logger = logging.getLogger(__name__)


class OECDAPIClient:
    """Client for fetching data from OECD SDMX API."""

    def __init__(self, timeout=60, max_retries=3, retry_delay=2):
        """
        Initialize the API client.

        Args:
            timeout: Request timeout in seconds (default: 60)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Delay between retries in seconds (default: 2)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()

    def fetch(self, url, retries=None):
        """
        Fetch data from a URL with retry logic.

        Args:
            url: URL to fetch
            retries: Number of retries (uses self.max_retries if None)

        Returns:
            requests.Response: Response object

        Raises:
            requests.exceptions.RequestException: If all retries fail
        """
        if retries is None:
            retries = self.max_retries

        last_exception = None

        for attempt in range(retries + 1):
            try:
                logger.info(f"Fetching URL (attempt {attempt + 1}/{retries + 1}): {url[:100]}...")

                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                logger.info(f"Successfully fetched data ({len(response.content)} bytes)")
                return response

            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Request timeout on attempt {attempt + 1}: {e}")

            except requests.exceptions.HTTPError as e:
                last_exception = e
                logger.error(f"HTTP error on attempt {attempt + 1}: {e}")

                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    raise

            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"Request failed on attempt {attempt + 1}: {e}")

            # Wait before retrying (unless this was the last attempt)
            if attempt < retries:
                sleep_time = self.retry_delay * (attempt + 1)  # Exponential backoff
                logger.info(f"Waiting {sleep_time}s before retry...")
                time.sleep(sleep_time)

        # All retries exhausted
        logger.error(f"All {retries + 1} attempts failed")
        raise last_exception

    def fetch_csv(self, url):
        """
        Fetch CSV data from URL.

        Args:
            url: URL to fetch

        Returns:
            str: CSV content as text

        Raises:
            requests.exceptions.RequestException: If fetch fails
        """
        response = self.fetch(url)
        return response.text

    def fetch_binary(self, url):
        """
        Fetch binary data from URL.

        Args:
            url: URL to fetch

        Returns:
            bytes: Response content

        Raises:
            requests.exceptions.RequestException: If fetch fails
        """
        response = self.fetch(url)
        return response.content

    def test_connection(self):
        """
        Test connection to OECD API.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Simple test query - fetch latest quarter for Austria GDP per capita
            test_url = (
                "https://sdmx.oecd.org/public/rest/data/"
                "OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA_EXPENDITURE_CAPITA,1.1/"
                "Q..AUT........LR..?startPeriod=2024-Q1&endPeriod=2024-Q1"
            )

            logger.info("Testing OECD API connection...")
            self.fetch(test_url)
            logger.info("Connection test successful")
            return True

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def close(self):
        """Close the session."""
        self.session.close()
