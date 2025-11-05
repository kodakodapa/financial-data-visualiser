# Savings Rate Metrics - Quick Reference

## Overview

Track household savings both as percentage of income and in nominal per capita terms.

For comprehensive documentation, see [SAVINGS_RATE.md](../Documentation/SAVINGS_RATE.md)

## Metrics

| Metric | Source | Unit | Description |
|--------|--------|------|-------------|
| **savings_rate** | OECD API | percent | Household net saving rate (% of disposable income) |
| **disposable_income_per_capita** | OECD API | USD_PPP | Household net disposable income per person |
| **savings_per_capita** | Calculated | USD_PPP | Nominal savings amount per person |

## Quick Start

### 1. Fetch Data from OECD

```bash
# Fetch both required metrics
python scripts/fetch_oecd_data.py savings_rate --latest 10
python scripts/fetch_oecd_data.py disposable_income_per_capita --latest 10
```

### 2. Calculate Nominal Savings

```bash
# Calculate savings per capita
python scripts/calculate_savings_per_capita.py

# Preview without saving
python scripts/calculate_savings_per_capita.py --dry-run
```

### 3. Access via API

```bash
# Start server
python app.py

# Query data
curl "http://localhost:5000/api/data?metric=savings_rate&countries=United States"
curl "http://localhost:5000/api/data?metric=savings_per_capita&countries=United States"
```

## Formula

```
savings_per_capita = (savings_rate / 100) × disposable_income_per_capita
```

## Example

**United States, 2024-Q2:**
- Disposable income per capita: $56,234
- Savings rate: 8.2%
- **Savings per capita: $4,611**

## Data Availability

- **Frequency**: Quarterly
- **Coverage**: Most OECD countries
- **History**: Typically 1995+
- **Updates**: Quarterly with OECD releases

## Related Scripts

- `fetch_oecd_data.py` - Fetch latest data
- `backfill_oecd_data.py` - Fetch historical data
- `calculate_savings_per_capita.py` - Calculate nominal savings

## See Also

- [SAVINGS_RATE.md](../Documentation/SAVINGS_RATE.md) - Full documentation
- [OECD_DATA_FETCHING.md](../Documentation/OECD_DATA_FETCHING.md) - General OECD fetching guide
