# Hours Worked Data

This document describes the hours worked datasets added to the financial data visualizer.

## Available Datasets

### 1. Annual Hours Worked (`hours_worked_annual`)
- **Description**: Average annual hours actually worked per worker
- **Unit**: hours per year
- **Frequency**: Annual
- **Source**: OECD Hours Worked dataset (DSD_HW@DF_AVG_ANN_HRS_WKD)
- **Coverage**: All OECD countries and selected non-OECD economies

This metric represents the total number of hours actually worked per year divided by the average number of people in employment per year. It provides a comprehensive view of labor intensity across countries.

### 2. Weekly Hours Worked by Age Group

The OECD provides average usual weekly hours worked broken down by age groups:

#### `hours_worked_weekly_age_15_24`
- **Description**: Average usual weekly hours worked, age 15-24 years
- **Unit**: hours per week
- **Age Group**: 15-24 years

#### `hours_worked_weekly_age_25_54`
- **Description**: Average usual weekly hours worked, age 25-54 years
- **Unit**: hours per week
- **Age Group**: 25-54 years (prime working age)

#### `hours_worked_weekly_age_55_64`
- **Description**: Average usual weekly hours worked, age 55-64 years
- **Unit**: hours per week
- **Age Group**: 55-64 years (pre-retirement)

#### `hours_worked_weekly_age_65_plus`
- **Description**: Average usual weekly hours worked, age 65+ years
- **Unit**: hours per week
- **Age Group**: 65 years and over

#### `hours_worked_weekly_total`
- **Description**: Average usual weekly hours worked, all ages
- **Unit**: hours per week
- **Age Group**: Total (all ages)

**Source**: OECD Hours Worked dataset (DSD_HW@DF_AVG_USL_WK_WKD)

## Usage

### Fetching Data

To fetch hours worked data, use the `fetch_oecd_data.py` script:

```bash
# Fetch annual hours worked for all countries
python scripts/fetch_oecd_data.py hours_worked_annual --latest 5

# Fetch weekly hours for specific age group
python scripts/fetch_oecd_data.py hours_worked_weekly_age_25_54 --latest 3

# Fetch all hours worked datasets
python scripts/fetch_oecd_data.py hours_worked_annual hours_worked_weekly_total --latest 2

# Dry run to preview data without saving
python scripts/fetch_oecd_data.py hours_worked_annual --latest 1 --dry-run
```

### Available Age Groups

The age breakdown follows standard OECD demographic categories:
- **15-24**: Youth workers, early career
- **25-54**: Prime working age population
- **55-64**: Pre-retirement age group
- **65+**: Post-retirement age workers

These breakdowns allow analysis of:
- How working hours vary across life stages
- Youth vs. senior employment patterns
- Part-time vs. full-time work by age
- Retirement transition patterns

## Data Limitations

### Migration Status Not Available

**Important Note**: While extensive research was conducted to find hours worked data broken down by migration status (foreign-born vs. native-born), this breakdown is **not available** in the OECD SDMX API.

The OECD maintains several migration-related databases:
- Database on Immigrants in OECD Countries (DIOC)
- International Migration Database
- Migration Demography Database

However, these databases provide:
- Employment rates by migration status
- Labor force participation by migration status
- Population stocks by birthplace

But they **do not include** hours worked broken down by migration status at the individual level through the SDMX API.

### Alternative Approaches for Migration Analysis

If you need to analyze hours worked by migration status, consider:

1. **Cross-referencing datasets**: Combine employment rates by migration status with total hours worked
2. **Alternative data sources**: National labor force surveys (e.g., Current Population Survey in the US)
3. **OECD publications**: The OECD's migration reports may contain aggregate statistics not available via API
4. **Research databases**: Academic datasets like the Integrated Public Use Microdata Series (IPUMS) International

## Technical Details

### SDMX Endpoints

The configurations use the following OECD SDMX API endpoints:

**Annual Hours**:
```
OECD.ELS.SAE,DSD_HW@DF_AVG_ANN_HRS_WKD,1.0
```

**Weekly Hours with Age Breakdown**:
```
OECD.ELS.SAE,DSD_HW@DF_AVG_USL_WK_WKD,1.0
```

### Data Selection Patterns

The data selection follows SDMX dimension codes:
- **Frequency**: `A` (Annual) for annual data, omitted for weekly data
- **Reference Area**: Country codes (e.g., USA, GBR, DEU)
- **Age**: `Y15T24`, `Y25T54`, `Y55T64`, `Y_GE65`, `_T` (total)
- **Sex**: `_T` (total, both sexes)

### Configuration Structure

Each dataset configuration in `data_configs.py` includes:
- `dataset_path`: OECD SDMX endpoint identifier
- `data_selection_template`: Dimension pattern with `{countries}` placeholder
- `countries`: List of country codes to query
- `metric_name`: Internal identifier for the database
- `unit`: Measurement unit
- `source`: Data provider (OECD)
- `description`: Human-readable description

## API Client

The existing OECD API client (`scripts/oecd/`) handles all data fetching:
- **api_client.py**: HTTP requests with retry logic and error handling
- **query_builder.py**: Constructs SDMX API URLs with proper dimension encoding
- **parser.py**: Parses CSV responses and validates data
- **fetcher.py**: Orchestrates the complete fetch-parse-store workflow

No changes to the API client were needed to support hours worked data.

## References

- [OECD Hours Worked Indicator](https://data.oecd.org/emp/hours-worked.htm)
- [OECD Data Explorer](https://data-explorer.oecd.org/)
- [OECD SDMX API Documentation](https://data.oecd.org/api/)
- [OECD Migration Databases](https://www.oecd.org/en/data/datasets/oecd-databases-on-migration.html)

## Examples

### Comparing Hours Worked Across Age Groups

```python
# Fetch data for all age groups for USA
python scripts/fetch_oecd_data.py \
  hours_worked_weekly_age_15_24 \
  hours_worked_weekly_age_25_54 \
  hours_worked_weekly_age_55_64 \
  hours_worked_weekly_age_65_plus \
  --latest 10
```

### Analyzing Long-term Trends

```python
# Fetch 20 years of annual hours worked data
python scripts/fetch_oecd_data.py hours_worked_annual --latest 20
```

### Cross-country Comparison

The data automatically includes all OECD countries, so you can compare:
- Work-life balance policies (shorter hours in some European countries)
- Cultural attitudes toward work (longer hours in some Asian countries)
- Economic structure (service vs. manufacturing economies)

## Future Enhancements

Potential additions:
1. **Sex breakdown**: Add separate configurations for male/female hours worked
2. **Employment status**: Self-employed vs. employees
3. **Full-time vs. part-time**: Separate tracking of work arrangements
4. **Derived metrics**: Calculate annualized hours from weekly data by age group

Note: These enhancements would require additional research into available SDMX dimensions.
