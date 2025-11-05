# Productivity Data Fetching from OECD API

## Overview

The system now supports fetching productivity data directly from the OECD API, similar to GDP per capita and population data. This provides access to official OECD productivity statistics based on GDP per hour worked.

## Available Productivity Datasets

### 1. productivity_gdp_per_hour
**GDP per Hour Worked (Levels)**

- **Source**: OECD Productivity Database (PDB_LV)
- **Unit**: USD_PPP_2015 (2015 US Dollars, Purchasing Power Parity)
- **Frequency**: Annual
- **Description**: Measures the level of GDP produced per hour worked
- **Coverage**: OECD countries and selected non-OECD economies
- **Indicator**: T_GDPHRS (Total economy GDP per hour worked)

This is the primary measure of labour productivity, showing how efficiently an economy converts labour input into output.

### 2. productivity_growth_rate
**Productivity Growth Rate**

- **Source**: OECD Productivity Database (PDB_GR)
- **Unit**: percent_annual (Year-on-year percentage change)
- **Frequency**: Annual
- **Description**: Annual growth rate of GDP per hour worked
- **Coverage**: OECD countries and selected non-OECD economies
- **Indicator**: T_GDPHRS (Total economy GDP per hour worked growth)

Shows the year-over-year change in productivity, useful for tracking productivity trends over time.

## Comparison with Calculated Metrics

The system provides both OECD-sourced and calculated productivity metrics:

| Metric | Source | Frequency | Unit | Base Data |
|--------|--------|-----------|------|-----------|
| **productivity_gdp_per_hour** | OECD API | Annual | USD_PPP_2015 | Official OECD calculations |
| **productivity_growth_rate** | OECD API | Annual | % annual | Official OECD calculations |
| **productivity_growth** | Calculated | Quarterly | USD_PPP | GDP per capita Q-o-Q change |
| **productivity_growth_pct** | Calculated | Quarterly | % | GDP per capita Q-o-Q % change |

**Key Differences:**
- **OECD metrics** are based on hours worked (more precise measure of labour productivity)
- **Calculated metrics** are based on GDP per capita (approximation when hours worked data unavailable)
- **OECD metrics** are annual, **calculated metrics** are quarterly
- **OECD metrics** use official methodology, **calculated metrics** are simple derivatives

## Usage

### Fetch Latest Data

```bash
# Fetch latest year of GDP per hour worked
python scripts/fetch_oecd_data.py productivity_gdp_per_hour --latest 1

# Fetch latest year of productivity growth rates
python scripts/fetch_oecd_data.py productivity_growth_rate --latest 1

# Fetch both productivity datasets
python scripts/fetch_oecd_data.py productivity_gdp_per_hour --latest 1
python scripts/fetch_oecd_data.py productivity_growth_rate --latest 1
```

### Fetch Specific Time Period

```bash
# Fetch specific years
python scripts/fetch_oecd_data.py productivity_gdp_per_hour --start 2020 --end 2023

# Fetch all available historical data
python scripts/backfill_oecd_data.py productivity_gdp_per_hour --start 1970 --end 2023 --batch-years 10
```

### Fetch All Datasets (Including Productivity)

```bash
# Fetch latest data for all configured datasets
python scripts/fetch_oecd_data.py --all --latest 1

# Dry run to see what would be fetched
python scripts/fetch_oecd_data.py --all --latest 1 --dry-run
```

### Test Configuration

```bash
# Test the productivity configuration
python scripts/exploration/test_productivity_fetch.py
```

## API Endpoints

The productivity data uses the following OECD SDMX API endpoints:

### GDP per Hour Worked (Levels)
```
https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PDB@DF_PDB_LV,1.0/A.{COUNTRIES}.T_GDPHRS...
```

### Productivity Growth Rate
```
https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PDB@DF_PDB_GR,1.0/A.{COUNTRIES}.T_GDPHRS...
```

**Parameters:**
- `A`: Annual frequency
- `{COUNTRIES}`: Plus-separated country codes (e.g., USA+GBR+AUS)
- `T_GDPHRS`: Total economy GDP per hour worked

## Configuration

The productivity datasets are configured in `scripts/oecd/data_configs.py`:

```python
'productivity_gdp_per_hour': {
    'dataset_path': 'OECD.SDD.TPS,DSD_PDB@DF_PDB_LV,1.0',
    'data_selection_template': 'A.{countries}.T_GDPHRS...',
    'countries': ALL_COUNTRIES,
    'metric_name': 'productivity_gdp_per_hour',
    'unit': 'USD_PPP_2015',
    'source': 'OECD',
    'description': 'Annual GDP per hour worked, PPP (2015 USD)',
}

'productivity_growth_rate': {
    'dataset_path': 'OECD.SDD.TPS,DSD_PDB@DF_PDB_GR,1.0',
    'data_selection_template': 'A.{countries}.T_GDPHRS...',
    'countries': ALL_COUNTRIES,
    'metric_name': 'productivity_growth_rate',
    'unit': 'percent_annual',
    'source': 'OECD',
    'description': 'Annual productivity growth rate (GDP per hour worked, year-on-year %)',
}
```

## Example Workflow

### 1. Initial Backfill (Historical Data)

```bash
# Fetch historical productivity levels from 1970 to present
python scripts/backfill_oecd_data.py productivity_gdp_per_hour \
    --start 1970 \
    --end 2023 \
    --batch-years 10

# Fetch historical productivity growth rates
python scripts/backfill_oecd_data.py productivity_growth_rate \
    --start 1970 \
    --end 2023 \
    --batch-years 10
```

### 2. Periodic Updates

```bash
# Update all datasets monthly (add to cron/scheduler)
python scripts/fetch_oecd_data.py --all --latest 2
```

### 3. Access via API

```bash
# Start the Flask server
python app.py

# Query productivity data
curl "http://localhost:5000/api/data?metric=productivity_gdp_per_hour&countries=United States,Canada"

# Query growth rates
curl "http://localhost:5000/api/data?metric=productivity_growth_rate&countries=United States,Canada"

# Correlate productivity with GDP
curl "http://localhost:5000/api/correlate?metric1=productivity_gdp_per_hour&metric2=gdp_per_capita&countries=United States"
```

## Data Quality Notes

### Observation Status Filtering

Like other OECD datasets, productivity data is filtered by observation status:
- **Included by default**: Normal (A), Estimated (E)
- **Excluded by default**: Provisional (P), Forecast (F)

To include provisional data:
```bash
python scripts/fetch_oecd_data.py productivity_gdp_per_hour --latest 1 --include-provisional
```

To disable all filtering:
```bash
python scripts/fetch_oecd_data.py productivity_gdp_per_hour --latest 1 --no-filter-status
```

### Country Coverage

Productivity data may not be available for all countries in `ALL_COUNTRIES`. The OECD Productivity Database has good coverage for:
- All OECD member countries
- G7 and OECD aggregates
- Selected non-OECD economies (coverage varies)

Missing data for a country will be logged but won't cause the fetch to fail.

### Data Revisions

OECD revises productivity data as new information becomes available. The upsert mechanism handles these revisions automatically:
- Existing records are updated with new values
- `last_updated` timestamp tracks when data was last fetched

## Troubleshooting

### 403 Forbidden Errors

If you encounter 403 errors when fetching:
1. Check network/firewall restrictions
2. Verify OECD API is accessible: `curl https://sdmx.oecd.org/public/rest/dataflow`
3. Try with a browser to rule out authentication issues

### Missing Data for Specific Countries

Some countries may not have productivity data available:
- Check OECD's data availability for that country
- Use calculated metrics (`productivity_growth`, `productivity_growth_pct`) as fallback
- These are automatically available for all countries with GDP per capita data

### Annual vs Quarterly Data

Remember that OECD productivity metrics are **annual**, while calculated metrics are **quarterly**:
- For quarterly analysis, use `productivity_growth` and `productivity_growth_pct`
- For official OECD comparisons, use `productivity_gdp_per_hour` and `productivity_growth_rate`
- They measure slightly different things (hours worked vs. per capita)

## References

- **OECD Productivity Database**: https://www.oecd.org/en/data/indicators/gdp-per-hour-worked.html
- **OECD Compendium of Productivity Indicators**: Published annually
- **SDMX API Documentation**: https://data.oecd.org/api/sdmx-ml-documentation/
