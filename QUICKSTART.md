# Quick Start Guide

## First Time Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database is already initialized and populated!**
   - Database: `data/economic_data.db`
   - Contains: 3,565 GDP per capita records
   - Countries: 30
   - Time range: 1995-Q1 to 2025-Q3

## Running the Application

Start the Flask server:
```bash
python app.py
```

Open your browser to: **http://localhost:5000**

## Using the Application

### View GDP Time Series

1. Select metric: **gdp_per_capita**
2. Click "Select All" to choose all countries (or select specific ones)
3. Click **Load Data**
4. Explore the interactive chart:
   - Hover over lines to see values
   - Zoom by dragging
   - Pan by holding shift and dragging
   - Double-click to reset zoom

### Compare Countries

- Select specific countries from the list
- Each country appears as a separate line in the chart
- Toggle countries on/off by clicking legend items

### Future: Correlation Analysis

When you add a second metric (e.g., employment rate):

1. Switch to **Correlation** view mode
2. Select first metric: **gdp_per_capita**
3. Select second metric: **employment_rate**
4. Select countries to analyze
5. Click **Load Data**
6. View scatter plot showing relationship between metrics

## Adding New Metrics

### Example: Adding Employment Data

1. Prepare CSV file: `employment-data.csv`
   ```csv
   Country,Quarter,Value
   United States,2020-Q1,60.5
   United States,2020-Q2,58.3
   ...
   ```

2. Ingest data:
   ```bash
   python scripts/ingest_data.py employment-data.csv employment_rate percent OECD
   ```

3. Refresh the web app - new metric appears in dropdown!

## Updating Existing Data

To add newer quarters to GDP data:

```bash
python scripts/extract_gdp_data.py data/raw/new-gdp-data.csv data/processed/new-gdp-extracted.csv
python scripts/ingest_data.py data/processed/new-gdp-extracted.csv gdp_per_capita USD_PPP OECD
```

Existing records are updated, new ones are added.

## Troubleshooting

### "Database not found" error
Run: `python scripts/init_database.py`

### No data appears
Check that database has records: `python scripts/ingest_data.py data/processed/gdp-data-extracted.csv gdp_per_capita USD_PPP OECD`

### Flask not found
Install dependencies: `pip install -r requirements.txt`

### Port 5000 already in use
Edit [app.py](app.py) and change the port in the last line:
```python
app.run(debug=True, port=5001)  # Changed from 5000 to 5001
```

## Next Steps

- Add more economic metrics (employment, inflation, etc.)
- Explore correlations between different indicators
- Export interesting findings
- Analyze trends and patterns

Enjoy exploring the economic data!
