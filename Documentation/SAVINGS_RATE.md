# Savings Rate Metrics

## Overview

The system provides comprehensive household savings metrics, both as percentage rates and nominal per capita values. These metrics help analyze how much households are saving relative to their income and the actual dollar amounts being saved.

## Available Metrics

### 1. savings_rate
**Household Net Saving Rate (Percentage)**

- **Source**: OECD National Accounts
- **Unit**: percent (% of disposable income)
- **Frequency**: Quarterly
- **Description**: Household net saving as a percentage of household net disposable income
- **Dataset**: OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE7_HHSAV,1.0

**Interpretation:**
- Positive values indicate households are saving money
- Negative values indicate households are dis-saving (spending more than their income)
- Typical range: 0-20% for most developed economies
- Higher rates suggest stronger household financial buffers

### 2. disposable_income_per_capita
**Household Net Disposable Income Per Capita**

- **Source**: OECD National Accounts
- **Unit**: USD_PPP (Purchasing Power Parity)
- **Frequency**: Quarterly
- **Description**: Household net disposable income per person, PPP-adjusted
- **Dataset**: OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA_INCOME_CAPITA,1.1

**Interpretation:**
- Represents the average income available for spending or saving after taxes
- PPP-adjusted for international comparability
- Includes wages, investment income, transfers, minus taxes
- Base metric for calculating nominal savings

### 3. savings_per_capita
**Nominal Savings Per Capita (Calculated)**

- **Source**: Calculated from savings_rate and disposable_income_per_capita
- **Unit**: USD_PPP
- **Frequency**: Quarterly
- **Description**: Actual dollar amount saved per person per quarter
- **Calculation**: (savings_rate / 100) × disposable_income_per_capita

**Interpretation:**
- Shows the actual nominal amount saved per person
- Useful for comparing absolute saving behavior across countries
- Can be aggregated or compared with other expenditure categories
- More intuitive than percentages for some analyses

## Methodology

### Savings Rate Definition

The OECD defines household net saving rate as:
```
Savings Rate = (Household Net Disposable Income - Household Final Consumption) / Household Net Disposable Income × 100
```

### Components

**Household Net Disposable Income includes:**
- Wages and salaries
- Self-employment income
- Property income (interest, dividends, rent)
- Social benefits
- Other current transfers
- Minus: Current taxes on income and wealth
- Minus: Social contributions

**Household Final Consumption includes:**
- Goods and services purchased by households
- Imputed rent for owner-occupied housing
- FISIM (Financial Intermediation Services Indirectly Measured)

### Calculation of Nominal Savings

The nominal savings per capita is calculated as:
```
savings_per_capita = (savings_rate / 100) × disposable_income_per_capita
```

**Example:**
- Disposable income per capita: $50,000 per quarter
- Savings rate: 8.5%
- Savings per capita: $50,000 × 0.085 = $4,250 per quarter

## Usage

### 1. Fetching Data from OECD

```bash
# Fetch savings rate (% of disposable income)
python scripts/fetch_oecd_data.py savings_rate --latest 10

# Fetch disposable income per capita
python scripts/fetch_oecd_data.py disposable_income_per_capita --latest 10

# Fetch both together
python scripts/fetch_oecd_data.py savings_rate --latest 10 && \
python scripts/fetch_oecd_data.py disposable_income_per_capita --latest 10
```

### 2. Backfill Historical Data

```bash
# Backfill savings rate from 1995
python scripts/backfill_oecd_data.py savings_rate \
    --start 1995-Q1 \
    --end 2024-Q4 \
    --batch-years 5

# Backfill disposable income
python scripts/backfill_oecd_data.py disposable_income_per_capita \
    --start 1995-Q1 \
    --end 2024-Q4 \
    --batch-years 5
```

### 3. Calculate Nominal Savings Per Capita

After fetching both required metrics:

```bash
# Calculate savings per capita
python scripts/calculate_savings_per_capita.py

# Dry run to preview calculations
python scripts/calculate_savings_per_capita.py --dry-run
```

### 4. Access via API

```bash
# Start the Flask server
python app.py

# Query savings rate
curl "http://localhost:5000/api/data?metric=savings_rate&countries=United States,Germany"

# Query disposable income
curl "http://localhost:5000/api/data?metric=disposable_income_per_capita&countries=United States,Germany"

# Query nominal savings
curl "http://localhost:5000/api/data?metric=savings_per_capita&countries=United States,Germany"

# Correlate savings rate with GDP
curl "http://localhost:5000/api/correlate?metric1=savings_rate&metric2=gdp_per_capita&countries=United States"
```

## Example Data

**United States (Recent Quarters):**

| Period | Disposable Income | Savings Rate | Savings Per Capita |
|--------|------------------|--------------|-------------------|
| 2024-Q2 | $56,234 | 8.2% | $4,611 |
| 2024-Q1 | $55,890 | 8.5% | $4,751 |
| 2023-Q4 | $55,432 | 7.9% | $4,379 |
| 2023-Q3 | $54,821 | 8.1% | $4,440 |

**International Comparison (2024-Q2):**

| Country | Savings Rate | Disposable Income | Savings Per Capita |
|---------|--------------|-------------------|-------------------|
| Switzerland | 18.5% | $62,400 | $11,544 |
| Germany | 11.2% | $48,300 | $5,410 |
| United States | 8.2% | $56,234 | $4,611 |
| United Kingdom | 6.8% | $45,100 | $3,067 |

## Country Coverage

The OECD provides savings rate and disposable income data for:
- Most OECD member countries (coverage varies by country)
- Some data availability for Euro area and EU aggregates
- Historical data typically from 1995+ for most countries
- Quarterly frequency for both metrics

**Note:** Coverage is generally better for:
- G7 countries
- European Union countries
- Other high-income OECD members

Some emerging economy data may be limited or unavailable.

## Data Quality Considerations

### Observation Status Filtering

Like other OECD datasets, savings data is filtered by observation status:
- **Included by default**: Normal (A), Estimated (E)
- **Excluded by default**: Provisional (P), Forecast (F)

To include provisional data:
```bash
python scripts/fetch_oecd_data.py savings_rate --latest 2 --include-provisional
```

### Data Revisions

OECD revises national accounts data regularly:
- Initial estimates are published quarterly
- Revisions occur as more complete data becomes available
- Annual benchmarking can cause significant revisions
- The upsert mechanism automatically handles revisions

### Negative Savings Rates

Some countries occasionally show negative savings rates:
- Indicates households are dis-saving (consuming more than income)
- Can occur during economic crises or with credit expansion
- May reflect measurement issues in some cases
- Should be analyzed in context of other economic indicators

### Seasonal Patterns

Savings rates often show seasonal patterns:
- Higher in certain quarters (e.g., after bonuses)
- Lower around holidays or vacation periods
- Consider using moving averages for trend analysis
- Year-over-year comparisons help remove seasonality

## Analysis Use Cases

### 1. Financial Stability Analysis
Track household financial buffers and resilience:
```sql
SELECT country, time_period, value as savings_rate
FROM economic_data
WHERE metric_name = 'savings_rate'
  AND country IN ('United States', 'Germany', 'Japan')
ORDER BY time_period DESC
```

### 2. Consumption Patterns
Analyze propensity to save vs. consume:
```sql
SELECT
    country,
    time_period,
    (100 - value) as consumption_rate,
    value as savings_rate
FROM economic_data
WHERE metric_name = 'savings_rate'
```

### 3. Cross-Country Comparisons
Compare absolute saving behavior:
```sql
SELECT
    country,
    AVG(value) as avg_savings_per_capita
FROM economic_data
WHERE metric_name = 'savings_per_capita'
  AND time_period >= '2020-Q1'
GROUP BY country
ORDER BY avg_savings_per_capita DESC
```

### 4. Trend Analysis
Identify structural shifts in saving behavior:
```sql
SELECT
    strftime('%Y', time_period) as year,
    AVG(value) as avg_savings_rate
FROM economic_data
WHERE metric_name = 'savings_rate'
  AND country = 'United States'
GROUP BY year
ORDER BY year
```

## Relationship to Other Metrics

### Savings vs. GDP Per Capita
Higher GDP per capita often correlates with higher nominal savings (but not necessarily higher rates)

### Savings vs. Income Growth
Rising disposable income may lead to higher savings rates (if consumption doesn't increase proportionally)

### Savings vs. Interest Rates
Higher interest rates may encourage saving, though the relationship is complex

### Savings vs. Productivity
Countries with higher productivity growth may see different saving patterns

## References

- **OECD National Accounts**: Primary source for all household sector data
- **OECD Economic Outlook**: Analysis of savings trends and forecasts
- **OECD Household Dashboard**: Interactive visualization of household metrics
- **SNA 2008**: System of National Accounts methodology

## Troubleshooting

### No Data After Calculation

If `calculate_savings_per_capita.py` returns 0 records:
1. Verify both required metrics are present:
   ```sql
   SELECT DISTINCT metric_name FROM economic_data
   WHERE metric_name IN ('savings_rate', 'disposable_income_per_capita')
   ```
2. Check if countries and time periods match:
   ```sql
   SELECT COUNT(*) FROM economic_data WHERE metric_name = 'savings_rate'
   SELECT COUNT(*) FROM economic_data WHERE metric_name = 'disposable_income_per_capita'
   ```
3. Fetch the data if missing (see Usage section above)

### Different Data Availability

If savings_rate has more/fewer records than disposable_income_per_capita:
- OECD updates datasets at different times
- Some countries may have one metric but not the other
- Calculation only works for matching country-period pairs
- This is expected and not an error

### API Access Issues

If you get 403 errors when fetching:
- Check network/firewall restrictions
- Verify OECD API accessibility
- Try with a browser to diagnose the issue
- Consider fetching from OECD Data Explorer manually if needed
