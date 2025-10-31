"""
OECD API Query Builder

Constructs properly formatted URLs for the OECD SDMX API based on
dataset configurations and time periods.
"""

from .data_configs import get_config


class OECDQueryBuilder:
    """Build OECD API query URLs."""

    BASE_URL = 'https://sdmx.oecd.org/public/rest/data/'

    def __init__(self):
        pass

    def build_url(
        self,
        dataset_path,
        data_selection,
        start_period,
        end_period,
        format_type='csvfilewithlabels'
    ):
        """
        Build a complete OECD API URL.

        Args:
            dataset_path: Dataset identifier (e.g., 'OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,1.1')
            data_selection: Data selection string (e.g., 'Q..AUT........LR..')
            start_period: Start period (e.g., '2024-Q1')
            end_period: End period (e.g., '2025-Q3')
            format_type: Response format (default: 'csvfilewithlabels')

        Returns:
            str: Complete API URL
        """
        url = f"{self.BASE_URL}{dataset_path}/{data_selection}"
        url += f"?startPeriod={start_period}&endPeriod={end_period}"

        if format_type:
            url += f"&format={format_type}"

        # Add dimensionAtObservation for better CSV structure
        url += "&dimensionAtObservation=AllDimensions"

        return url

    def build_from_config(
        self,
        config_name,
        start_period,
        end_period,
        countries=None,
        format_type='csvfilewithlabels'
    ):
        """
        Build URL from a data configuration.

        Args:
            config_name: Name of config in data_configs.py (e.g., 'gdp_per_capita')
            start_period: Start period (e.g., '2024-Q1')
            end_period: End period (e.g., '2025-Q3')
            countries: List of country codes or None to use config default
            format_type: Response format

        Returns:
            str: Complete API URL
        """
        config = get_config(config_name)

        # Use provided countries or default from config
        country_list = countries if countries else config['countries']

        # Join countries with '+' separator
        countries_str = '+'.join(country_list)

        # Fill in the country placeholder in data selection template
        data_selection = config['data_selection_template'].format(
            countries=countries_str
        )

        return self.build_url(
            dataset_path=config['dataset_path'],
            data_selection=data_selection,
            start_period=start_period,
            end_period=end_period,
            format_type=format_type
        )

    def build_batched_urls(
        self,
        config_name,
        start_period,
        end_period,
        batch_size=20,
        format_type='csvfilewithlabels'
    ):
        """
        Build multiple URLs with countries split into batches.

        Useful when the country list is very long and might exceed URL length limits.

        Args:
            config_name: Name of config in data_configs.py
            start_period: Start period (e.g., '2024-Q1')
            end_period: End period (e.g., '2025-Q3')
            batch_size: Number of countries per batch (default: 20)
            format_type: Response format

        Returns:
            list: List of (batch_num, url) tuples
        """
        config = get_config(config_name)
        all_countries = config['countries']

        urls = []
        for i in range(0, len(all_countries), batch_size):
            batch = all_countries[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            url = self.build_from_config(
                config_name=config_name,
                start_period=start_period,
                end_period=end_period,
                countries=batch,
                format_type=format_type
            )

            urls.append((batch_num, url, batch))

        return urls

    def calculate_period_range(self, start_year, start_quarter, end_year, end_quarter):
        """
        Calculate all quarters between start and end.

        Args:
            start_year: Starting year (e.g., 1995)
            start_quarter: Starting quarter (1-4)
            end_year: Ending year (e.g., 2025)
            end_quarter: Ending quarter (1-4)

        Returns:
            list: List of period strings (e.g., ['1995-Q1', '1995-Q2', ...])
        """
        periods = []
        year = start_year
        quarter = start_quarter

        while year < end_year or (year == end_year and quarter <= end_quarter):
            periods.append(f"{year}-Q{quarter}")

            quarter += 1
            if quarter > 4:
                quarter = 1
                year += 1

        return periods
