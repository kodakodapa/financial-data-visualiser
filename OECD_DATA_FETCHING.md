# OECD Data Fetching System

## Overview

Automated system for fetching economic data from the OECD SDMX API and upserting it into the local database. Supports both periodic updates and historical backfills.

## Architecture

```
scripts/oecd/
├── __init__.py           # Module exports
├── data_configs.py       # Dataset definitions (gdp_per_capita, real_gdp)
├── query_builder.py      # Build OECD API URLs
├── api_client.py         # HTTP client with retry logic
├── parser.py             # Parse CSV responses
└── fetcher.py            # Orchestrate fetch → parse → upsert

scripts/
├── fetch_oecd_data.py    # CLI tool for periodic updates
└── backfill_oecd_data.py # CLI tool for historical backfills
```

## Quick Start

### 1. List Available Datasets

```bash
python scripts/fetch_oecd_data.py --list
```

Output:
```
Available data configurations:
  - gdp_per_capita
  - real_gdp
```

### 2. Fetch Latest Data (Dry Run)

```bash
# Test without saving to database
python scripts/fetch_oecd_data.py gdp_per_capita --start 2025-Q2 --end 2025-Q3 --dry-run
```

### 3. Fetch and Save to Database

```bash
# Fetch Q2-Q3 2025 for GDP per capita
python scripts/fetch_oecd_data.py gdp_per_capita --start 2025-Q2 --end 2025-Q3

# Include provisional data (by default only Normal and Estimated data is included)
python scripts/fetch_oecd_data.py gdp_per_capita --start 2025-Q2 --end 2025-Q3 --include-provisional

# Disable status filtering entirely (accept all data)
python scripts/fetch_oecd_data.py gdp_per_capita --start 2025-Q2 --end 2025-Q3 --no-filter-status
```

### 4. Backfill Historical Data

```bash
# Backfill all data from 1995
python scripts/backfill_oecd_data.py gdp_per_capita --start 1995-Q1 --end 2025-Q3 --batch-years 5
```

## Usage Examples

### Periodic Updates (Quarterly)

Fetch the latest 2 quarters to catch new data and revisions:

```bash
python scripts/fetch_oecd_data.py gdp_per_capita --latest 2
python scripts/fetch_oecd_data.py real_gdp --latest 2
```

Or fetch all configured datasets:

```bash
python scripts/fetch_oecd_data.py --all --latest 2
```

### Backfill from 1995

```bash
# Single dataset
python scripts/backfill_oecd_data.py gdp_per_capita --start 1995-Q1 --end 2025-Q3 --batch-years 5

# All datasets
python scripts/backfill_oecd_data.py --all --start 1995-Q1 --end 2025-Q3 --batch-years 5
```

The `--batch-years 5` option splits the request into 5-year batches to avoid timeouts.

### Fetch Specific Time Range

```bash
python scripts/fetch_oecd_data.py gdp_per_capita --start 2020-Q1 --end 2023-Q4
```

## Current Datasets

### GDP per Capita

- **Config name**: `gdp_per_capita`
- **OECD dataset**: `DF_QNA_EXPENDITURE_CAPITA`
- **Description**: Quarterly GDP per capita, chain-linked volumes (rebased), PPP
- **Unit**: USD_PPP
- **Countries**: All OECD members + aggregates (~50)
- **Metric name in DB**: `gdp_per_capita`

### Real GDP

- **Config name**: `real_gdp`
- **OECD dataset**: `DF_QNA`
- **Description**: Quarterly National Accounts - Real GDP, seasonally adjusted, PPP
- **Unit**: USD_PPP
- **Countries**: All OECD members + aggregates (~50)
- **Metric name in DB**: `real_gdp`

## Countries Included

All OECD member countries:
- Australia, Austria, Belgium, Canada, Chile, Colombia, Costa Rica, Czechia, Denmark, Estonia
- Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Japan
- Korea, Latvia, Lithuania, Luxembourg, Mexico, Netherlands, New Zealand, Norway, Poland, Portugal
- Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, United Kingdom, United States

Plus aggregates:
- G7, EA20 (Euro area 20), EU15, EU27_2020, OECD, OECD26, OECDE

Plus selected non-OECD economies (if available):
- Argentina, Brazil, Bulgaria, Croatia, India, Indonesia, Romania, Saudi Arabia, South Africa, USMCA

## How It Works

### 1. Query Builder

Constructs OECD API URLs based on dataset configuration:

```python
from oecd import OECDQueryBuilder

builder = OECDQueryBuilder()
url = builder.build_from_config(
    config_name='gdp_per_capita',
    start_period='2025-Q2',
    end_period='2025-Q3'
)
```

### 2. API Client

Fetches data with retry logic:

```python
from oecd import OECDAPIClient

client = OECDAPIClient(timeout=60, max_retries=3)
csv_text = client.fetch_csv(url)
```

### 3. Parser

Parses CSV into structured data with observation status filtering:

```python
from oecd import OECDDataParser

parser = OECDDataParser()
data_points = parser.parse_csv(
    csv_text,
    'gdp_per_capita',
    filter_status=True,
    allowed_statuses=['A', 'E']  # Normal and Estimated only
)
# Returns: [{'country': 'Spain', 'time_period': '2025-Q2', 'value': 43500.5, 'status': 'A'}, ...]
```

### 4. Fetcher (Orchestrator)

Coordinates the entire workflow:

```python
from oecd import OECDDataFetcher

fetcher = OECDDataFetcher()
result = fetcher.fetch_and_upsert(
    config_name='gdp_per_capita',
    start_period='2025-Q2',
    end_period='2025-Q3',
    dry_run=False,
    filter_status=True,
    include_provisional=False
)
```

## Data Quality: Observation Status Filtering

### What is Observation Status?

OECD data comes with an `OBS_STATUS` field indicating data quality:

| Status | Name | Description | Default |
|--------|------|-------------|---------|
| A | Normal | Final, official data | ✓ Included |
| E | Estimated | Estimated values | ✓ Included |
| P | Provisional | Preliminary, subject to revision | ✗ Excluded |
| F | Forecast | Projected future values | ✗ Excluded |
| M | Missing | Data not available | ✗ Excluded |

### Why Filter?

Provisional and forecast data can be significantly different from final values:
- Provisional data may be based on incomplete information
- Forecast data represents projections, not actual measurements
- Including this data can create misleading visualizations

**Example issue**: User reported "weird results for the last quarter" where data was "significantly out of line" - investigation revealed this was provisional data that hadn't been finalized yet.

### Default Behavior

By default, the system **filters data** to include only:
- **A (Normal)**: Final, official values
- **E (Estimated)**: Estimated values (considered reliable)

This excludes:
- **P (Provisional)**: Preliminary data
- **F (Forecast)**: Projected values

### Override Filtering

#### Include Provisional Data

To include provisional data (P) in addition to Normal (A) and Estimated (E):

```bash
python scripts/fetch_oecd_data.py gdp_per_capita --start 2025-Q2 --end 2025-Q3 --include-provisional
python scripts/backfill_oecd_data.py gdp_per_capita --start 1995-Q1 --end 2025-Q3 --include-provisional
```

Allowed statuses: A, E, P

#### Disable All Filtering

To accept all data regardless of observation status:

```bash
python scripts/fetch_oecd_data.py gdp_per_capita --start 2025-Q2 --end 2025-Q3 --no-filter-status
python scripts/backfill_oecd_data.py gdp_per_capita --start 1995-Q1 --end 2025-Q3 --no-filter-status
```

### Monitoring Status

The parser logs detailed status breakdown:

```
Observation status breakdown:
  A (Normal): 35 [KEPT]
  E (Estimated): 3 [KEPT]
  P (Provisional): 2 [FILTERED]
```

This helps you understand what data is being included/excluded.

## Batching

The system automatically batches countries to avoid URL length limits:

- Default batch size: 30 countries per request
- For 50 countries → 2 batches
- Each batch is fetched separately and results are combined

## Error Handling

### Retry Logic

- HTTP requests retry up to 3 times with exponential backoff
- Timeouts: 60 seconds per request
- 4xx errors (client errors) are not retried
- 5xx errors and timeouts trigger retries

### Logging

All operations are logged to:
- `logs/oecd_fetch.log` - Periodic updates
- `logs/oecd_backfill.log` - Historical backfills

Log format:
```
2025-10-31 09:10:01,390 - oecd.fetcher - INFO - FETCHING OECD DATA: gdp_per_capita
2025-10-31 09:10:05,679 - oecd.api_client - INFO - Successfully fetched data (14854 bytes)
2025-10-31 09:10:05,681 - oecd.parser - INFO - Parsed 26 data points
```

### Failed Batches

- If a batch fails, the system continues with remaining batches
- Final summary shows which batches succeeded/failed
- Exit code 1 if any batch fails, 0 if all succeed

## Database Upsert

Data is upserted using:
```sql
INSERT INTO economic_data (country, time_period, metric_name, value, unit, source, last_updated)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(country, time_period, metric_name)
DO UPDATE SET
    value = excluded.value,
    unit = excluded.unit,
    source = excluded.source,
    last_updated = excluded.last_updated
```

- **New data** → Inserted
- **Existing data** → Updated (handles OECD revisions)
- **Composite key**: (country, time_period, metric_name)

## Adding New Datasets

To add a new economic indicator (e.g., employment rate):

### 1. Add Configuration

Edit `scripts/oecd/data_configs.py`:

```python
DATA_CONFIGS = {
    # ... existing configs ...

    'employment_rate': {
        'dataset_path': 'OECD.XXX.YYY,DSD_ZZZ@DF_EMPLOYMENT,1.1',
        'data_selection_template': 'Q..{countries}........',
        'countries': ALL_COUNTRIES,
        'metric_name': 'employment_rate',
        'unit': 'percent',
        'source': 'OECD',
        'description': 'Quarterly employment rate',
        'value_column': 'OBS_VALUE',
        'country_column': 'Reference area',
        'time_column': 'TIME_PERIOD',
    },
}
```

### 2. Use It

```bash
python scripts/fetch_oecd_data.py employment_rate --latest 2
```

## CLI Reference

### fetch_oecd_data.py

```bash
# Fetch specific config and period
python scripts/fetch_oecd_data.py <config> --start YYYY-QN --end YYYY-QN [--dry-run]

# Fetch latest N quarters
python scripts/fetch_oecd_data.py <config> --latest N [--dry-run]

# Fetch all configs
python scripts/fetch_oecd_data.py --all --latest N

# List available configs
python scripts/fetch_oecd_data.py --list
```

**Options:**
- `<config>`: Config name (gdp_per_capita, real_gdp)
- `--start YYYY-QN`: Start period (e.g., 2025-Q1)
- `--end YYYY-QN`: End period (e.g., 2025-Q3)
- `--latest N`: Fetch latest N quarters from now
- `--all`: Fetch all configured datasets
- `--dry-run`: Fetch and parse but don't save to database
- `--include-provisional`: Include provisional data (status P). By default, only Normal (A) and Estimated (E) data is included
- `--no-filter-status`: Disable status filtering (accept all data regardless of observation status)
- `--list`: List available configurations

### backfill_oecd_data.py

```bash
# Backfill specific config
python scripts/backfill_oecd_data.py <config> --start YYYY-QN --end YYYY-QN [--batch-years N] [--dry-run]

# Backfill all configs
python scripts/backfill_oecd_data.py --all --start YYYY-QN --end YYYY-QN [--batch-years N]
```

**Options:**
- `--batch-years N`: Split into batches of N years (recommended for large ranges)
- `--include-provisional`: Include provisional data (status P)
- `--no-filter-status`: Disable status filtering
- Other options same as fetch_oecd_data.py

## Recommended Workflow

### Initial Setup (Once)

```bash
# 1. Backfill GDP per capita from 1995
python scripts/backfill_oecd_data.py gdp_per_capita --start 1995-Q1 --end 2025-Q3 --batch-years 5

# 2. Backfill real GDP from 1995
python scripts/backfill_oecd_data.py real_gdp --start 1995-Q1 --end 2025-Q3 --batch-years 5

# 3. Recalculate cumulative return
python scripts/calculate_cumulative_return.py gdp_per_capita gdp_cumulative_return_per_capita
```

### Quarterly Updates (Manual)

Run at quarter end + 45 days (when OECD publishes):

```bash
# Fetch latest 2 quarters (catches new data + revisions)
python scripts/fetch_oecd_data.py gdp_per_capita --latest 2
python scripts/fetch_oecd_data.py real_gdp --latest 2

# Recalculate cumulative return if needed
python scripts/calculate_cumulative_return.py gdp_per_capita gdp_cumulative_return_per_capita
```

## Testing

### Dry Run Test

```bash
python scripts/fetch_oecd_data.py gdp_per_capita --start 2025-Q2 --end 2025-Q3 --dry-run
```

Expected output:
```
[OK] Fetched: 40 points
```

### Connection Test

```python
from oecd import OECDAPIClient

client = OECDAPIClient()
success = client.test_connection()  # Returns True if API is accessible
```

## Troubleshooting

### Issue: "Weird results" or data "significantly out of line"

**Cause**: Provisional or forecast data is being included

**Solution**: The default filtering should prevent this, but if you used `--no-filter-status` or `--include-provisional`, remove those flags. The system will then only include Normal (A) and Estimated (E) data, excluding preliminary values.

### Issue: "No data points found"

**Cause**: Time period might be outside available data range, or all data is being filtered out due to observation status

**Solution**:
- Check OECD website for data availability
- Try a different period
- Check the log output for "Observation status breakdown" to see what statuses are present
- If needed, use `--include-provisional` to include more data

### Issue: "HTTP 404 Not Found"

**Cause**: Dataset path or data selection is incorrect

**Solution**: Verify dataset configuration against OECD API documentation

### Issue: "Connection timeout"

**Cause**: Network issues or OECD API is slow/down

**Solution**:
- Check internet connection
- Try again later
- Increase timeout: edit `api_client.py` and change `timeout=60` to `timeout=120`

### Issue: "Missing required columns"

**Cause**: OECD changed their CSV format

**Solution**: Check the error message for available columns, update `data_configs.py` column names

## Performance

- **Small fetch** (1-2 quarters, 40 countries): ~10 seconds
- **Medium fetch** (10 quarters, 40 countries): ~30 seconds
- **Large backfill** (30 years, 40 countries): ~5-10 minutes (with batching)

## Files Created/Modified

**New files:**
- `scripts/oecd/` - Complete OECD fetching module
- `scripts/fetch_oecd_data.py` - CLI for periodic updates
- `scripts/backfill_oecd_data.py` - CLI for backfills
- `logs/oecd_fetch.log` - Fetch operation logs
- `logs/oecd_backfill.log` - Backfill operation logs

**Modified files:**
- `requirements.txt` - Added `requests==2.31.0`

## Next Steps

1. **Run initial backfill** to populate historical data
2. **Set calendar reminder** to fetch new data quarterly
3. **Add more datasets** as needed (employment, inflation, etc.)
4. **Monitor logs** for any fetch failures

The OECD data fetching system is ready to use!
