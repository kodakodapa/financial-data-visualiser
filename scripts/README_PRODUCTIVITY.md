# Productivity Metrics

## Overview

The system provides comprehensive productivity metrics from two sources:
1. **Calculated metrics** derived from GDP per capita (quarterly)
2. **OECD API metrics** based on GDP per hour worked (annual)

This document covers the **calculated metrics**. For OECD API fetching, see [PRODUCTIVITY_DATA_FETCHING.md](../Documentation/PRODUCTIVITY_DATA_FETCHING.md).

## Metrics Added

### 1. productivity_growth
- **Description**: Quarterly change in GDP per capita (nominal)
- **Unit**: USD_PPP (US Dollars, Purchasing Power Parity)
- **Calculation**: GDP_per_capita(t) - GDP_per_capita(t-1)
- **Records**: 3,530 data points
- **Time Range**: 1995-Q2 to 2025-Q2
- **Source**: Calculated from OECD GDP per capita data

### 2. productivity_growth_pct
- **Description**: Quarterly percentage change in GDP per capita
- **Unit**: percent
- **Calculation**: ((GDP_per_capita(t) - GDP_per_capita(t-1)) / GDP_per_capita(t-1)) * 100
- **Records**: 3,530 data points
- **Time Range**: 1995-Q2 to 2025-Q2
- **Source**: Calculated from OECD GDP per capita data

## Country Coverage

All 50 countries/regions in the database:
- 30 OECD member countries
- 7 regional aggregates (G7, Euro area, EU27, etc.)
- 13 non-OECD economies

## Methodology

Productivity growth is calculated as the quarter-over-quarter change in GDP per capita. This measure serves as a proxy for labour productivity when employment/hours worked data is not available.

GDP per capita is a valid approximation because:
- It captures output per person in the economy
- It's internationally comparable (PPP-adjusted)
- It reflects economic efficiency and living standards

## Usage

### Command Line
```bash
# Calculate/recalculate productivity growth
python scripts/calculate_productivity_growth.py

# Dry run (preview without saving)
python scripts/calculate_productivity_growth.py --dry-run
```

### API Access

**List metrics:**
```
GET /api/metrics
```

**Get data for specific countries:**
```
GET /api/data?metric=productivity_growth&countries=United States,Canada
GET /api/data?metric=productivity_growth_pct&countries=United States,Canada
```

**Correlate with other metrics:**
```
GET /api/correlate?metric1=productivity_growth_pct&metric2=gdp_per_capita&countries=United States
```

## Example Data

**United States (Recent Quarters):**

| Period  | GDP/capita | Nominal Growth | % Growth |
|---------|------------|----------------|----------|
| 2025-Q2 | $73,236    | +$592          | +0.81%   |
| 2025-Q1 | $72,644    | -$209          | -0.29%   |
| 2024-Q4 | $72,853    | +$221          | +0.30%   |
| 2024-Q3 | $72,632    | +$444          | +0.62%   |
| 2024-Q2 | $72,188    | +$463          | +0.65%   |

## Comparison with OECD API Metrics

In addition to these calculated metrics, you can also fetch official OECD productivity data:

| Metric | Source | Frequency | Measure |
|--------|--------|-----------|---------|
| productivity_growth | Calculated | Quarterly | GDP per capita change |
| productivity_growth_pct | Calculated | Quarterly | GDP per capita % change |
| productivity_gdp_per_hour | OECD API | Annual | GDP per hour worked (levels) |
| productivity_growth_rate | OECD API | Annual | GDP per hour worked (growth %) |

**When to use each:**
- Use **calculated metrics** for quarterly analysis and when hours-worked data is unavailable
- Use **OECD API metrics** for official productivity comparisons and annual trends
- Calculated metrics are available immediately; OECD metrics require API fetching

See [PRODUCTIVITY_DATA_FETCHING.md](../Documentation/PRODUCTIVITY_DATA_FETCHING.md) for details on fetching OECD productivity data.

## Notes

- First quarter for each country has no growth data (needs previous quarter)
- Negative growth indicates productivity decline
- Data is automatically recalculated when GDP per capita is updated
- Both calculated metrics use the same source data for consistency
- OECD metrics provide more accurate labour productivity but are only annual
