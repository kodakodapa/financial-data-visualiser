# Rebase to Start Date Feature

## Overview

Added the ability to recalculate any metric's values to start at 100 from the selected start date. This makes it easy to compare relative growth across countries over a specific time period, regardless of their absolute values.

## What Was Added

### 1. HTML Control ([web/index.html](web/index.html))

New checkbox control:
- **Checkbox**: "Rebase to 100 at start date"
- **Help text**: Explains what the feature does
- Located between the time range controls and the Load Data button

### 2. JavaScript Functionality ([web/app.js](web/app.js))

**State Management:**
- `rebaseToStart`: Boolean flag indicating if rebase is enabled

**New Functions:**
- `handleRebaseChange()`: Updates state when checkbox is toggled
- `rebaseTimeSeries(data)`: Recalculates all values relative to the first data point

**Updated Functions:**
- `visualizeTimeSeries()`: Applies rebase transformation before charting if enabled
- Chart title and axis labels update to show when data is rebased

### 3. CSS Styling ([web/styles.css](web/styles.css))

**New Classes:**
- `.rebase-control`: Container for the checkbox and help text
- `.help-text`: Styling for explanatory text
- Checkbox styling with primary color accent

## How It Works

### Mathematical Calculation

When rebase is enabled, each value is recalculated as:

```
Rebased Value = (Current Value / First Value) × 100
```

**Example (Spain GDP):**
- Original Q1 2020: 42,152.2 → Rebased: 100.00
- Original Q2 2020: 34,642.7 → Rebased: 82.18 (82.18% of Q1 value)
- Original Q3 2020: 40,141.2 → Rebased: 95.23 (95.23% of Q1 value)
- Original Q4 2020: 40,423.9 → Rebased: 95.90 (95.90% of Q1 value)

### User Flow

1. **Select a metric** (e.g., gdp_per_capita)
2. **Set a start date** (e.g., 2020-Q1)
3. **Optionally set an end date** (e.g., 2021-Q4)
4. **Check "Rebase to 100 at start date"**
5. **Select countries** and click "Load Data"
6. **View the chart** with all countries starting at 100

The chart will show:
- Title: "gdp_per_capita Over Time (Rebased to 100 at 2020-Q1)"
- Y-axis: "gdp_per_capita (Index, base=100 at 2020-Q1)"
- All country lines starting at 100 at the selected start date

## Why This Is Useful

### 1. Compare Countries with Different Scales

**Without rebase:**
```
USA GDP: $60,000 per capita
Mexico GDP: $20,000 per capita
Hard to see which grew faster percentage-wise
```

**With rebase:**
```
USA: 100 → 110 (10% growth)
Mexico: 100 → 115 (15% growth)
Easy to see Mexico grew faster!
```

### 2. Focus on Specific Time Periods

**COVID-19 Impact Analysis:**
- Set start date: 2019-Q4 (pre-COVID)
- Set end date: 2022-Q4 (recovery period)
- Rebase to 100
- See which countries recovered better

**Post-Financial Crisis:**
- Set start date: 2008-Q4 (crisis bottom)
- Rebase to 100
- Compare recovery trajectories

### 3. Works with Any Metric

The rebase feature works with:
- **gdp_per_capita**: Compare absolute GDP growth
- **gdp_cumulative_return_per_capita**: Re-anchor already normalized data
- **Any future metrics**: Employment, inflation, etc.

## Important Notes

### Rebase Only Works When Start Date Is Set

- If no start date is selected, the checkbox has no effect
- This is intentional: rebasing requires a clear starting point
- The checkbox is always visible but only affects output when start date exists

### Rebase vs. Cumulative Return Metric

**Cumulative Return (pre-calculated metric):**
- Stored in database
- Always indexed to first available data point (e.g., 1995-Q1)
- Fixed baseline for all time ranges

**Rebase Feature (dynamic calculation):**
- Calculated on-the-fly in the frontend
- Can reindex to ANY date you choose
- Flexible baseline that changes with your selection

**Use Case Comparison:**
- "Show me GDP growth since 1995" → Use `gdp_cumulative_return_per_capita` metric
- "Show me GDP growth since COVID started (2020-Q1)" → Use `gdp_per_capita` with rebase

## Example Use Cases

### 1. COVID-19 Recovery Comparison
```
Metric: gdp_per_capita
Start Date: 2019-Q4
End Date: 2023-Q4
Rebase: ✓ Enabled
Countries: Spain, Italy, Germany, France
Result: See which European country recovered best
```

### 2. 2008 Financial Crisis Recovery
```
Metric: gdp_per_capita
Start Date: 2008-Q4
End Date: 2013-Q4
Rebase: ✓ Enabled
Countries: USA, Greece, Ireland, Spain
Result: Compare recovery speeds after crisis
```

### 3. Recent Growth Trends
```
Metric: gdp_per_capita
Start Date: 2020-Q1
End Date: 2025-Q3
Rebase: ✓ Enabled
Countries: Poland, Estonia, Latvia, Korea
Result: See which growing economies performed best recently
```

## Testing

Created [test_rebase.html](test_rebase.html) to verify the calculation:

**Test Data (Spain Q1 2020 = 42,152.2):**
- Q1 2020: 42,152.2 → 100.00 ✓
- Q2 2020: 34,642.7 → 82.18 ✓ (34642.7/42152.2 × 100)
- Q3 2020: 40,141.2 → 95.23 ✓ (40141.2/42152.2 × 100)
- Q4 2020: 40,423.9 → 95.90 ✓ (40423.9/42152.2 × 100)

All calculations verified correct!

## UI/UX Features

- **Clear labeling**: Checkbox text explains what it does
- **Help text**: Additional explanation below checkbox
- **Visual feedback**: Chart title updates to show rebase is active
- **Axis labels**: Y-axis shows "Index, base=100 at [date]"
- **No automatic application**: User must explicitly check the box
- **Works with existing features**: Combines with country selection and date filtering

## Technical Implementation

### Frontend Calculation (Client-Side)

The rebase is calculated in JavaScript after receiving data from the API:

```javascript
function rebaseTimeSeries(data) {
    return {
        ...data,
        data: data.data.map(countryData => {
            const baseValue = countryData.time_series[0].value;
            const rebasedSeries = countryData.time_series.map((point, index) => {
                if (index === 0) {
                    return { ...point, value: 100 };
                }
                return {
                    ...point,
                    value: (point.value / baseValue) * 100
                };
            });
            return { ...countryData, time_series: rebasedSeries };
        })
    };
}
```

**Why client-side?**
- No API changes needed
- Works with existing backend
- Instant recalculation when toggling checkbox
- Keeps backend simple and focused on data retrieval

## Files Modified

1. [web/index.html](web/index.html) - Added rebase checkbox and help text
2. [web/app.js](web/app.js) - Added rebase calculation and state management
3. [web/styles.css](web/styles.css) - Added rebase control styling

## How to Use

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Open browser**: http://localhost:5000

3. **Try it out**:
   - Select "gdp_per_capita"
   - Set start date: "2020-Q1"
   - Check "Rebase to 100 at start date"
   - Select multiple countries (e.g., Spain, Italy, France)
   - Click "Load Data"
   - See all countries start at 100 and diverge based on their relative growth!

4. **Compare with original**:
   - Uncheck the rebase box
   - Click "Load Data" again
   - See the absolute values instead

## Future Enhancements

Potential improvements:
- Add keyboard shortcut to toggle rebase (e.g., 'R' key)
- Remember rebase preference per metric
- Add "Growth Rate %" view mode (show percentage change per quarter)
- Export rebased data to CSV
- Add statistical summary (avg growth rate, volatility, etc.)

The rebase feature is now fully functional and ready to use for comparative analysis across time periods!
