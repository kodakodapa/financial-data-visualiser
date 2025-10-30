# Economic Data Visualizer

An interactive web application for exploring and analyzing economic data with support for time series visualization and metric correlations.

## Features

- **Multi-dimensional Data Storage**: SQLite database supporting multiple economic metrics
- **Interactive Visualizations**: Line charts, scatter plots, and correlation analysis using Plotly.js
- **Data Upserts**: Easy updates to existing data or addition of new metrics
- **On-demand Correlations**: Explore relationships between different economic indicators
- **Simple & Performant**: Lightweight Flask backend with no complex build tools

## Project Structure

```
financial-data-visualiser/
├── data/
│   ├── raw/                        # Original OECD CSV files
│   ├── processed/                  # Cleaned/extracted CSV files
│   └── economic_data.db            # SQLite database
├── scripts/
│   ├── extract_gdp_data.py         # Extract data from raw OECD files
│   ├── analyze_gdp_completeness.py # Analyze data completeness
│   ├── init_database.py            # Initialize database schema
│   └── ingest_data.py              # Ingest CSV data into database
├── web/
│   ├── index.html                  # Main UI
│   ├── app.js                      # Frontend application
│   └── styles.css                  # Styling
├── app.py                          # Flask backend API
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python scripts/init_database.py
```

### 3. Ingest Data

For GDP data (already extracted):

```bash
python scripts/ingest_data.py data/processed/gdp-data-extracted.csv gdp_per_capita USD_PPP OECD
```

For new OECD data files, first extract:

```bash
python scripts/extract_gdp_data.py data/raw/your-data.csv data/processed/your-data-extracted.csv
python scripts/ingest_data.py data/processed/your-data-extracted.csv metric_name unit source
```

### 4. Run the Application

```bash
python app.py
```

Then open your browser to: http://localhost:5000

## Usage

### Viewing Time Series Data

1. Select a metric from the dropdown
2. Select one or more countries (use "Select All" or individual checkboxes)
3. Click "Load Data"
4. Interact with the chart: zoom, pan, hover for details

### Analyzing Correlations

1. Click the "Correlation" view mode button
2. Select the first metric
3. Select the second metric to correlate against
4. Select countries to analyze
5. Click "Load Data"
6. View scatter plots showing the relationship between the two metrics

## Adding New Metrics

To add a new economic metric:

1. **Prepare your CSV file** with columns: `Country`, `Quarter` (or `TIME_PERIOD`), `Value`

2. **Ingest the data**:
   ```bash
   python scripts/ingest_data.py your-file.csv metric_name unit source
   ```

   Example:
   ```bash
   python scripts/ingest_data.py employment-data.csv employment_rate percent OECD
   ```

3. **Refresh the web app** - new metrics appear automatically in the dropdown

## Updating Existing Data

The ingestion script supports upserts (insert or update). To update existing data:

```bash
python scripts/ingest_data.py updated-data.csv existing_metric_name unit source
```

Existing records (same country + time period + metric) will be updated with new values.

## API Endpoints

The Flask backend provides these REST API endpoints:

- `GET /api/stats` - Database statistics
- `GET /api/metrics` - List all available metrics
- `GET /api/countries?metric=<name>` - List countries for a metric
- `GET /api/data?metric=<name>&countries=<list>` - Get time series data
- `GET /api/correlate?metric1=<name>&metric2=<name>&countries=<list>` - Correlate two metrics

## Data Analysis Scripts

### Extract GDP Data
```bash
python scripts/extract_gdp_data.py [input.csv] [output.csv]
```

### Analyze Data Completeness
```bash
python scripts/analyze_gdp_completeness.py [data-file.csv]
```

Shows:
- Countries with complete data
- Countries with missing quarters
- Coverage percentages
- Missing quarter details

## Technology Stack

- **Backend**: Python 3, Flask, SQLite
- **Frontend**: Vanilla JavaScript (ES6 modules), HTML5, CSS3
- **Visualization**: Plotly.js
- **Storage**: SQLite database (file-based, version-controllable)

## Performance Characteristics

- Database size: ~80KB for 3,565 GDP records
- Expected max: ~2-3MB for 20 metrics at 80K total rows
- Query performance: <50ms for typical time series queries
- Supports up to millions of rows before optimization needed

## Future Enhancements

- Statistical analysis (correlation coefficients, p-values)
- Export charts and data to CSV/PNG
- Moving averages and growth rate calculations
- Multiple metric comparisons (3+ metrics on same chart)
- Heatmap visualizations for country comparisons
- Date range filtering

## License

MIT
