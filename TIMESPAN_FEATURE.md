# Time Range Filtering Feature

## Overview

Added time range (timespan) filtering to the Economic Data Visualizer, allowing users to focus on specific time periods when analyzing data.

## What Was Added

### 1. HTML Controls ([web/index.html](web/index.html))

New time range control group with:
- **From** dropdown: Select start date
- **To** dropdown: Select end date
- **Reset** button: Clear date filters and show all data

### 2. JavaScript Functionality ([web/app.js](web/app.js))

**State Management:**
- `availablePeriods`: Array of all time periods for selected metric
- `startDate`: Selected start date filter
- `endDate`: Selected end date filter

**New Functions:**
- `loadAvailablePeriods()`: Fetches all available time periods for a metric
- `populateDateSelectors()`: Populates the date dropdowns with available periods
- `handleStartDateChange()`: Updates state when start date changes
- `handleEndDateChange()`: Updates state when end date changes
- `resetDates()`: Clears all date filters

**Updated Functions:**
- `handleMetricChange()`: Now also loads available periods when metric changes
- `loadTimeSeriesData()`: Includes `start_date` and `end_date` parameters in API calls

### 3. CSS Styling ([web/styles.css](web/styles.css))

**New Classes:**
- `.date-range-controls`: Flexbox container for date inputs and reset button
- `.date-input-group`: Container for label and select (one for each date)
- `.date-label`: Styling for "From:" and "To:" labels
- `.date-select`: Styling for date dropdown selectors

## How It Works

### User Flow

1. **Select a metric** (e.g., gdp_per_capita)
   - Available time periods are automatically loaded
   - Date dropdowns are populated with all quarters

2. **Choose time range** (optional)
   - Select start date from "From" dropdown
   - Select end date from "To" dropdown
   - Or leave both as "All data" to see full range

3. **Select countries** and click "Load Data"
   - Chart displays only data within selected time range
   - If no dates selected, shows all available data

4. **Reset filters**
   - Click "Reset" button to clear date selection
   - Reload data to see full time range again

### Technical Implementation

**API Integration:**
```javascript
// API call with date filters
GET /api/data?metric=gdp_per_capita&countries=Spain,France&start_date=2020-Q1&end_date=2021-Q4
```

**Backend Support:**
The Flask backend already supports `start_date` and `end_date` query parameters in:
- `/api/data` endpoint (time series)
- Filters are applied via SQL WHERE clauses

## Example Use Cases

### 1. Analyzing COVID-19 Impact
```
Metric: gdp_per_capita
Time Range: 2019-Q1 to 2021-Q4
Countries: Spain, Italy, France
Result: See GDP drops and recovery across European countries
```

### 2. Comparing Growth Rates
```
Metric: gdp_cumulative_return_per_capita
Time Range: 2010-Q1 to 2024-Q4
Countries: Poland, Estonia, Latvia
Result: Compare cumulative growth over past 15 years
```

### 3. Recent Trends
```
Metric: gdp_per_capita
Time Range: 2023-Q1 to 2025-Q3
Countries: All
Result: Focus on most recent economic performance
```

## Testing

Verified functionality with API tests:

```bash
# Test: Filter Spain's GDP from 2020-Q1 to 2021-Q4
curl "http://localhost:5000/api/data?metric=gdp_per_capita&countries=Spain&start_date=2020-Q1&end_date=2021-Q4"

# Result: Returns exactly 8 quarters (2020-Q1 through 2021-Q4)
```

## UI Features

- **Responsive dropdown design**: Matches existing control styling
- **Clear visual hierarchy**: Date controls grouped together
- **Reset convenience**: One-click to clear all date filters
- **All data default**: No filters applied unless user selects dates
- **Dynamic population**: Date options update based on selected metric

## Future Enhancements

Potential improvements:
- Preset ranges (e.g., "Last 5 years", "Last decade", "Pre/Post COVID")
- Date range validation (prevent end date before start date)
- Visual indicator when filters are active
- Remember last selected date range per metric
- Apply date filters to correlation view as well

## Files Modified

1. [web/index.html](web/index.html) - Added date range HTML controls
2. [web/app.js](web/app.js) - Added date filtering logic
3. [web/styles.css](web/styles.css) - Added date control styling

## How to Use

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Open browser**: http://localhost:5000

3. **Try it out**:
   - Select "gdp_per_capita" or "gdp_cumulative_return_per_capita"
   - Choose a start and/or end date
   - Select countries
   - Click "Load Data"
   - See filtered results!

The time range filtering feature is now fully functional and integrated with the existing visualization system!
