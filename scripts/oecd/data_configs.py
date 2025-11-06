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

    'savings_rate': {
        'dataset_path': 'OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE7_HHSAV,1.0',
        'data_selection_template': 'Q.{countries}._T._T._Z._T.N.PC_HDIS.',
        'countries': ALL_COUNTRIES,
        'metric_name': 'savings_rate',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly household net saving rate (% of disposable income)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'disposable_income_per_capita': {
        'dataset_path': 'OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA_INCOME_CAPITA,1.1',
        'data_selection_template': 'Q..{countries}..B6N.LR..',
        'countries': ALL_COUNTRIES,
        'metric_name': 'disposable_income_per_capita',
        'unit': 'USD_PPP',
        'source': 'OECD',
        'description': 'Quarterly household net disposable income per capita, PPP',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    # Hours Worked Statistics
    'hours_worked_annual': {
        'dataset_path': 'OECD.ELS.SAE,DSD_HW@DF_AVG_ANN_HRS_WKD,1.0',
        'data_selection_template': 'A.{countries}...._T...',
        'countries': ALL_COUNTRIES,
        'metric_name': 'hours_worked_annual',
        'unit': 'hours_per_year',
        'source': 'OECD',
        'description': 'Annual average hours actually worked per worker',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'hours_worked_weekly_age_15_24': {
        'dataset_path': 'OECD.ELS.SAE,DSD_HW@DF_AVG_USL_WK_WKD,1.0',
        'data_selection_template': '{countries}.._T.Y15T24...._T._T...',
        'countries': ALL_COUNTRIES,
        'metric_name': 'hours_worked_weekly_age_15_24',
        'unit': 'hours_per_week',
        'source': 'OECD',
        'description': 'Average usual weekly hours worked, age 15-24 years',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'hours_worked_weekly_age_25_54': {
        'dataset_path': 'OECD.ELS.SAE,DSD_HW@DF_AVG_USL_WK_WKD,1.0',
        'data_selection_template': '{countries}.._T.Y25T54...._T._T...',
        'countries': ALL_COUNTRIES,
        'metric_name': 'hours_worked_weekly_age_25_54',
        'unit': 'hours_per_week',
        'source': 'OECD',
        'description': 'Average usual weekly hours worked, age 25-54 years',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'hours_worked_weekly_age_55_64': {
        'dataset_path': 'OECD.ELS.SAE,DSD_HW@DF_AVG_USL_WK_WKD,1.0',
        'data_selection_template': '{countries}.._T.Y55T64...._T._T...',
        'countries': ALL_COUNTRIES,
        'metric_name': 'hours_worked_weekly_age_55_64',
        'unit': 'hours_per_week',
        'source': 'OECD',
        'description': 'Average usual weekly hours worked, age 55-64 years',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'hours_worked_weekly_age_65_plus': {
        'dataset_path': 'OECD.ELS.SAE,DSD_HW@DF_AVG_USL_WK_WKD,1.0',
        'data_selection_template': '{countries}.._T.Y_GE65...._T._T...',
        'countries': ALL_COUNTRIES,
        'metric_name': 'hours_worked_weekly_age_65_plus',
        'unit': 'hours_per_week',
        'source': 'OECD',
        'description': 'Average usual weekly hours worked, age 65+ years',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'hours_worked_weekly_total': {
        'dataset_path': 'OECD.ELS.SAE,DSD_HW@DF_AVG_USL_WK_WKD,1.0',
        'data_selection_template': '{countries}.._T._T...._T._T...',
        'countries': ALL_COUNTRIES,
        'metric_name': 'hours_worked_weekly_total',
        'unit': 'hours_per_week',
        'source': 'OECD',
        'description': 'Average usual weekly hours worked, all ages',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    # Employment and Labour Force Statistics
    'employment_rate': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_EMP,1.0',
        'data_selection_template': 'Q.{countries}._T._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'employment_rate',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly employment rate (% of working-age population, 15-64 years, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'unemployment_rate': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_UNE,1.0',
        'data_selection_template': 'Q.{countries}._T._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'unemployment_rate',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly unemployment rate (% of labour force, 15-64 years, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'labour_force_participation': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_POP,1.0',
        'data_selection_template': 'Q.{countries}._T._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'labour_force_participation',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly labour force participation rate (% of working-age population, 15-64 years, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    # Employment by Age Groups
    'employment_rate_youth': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_EMP,1.0',
        'data_selection_template': 'Q.{countries}.Y15T24._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'employment_rate_youth',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly employment rate for youth (% of population aged 15-24, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'employment_rate_prime_age': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_EMP,1.0',
        'data_selection_template': 'Q.{countries}.Y25T54._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'employment_rate_prime_age',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly employment rate for prime-age workers (% of population aged 25-54, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'employment_rate_older': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_EMP,1.0',
        'data_selection_template': 'Q.{countries}.Y55T64._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'employment_rate_older',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly employment rate for older workers (% of population aged 55-64, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    # Unemployment by Age Groups
    'unemployment_rate_youth': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_UNE,1.0',
        'data_selection_template': 'Q.{countries}.Y15T24._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'unemployment_rate_youth',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly unemployment rate for youth (% of labour force aged 15-24, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'unemployment_rate_prime_age': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_UNE,1.0',
        'data_selection_template': 'Q.{countries}.Y25T54._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'unemployment_rate_prime_age',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly unemployment rate for prime-age workers (% of labour force aged 25-54, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'unemployment_rate_older': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_UNE,1.0',
        'data_selection_template': 'Q.{countries}.Y55T64._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'unemployment_rate_older',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly unemployment rate for older workers (% of labour force aged 55-64, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    # Labour Force Participation by Age Groups
    'labour_force_participation_youth': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_POP,1.0',
        'data_selection_template': 'Q.{countries}.Y15T24._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'labour_force_participation_youth',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly labour force participation rate for youth (% of population aged 15-24, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'labour_force_participation_prime_age': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_POP,1.0',
        'data_selection_template': 'Q.{countries}.Y25T54._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'labour_force_participation_prime_age',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly labour force participation rate for prime-age workers (% of population aged 25-54, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'labour_force_participation_older': {
        'dataset_path': 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_POP,1.0',
        'data_selection_template': 'Q.{countries}.Y55T64._T',
        'countries': ALL_COUNTRIES,
        'metric_name': 'labour_force_participation_older',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly labour force participation rate for older workers (% of population aged 55-64, total)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    # Migration Statistics (Annual data)
    'migration_inflows': {
        'dataset_path': 'OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0',
        'data_selection_template': 'A.{countries}.B11',
        'countries': ALL_COUNTRIES,
        'metric_name': 'migration_inflows',
        'unit': 'persons',
        'source': 'OECD',
        'description': 'Annual inflows of foreign population by nationality (thousands)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'migration_outflows': {
        'dataset_path': 'OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0',
        'data_selection_template': 'A.{countries}.B21',
        'countries': ALL_COUNTRIES,
        'metric_name': 'migration_outflows',
        'unit': 'persons',
        'source': 'OECD',
        'description': 'Annual outflows of foreign population by nationality (thousands)',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },

    'migration_stock': {
        'dataset_path': 'OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0',
        'data_selection_template': 'A.{countries}.B11_B21',
        'countries': ALL_COUNTRIES,
        'metric_name': 'migration_stock',
        'unit': 'persons',
        'source': 'OECD',
        'description': 'Annual stock of foreign-born population (thousands)',
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
