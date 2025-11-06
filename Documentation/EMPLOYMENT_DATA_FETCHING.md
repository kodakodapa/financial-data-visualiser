# Employment Data Implementation Guide

## Overview

This guide documents the employment, unemployment, labour force, and migration data that has been added to the financial data visualizer. All configurations follow the existing OECD API client pattern and are ready to fetch data once OECD API access is available.

## Added Data Configurations

### 1. Overall Employment Metrics (Total Population)

#### `employment_rate`
- **Description**: Quarterly employment rate (% of working-age population, 15-64 years, total)
- **Unit**: percent
- **Frequency**: Quarterly
- **Dataset**: OECD Labour Force Statistics (DF_IALFS_EMP)

#### `unemployment_rate`
- **Description**: Quarterly unemployment rate (% of labour force, 15-64 years, total)
- **Unit**: percent
- **Frequency**: Quarterly
- **Dataset**: OECD Labour Force Statistics (DF_IALFS_UNE)

#### `labour_force_participation`
- **Description**: Quarterly labour force participation rate (% of working-age population, 15-64 years, total)
- **Unit**: percent
- **Frequency**: Quarterly
- **Dataset**: OECD Labour Force Statistics (DF_IALFS_POP)

### 2. Employment by Age Tiers

#### Youth (15-24 years)
- `employment_rate_youth` - Employment rate for youth
- `unemployment_rate_youth` - Unemployment rate for youth
- `labour_force_participation_youth` - Labour force participation for youth

#### Prime Age (25-54 years)
- `employment_rate_prime_age` - Employment rate for prime-age workers
- `unemployment_rate_prime_age` - Unemployment rate for prime-age workers
- `labour_force_participation_prime_age` - Labour force participation for prime-age workers

#### Older Workers (55-64 years)
- `employment_rate_older` - Employment rate for older workers
- `unemployment_rate_older` - Unemployment rate for older workers
- `labour_force_participation_older` - Labour force participation for older workers

### 3. Migration Statistics

#### `migration_inflows`
- **Description**: Annual inflows of foreign population by nationality (thousands)
- **Unit**: persons
- **Frequency**: Annual
- **Dataset**: OECD International Migration Database (DF_MIG)

#### `migration_outflows`
- **Description**: Annual outflows of foreign population by nationality (thousands)
- **Unit**: persons
- **Frequency**: Annual
- **Dataset**: OECD International Migration Database (DF_MIG)

#### `migration_stock`
- **Description**: Annual stock of foreign-born population (thousands)
- **Unit**: persons
- **Frequency**: Annual
- **Dataset**: OECD International Migration Database (DF_MIG)

## Usage Examples

### Fetching Latest Employment Data

```bash
# Fetch latest 2 quarters of overall employment rate
python scripts/fetch_oecd_data.py employment_rate --latest 2

# Fetch latest 2 quarters of unemployment rate
python scripts/fetch_oecd_data.py unemployment_rate --latest 2

# Fetch latest 2 quarters of labour force participation
python scripts/fetch_oecd_data.py labour_force_participation --latest 2
```

### Fetching Employment Data by Age Groups

```bash
# Youth employment (15-24 years)
python scripts/fetch_oecd_data.py employment_rate_youth --latest 4

# Prime-age employment (25-54 years)
python scripts/fetch_oecd_data.py employment_rate_prime_age --latest 4

# Older worker employment (55-64 years)
python scripts/fetch_oecd_data.py employment_rate_older --latest 4
```

### Fetching Unemployment Data by Age Groups

```bash
# Youth unemployment
python scripts/fetch_oecd_data.py unemployment_rate_youth --latest 4

# Prime-age unemployment
python scripts/fetch_oecd_data.py unemployment_rate_prime_age --latest 4

# Older worker unemployment
python scripts/fetch_oecd_data.py unemployment_rate_older --latest 4
```

### Fetching Historical Data

```bash
# Fetch employment data for a specific period
python scripts/fetch_oecd_data.py employment_rate --start 2020-Q1 --end 2024-Q4

# Backfill historical data (5-year batches)
python scripts/backfill_oecd_data.py employment_rate --start 2000-Q1 --end 2024-Q4 --batch-years 5
```

### Fetching Migration Data (Annual)

```bash
# Fetch latest 3 years of migration inflows
python scripts/fetch_oecd_data.py migration_inflows --latest 3

# Fetch migration outflows
python scripts/fetch_oecd_data.py migration_outflows --latest 3

# Fetch migration stock
python scripts/fetch_oecd_data.py migration_stock --latest 3
```

### Fetching All Employment Metrics at Once

```bash
# List all available datasets
python scripts/fetch_oecd_data.py --list

# Fetch multiple metrics in sequence
for metric in employment_rate unemployment_rate labour_force_participation; do
    python scripts/fetch_oecd_data.py $metric --latest 4
done
```

### Dry Run (Test Without Saving)

```bash
# Test fetching without saving to database
python scripts/fetch_oecd_data.py employment_rate --latest 2 --dry-run

# Test with provisional data included
python scripts/fetch_oecd_data.py unemployment_rate --latest 2 --dry-run --include-provisional
```

## Data Structure

All employment data is stored in the same SQLite database (`data/economic_data.db`) with the schema:

```sql
CREATE TABLE economic_data (
    country TEXT NOT NULL,
    time_period TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    source TEXT,
    last_updated TIMESTAMP,
    PRIMARY KEY (country, time_period, metric_name)
)
```

## Country Coverage

All configurations fetch data for 50+ countries including:
- 38 OECD member countries (USA, CAN, GBR, DEU, FRA, JPN, etc.)
- OECD aggregates (G7, EA20, EU27, OECD)
- Selected non-OECD economies (BRA, IND, IDN, ZAF, etc.)

See `ALL_COUNTRIES` in `scripts/oecd/data_configs.py` for the complete list.

## Age Tier Breakdowns

The OECD Labour Force Statistics provide data for three standard age groups:
- **Youth**: 15-24 years (early career, education-to-work transition)
- **Prime Age**: 25-54 years (peak working years)
- **Older Workers**: 55-64 years (pre-retirement)

These breakdowns are available for:
- Employment rates
- Unemployment rates
- Labour force participation rates

## Migration Data Notes

Migration statistics are reported **annually** (not quarterly) and include:

1. **Inflows**: Foreign nationals entering the country
2. **Outflows**: Foreign nationals leaving the country
3. **Stock**: Total foreign-born population residing in the country

These metrics help analyze:
- Impact of migration on labour markets
- Demographic changes
- Workforce composition shifts

## Observation Status Filtering

By default, data fetching filters by observation status:
- **A** (Normal): Included
- **E** (Estimated): Included
- **P** (Provisional): Excluded by default (use `--include-provisional`)
- **F** (Forecast): Excluded by default
- **M** (Missing): Excluded

To include all statuses:
```bash
python scripts/fetch_oecd_data.py employment_rate --latest 2 --no-filter-status
```

## API Access Notes

The OECD SDMX API is public and free, but:
- Temporary access issues may occur (503, 403 errors)
- URL length limits are handled via automatic country batching (30 countries per batch)
- Retry logic is built-in (up to 4 retries with exponential backoff)
- Data is upserted, so running fetches multiple times is safe

## Integration with Flask API

Once data is fetched, it's immediately available via the Flask API:

```bash
# Get employment rate for USA
curl http://localhost:5000/api/data?metric=employment_rate&country=USA

# Get unemployment rate for multiple countries
curl http://localhost:5000/api/data?metric=unemployment_rate&country=USA,CAN,GBR

# Get youth employment for a specific time range
curl "http://localhost:5000/api/data?metric=employment_rate_youth&country=USA&start_period=2020-Q1&end_period=2024-Q4"
```

## Next Steps

1. **Test API Access**: When OECD API is accessible, test fetching:
   ```bash
   python scripts/fetch_oecd_data.py employment_rate --latest 1 --dry-run
   ```

2. **Fetch Historical Data**: Build up historical time series:
   ```bash
   python scripts/backfill_oecd_data.py employment_rate --start 2000-Q1 --end 2024-Q4 --batch-years 5
   ```

3. **Update Frontend**: Add employment metrics to the visualization interface

4. **Create Dashboards**: Build visualizations comparing:
   - Employment rates across countries
   - Youth vs. prime-age vs. older worker trends
   - Unemployment rate changes over time
   - Migration patterns and their correlation with employment

## Troubleshooting

### 403 Forbidden Errors
If you encounter 403 errors:
1. Check OECD API status: https://data.oecd.org
2. Verify network connectivity
3. Wait a few minutes and retry (may be temporary rate limiting)

### Missing Data
Some countries may not report data for all age groups or time periods. The parser handles this gracefully.

### Data Revisions
OECD may revise historical data. Run periodic updates to keep data current:
```bash
python scripts/fetch_oecd_data.py employment_rate --start 2023-Q1 --end 2024-Q4
```

## Summary

You now have access to:
- ✅ 3 overall employment metrics (employment, unemployment, labour force participation)
- ✅ 9 age-tier breakdowns (3 metrics × 3 age groups)
- ✅ 3 migration statistics (inflows, outflows, stock)
- ✅ Data for 50+ countries
- ✅ Quarterly frequency for labour force statistics
- ✅ Annual frequency for migration statistics
- ✅ Full integration with existing OECD API client infrastructure
