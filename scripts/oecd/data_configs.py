"""
OECD Data Configuration

Defines the datasets to fetch from OECD API, including:
- API endpoints
- Data selection patterns
- Country lists
- Metric metadata
"""

# All OECD countries + key non-OECD economies
ALL_COUNTRIES = [
    # OECD Members
    'AUS', 'AUT', 'BEL', 'CAN', 'CHL', 'COL', 'CRI', 'CZE', 'DNK', 'EST',
    'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'ISL', 'IRL', 'ISR', 'ITA', 'JPN',
    'KOR', 'LVA', 'LTU', 'LUX', 'MEX', 'NLD', 'NZL', 'NOR', 'POL', 'PRT',
    'SVK', 'SVN', 'ESP', 'SWE', 'CHE', 'TUR', 'GBR', 'USA',
    # Aggregates
    'G7', 'EA20', 'EU15', 'EU27_2020', 'OECD', 'OECD26', 'OECDE',
    # Non-OECD Economies (if available)
    'ARG', 'BRA', 'BGR', 'HRV', 'IND', 'IDN', 'ROU', 'SAU', 'ZAF', 'USMCA'
]

# Country code to full name mapping (for reference)
COUNTRY_NAMES = {
    'AUS': 'Australia',
    'AUT': 'Austria',
    'BEL': 'Belgium',
    'CAN': 'Canada',
    'CHL': 'Chile',
    'COL': 'Colombia',
    'CRI': 'Costa Rica',
    'CZE': 'Czechia',
    'DNK': 'Denmark',
    'EST': 'Estonia',
    'FIN': 'Finland',
    'FRA': 'France',
    'DEU': 'Germany',
    'GRC': 'Greece',
    'HUN': 'Hungary',
    'ISL': 'Iceland',
    'IRL': 'Ireland',
    'ISR': 'Israel',
    'ITA': 'Italy',
    'JPN': 'Japan',
    'KOR': 'Korea',
    'LVA': 'Latvia',
    'LTU': 'Lithuania',
    'LUX': 'Luxembourg',
    'MEX': 'Mexico',
    'NLD': 'Netherlands',
    'NZL': 'New Zealand',
    'NOR': 'Norway',
    'POL': 'Poland',
    'PRT': 'Portugal',
    'SVK': 'Slovakia',
    'SVN': 'Slovenia',
    'ESP': 'Spain',
    'SWE': 'Sweden',
    'CHE': 'Switzerland',
    'TUR': 'Turkey',
    'GBR': 'United Kingdom',
    'USA': 'United States',
    'EA20': 'Euro area (20 countries)',
    'EU27_2020': 'European Union (27 countries from 01/02/2020)',
}

# Dataset configurations
DATA_CONFIGS = {
    'gdp_per_capita': {
        'dataset_path': 'OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA_EXPENDITURE_CAPITA,1.1',
        'data_selection_template': 'Q..{countries}........LR..',
        'countries': ALL_COUNTRIES,
        'metric_name': 'gdp_per_capita',
        'unit': 'USD_PPP',
        'source': 'OECD',
        'description': 'Quarterly GDP per capita, chain-linked volumes (rebased), PPP',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'population': {
        'dataset_path': 'OECD.ELS.SAE,DSD_POPULATION@DF_POP_HIST,1.0',
        'data_selection_template': '{countries}.POP.PS._T._T.',
        'countries': ALL_COUNTRIES,
        'metric_name': 'population',
        'unit': 'persons',
        'source': 'OECD',
        'description': 'Annual historical population data (total, both sexes)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'productivity_gdp_per_hour': {
        'dataset_path': 'OECD.SDD.TPS,DSD_PDB@DF_PDB_LV,1.0',
        'data_selection_template': 'A.{countries}.T_GDPHRS...',
        'countries': ALL_COUNTRIES,
        'metric_name': 'productivity_gdp_per_hour',
        'unit': 'USD_PPP_2015',
        'source': 'OECD',
        'description': 'Annual GDP per hour worked, PPP (2015 USD)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'productivity_growth_rate': {
        'dataset_path': 'OECD.SDD.TPS,DSD_PDB@DF_PDB_GR,1.0',
        'data_selection_template': 'A.{countries}.T_GDPHRS...',
        'countries': ALL_COUNTRIES,
        'metric_name': 'productivity_growth_rate',
        'unit': 'percent_annual',
        'source': 'OECD',
        'description': 'Annual productivity growth rate (GDP per hour worked, year-on-year %)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },
}

def get_config(config_name):
    """
    Get a data configuration by name.

    Args:
        config_name: Name of the configuration (e.g., 'gdp_per_capita')

    Returns:
        dict: Configuration dictionary

    Raises:
        KeyError: If config_name doesn't exist
    """
    if config_name not in DATA_CONFIGS:
        available = ', '.join(DATA_CONFIGS.keys())
        raise KeyError(f"Unknown config '{config_name}'. Available: {available}")

    return DATA_CONFIGS[config_name]

def list_configs():
    """
    List all available data configurations.

    Returns:
        list: List of configuration names
    """
    return list(DATA_CONFIGS.keys())
