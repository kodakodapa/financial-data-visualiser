// Economic Data Visualizer - Frontend Application

const API_BASE = 'http://localhost:5000/api';

// Application state
const state = {
    metrics: [],
    countries: [],
    availablePeriods: [],
    selectedMetric: null,
    selectedMetric2: null,
    selectedCountries: new Set(),
    startDate: null,
    endDate: null,
    rebaseToStart: false,
    viewMode: 'timeseries' // 'timeseries' or 'correlation'
};

// DOM Elements
const elements = {
    metricSelect: document.getElementById('metric-select'),
    metric2Select: document.getElementById('metric2-select'),
    countryList: document.getElementById('country-list'),
    selectAllBtn: document.getElementById('select-all-countries'),
    clearBtn: document.getElementById('clear-countries'),
    loadDataBtn: document.getElementById('load-data'),
    chart: document.getElementById('chart'),
    message: document.getElementById('message'),
    stats: document.getElementById('stats'),
    viewTimeseriesBtn: document.getElementById('view-timeseries'),
    viewCorrelationBtn: document.getElementById('view-correlation'),
    correlationControls: document.getElementById('correlation-controls'),
    startDateSelect: document.getElementById('start-date'),
    endDateSelect: document.getElementById('end-date'),
    resetDatesBtn: document.getElementById('reset-dates'),
    rebaseCheckbox: document.getElementById('rebase-to-start')
};

// Initialize the application
async function init() {
    setupEventListeners();
    await loadStats();
    await loadMetrics();
}

// Setup event listeners
function setupEventListeners() {
    elements.metricSelect.addEventListener('change', handleMetricChange);
    elements.metric2Select.addEventListener('change', handleMetric2Change);
    elements.selectAllBtn.addEventListener('click', selectAllCountries);
    elements.clearBtn.addEventListener('click', clearCountries);
    elements.loadDataBtn.addEventListener('click', loadData);
    elements.viewTimeseriesBtn.addEventListener('click', () => switchViewMode('timeseries'));
    elements.viewCorrelationBtn.addEventListener('click', () => switchViewMode('correlation'));
    elements.startDateSelect.addEventListener('change', handleStartDateChange);
    elements.endDateSelect.addEventListener('change', handleEndDateChange);
    elements.resetDatesBtn.addEventListener('click', resetDates);
    elements.rebaseCheckbox.addEventListener('change', handleRebaseChange);
}

// Switch view mode
function switchViewMode(mode) {
    state.viewMode = mode;

    if (mode === 'timeseries') {
        elements.viewTimeseriesBtn.classList.add('active');
        elements.viewCorrelationBtn.classList.remove('active');
        elements.correlationControls.style.display = 'none';
    } else {
        elements.viewTimeseriesBtn.classList.remove('active');
        elements.viewCorrelationBtn.classList.add('active');
        elements.correlationControls.style.display = 'block';
    }

    // Clear chart when switching modes
    Plotly.purge(elements.chart);
}

// Load database statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();

        elements.stats.innerHTML = `
            <strong>${stats.total_records.toLocaleString()}</strong> records |
            <strong>${stats.unique_metrics}</strong> metrics |
            <strong>${stats.unique_countries}</strong> countries |
            <strong>${stats.time_range.start}</strong> to <strong>${stats.time_range.end}</strong>
        `;
    } catch (error) {
        showMessage('Failed to load statistics', 'error');
    }
}

// Load available metrics
async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`);
        state.metrics = await response.json();

        // Populate metric select
        elements.metricSelect.innerHTML = '<option value="">Select a metric...</option>';
        elements.metric2Select.innerHTML = '<option value="">Select a metric...</option>';

        state.metrics.forEach(metric => {
            const option = document.createElement('option');
            option.value = metric.name;
            option.textContent = `${metric.name} (${metric.unit}) - ${metric.data_points} points`;

            elements.metricSelect.appendChild(option);
            elements.metric2Select.appendChild(option.cloneNode(true));
        });
    } catch (error) {
        showMessage('Failed to load metrics', 'error');
    }
}

// Handle metric selection change
async function handleMetricChange() {
    const metricName = elements.metricSelect.value;
    if (!metricName) return;

    state.selectedMetric = metricName;
    await loadCountries(metricName);
    await loadAvailablePeriods(metricName);
}

// Handle second metric selection change
function handleMetric2Change() {
    state.selectedMetric2 = elements.metric2Select.value;
}

// Load countries for selected metric
async function loadCountries(metricName) {
    try {
        const response = await fetch(`${API_BASE}/countries?metric=${metricName}`);
        state.countries = await response.json();

        // Populate country list with checkboxes
        elements.countryList.innerHTML = '';
        state.countries.forEach(country => {
            const div = document.createElement('div');
            div.className = 'country-item';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `country-${country.name}`;
            checkbox.value = country.name;
            checkbox.addEventListener('change', handleCountryChange);

            const label = document.createElement('label');
            label.htmlFor = `country-${country.name}`;
            label.textContent = `${country.name} (${country.data_points} points)`;

            div.appendChild(checkbox);
            div.appendChild(label);
            elements.countryList.appendChild(div);
        });
    } catch (error) {
        showMessage('Failed to load countries', 'error');
    }
}

// Load available time periods for a metric
async function loadAvailablePeriods(metricName) {
    try {
        const response = await fetch(`${API_BASE}/data?metric=${metricName}`);
        const data = await response.json();

        // Collect all unique periods
        const periods = new Set();
        data.data.forEach(countryData => {
            countryData.time_series.forEach(point => {
                periods.add(point.time_period);
            });
        });

        // Sort periods chronologically
        state.availablePeriods = Array.from(periods).sort();

        // Populate date selectors
        populateDateSelectors();
    } catch (error) {
        console.error('Failed to load available periods:', error);
    }
}

// Populate date selector dropdowns
function populateDateSelectors() {
    // Clear existing options except the first "All data" option
    elements.startDateSelect.innerHTML = '<option value="">All data</option>';
    elements.endDateSelect.innerHTML = '<option value="">All data</option>';

    state.availablePeriods.forEach(period => {
        const startOption = document.createElement('option');
        startOption.value = period;
        startOption.textContent = period;
        elements.startDateSelect.appendChild(startOption);

        const endOption = document.createElement('option');
        endOption.value = period;
        endOption.textContent = period;
        elements.endDateSelect.appendChild(endOption);
    });
}

// Handle start date change
function handleStartDateChange() {
    state.startDate = elements.startDateSelect.value || null;
}

// Handle end date change
function handleEndDateChange() {
    state.endDate = elements.endDateSelect.value || null;
}

// Reset date filters
function resetDates() {
    state.startDate = null;
    state.endDate = null;
    elements.startDateSelect.value = '';
    elements.endDateSelect.value = '';
}

// Handle rebase checkbox change
function handleRebaseChange() {
    state.rebaseToStart = elements.rebaseCheckbox.checked;
}

// Handle country checkbox change
function handleCountryChange(event) {
    const country = event.target.value;
    if (event.target.checked) {
        state.selectedCountries.add(country);
    } else {
        state.selectedCountries.delete(country);
    }
}

// Select all countries
function selectAllCountries() {
    const checkboxes = elements.countryList.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(cb => {
        cb.checked = true;
        state.selectedCountries.add(cb.value);
    });
}

// Clear all countries
function clearCountries() {
    const checkboxes = elements.countryList.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(cb => {
        cb.checked = false;
    });
    state.selectedCountries.clear();
}

// Load and visualize data
async function loadData() {
    if (!state.selectedMetric) {
        showMessage('Please select a metric', 'error');
        return;
    }

    if (state.selectedCountries.size === 0) {
        showMessage('Please select at least one country', 'error');
        return;
    }

    if (state.viewMode === 'correlation') {
        if (!state.selectedMetric2) {
            showMessage('Please select a second metric for correlation', 'error');
            return;
        }
        await loadCorrelationData();
    } else {
        await loadTimeSeriesData();
    }
}

// Load time series data
async function loadTimeSeriesData() {
    try {
        showMessage('Loading data...', 'info');
        elements.loadDataBtn.disabled = true;

        const countries = Array.from(state.selectedCountries).join(',');
        let url = `${API_BASE}/data?metric=${state.selectedMetric}&countries=${countries}`;

        // Add date filters if set
        if (state.startDate) {
            url += `&start_date=${state.startDate}`;
        }
        if (state.endDate) {
            url += `&end_date=${state.endDate}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.error) {
            showMessage(data.error, 'error');
            return;
        }

        visualizeTimeSeries(data);
        hideMessage();
    } catch (error) {
        showMessage(`Failed to load data: ${error.message}`, 'error');
    } finally {
        elements.loadDataBtn.disabled = false;
    }
}

// Load correlation data
async function loadCorrelationData() {
    try {
        showMessage('Loading correlation data...', 'info');
        elements.loadDataBtn.disabled = true;

        const countries = Array.from(state.selectedCountries).join(',');
        const response = await fetch(
            `${API_BASE}/correlate?metric1=${state.selectedMetric}&metric2=${state.selectedMetric2}&countries=${countries}`
        );
        const data = await response.json();

        if (data.error) {
            showMessage(data.error, 'error');
            return;
        }

        visualizeCorrelation(data);
        hideMessage();
    } catch (error) {
        showMessage(`Failed to load correlation data: ${error.message}`, 'error');
    } finally {
        elements.loadDataBtn.disabled = false;
    }
}

// Rebase time series data to start at 100 from the first data point
function rebaseTimeSeries(data) {
    return {
        ...data,
        data: data.data.map(countryData => {
            if (countryData.time_series.length === 0) {
                return countryData;
            }

            // Get the first value as the base
            const baseValue = countryData.time_series[0].value;

            // Recalculate all values relative to the base, indexed to 100
            const rebasedSeries = countryData.time_series.map((point, index) => {
                if (index === 0) {
                    return { ...point, value: 100 };
                }
                // Calculate cumulative return from the base
                const cumulativeReturn = (point.value / baseValue) * 100;
                return { ...point, value: cumulativeReturn };
            });

            return {
                ...countryData,
                time_series: rebasedSeries
            };
        })
    };
}

// Normalize time series data to handle missing quarters
function normalizeTimeSeries(data) {
    // Collect all unique time periods across all countries
    const allPeriods = new Set();
    data.data.forEach(countryData => {
        countryData.time_series.forEach(point => {
            allPeriods.add(point.time_period);
        });
    });

    // Sort periods chronologically
    const sortedPeriods = Array.from(allPeriods).sort();

    // Normalize each country's data to include all periods
    const normalizedData = {
        ...data,
        data: data.data.map(countryData => {
            // Create a map of period -> value for quick lookup
            const periodMap = new Map();
            countryData.time_series.forEach(point => {
                periodMap.set(point.time_period, point.value);
            });

            // Build normalized time series with null for missing periods
            const normalizedSeries = sortedPeriods.map(period => ({
                time_period: period,
                value: periodMap.has(period) ? periodMap.get(period) : null
            }));

            return {
                ...countryData,
                time_series: normalizedSeries
            };
        })
    };

    return normalizedData;
}

// Visualize time series data
function visualizeTimeSeries(data) {
    // Normalize data to handle missing quarters
    let displayData = normalizeTimeSeries(data);

    // Apply rebase if enabled
    if (state.rebaseToStart && state.startDate) {
        displayData = rebaseTimeSeries(displayData);
    }

    const traces = displayData.data.map(countryData => ({
        x: countryData.time_series.map(d => d.time_period),
        y: countryData.time_series.map(d => d.value),
        type: 'scatter',
        mode: 'lines+markers',
        name: countryData.country,
        line: { width: 2 },
        marker: { size: 4 },
        connectgaps: false  // Don't connect lines across missing data
    }));

    // Update title and axis labels based on rebase status
    const isRebased = state.rebaseToStart && state.startDate;
    const chartTitle = isRebased
        ? `${data.metric} Over Time (Rebased to 100 at ${state.startDate})`
        : `${data.metric} Over Time`;
    const yAxisTitle = isRebased
        ? `${data.metric} (Index, base=100 at ${state.startDate})`
        : `${data.metric} (${data.unit || ''})`;

    const layout = {
        title: chartTitle,
        xaxis: {
            title: 'Time Period',
            tickangle: -45
        },
        yaxis: {
            title: yAxisTitle
        },
        hovermode: 'closest',
        showlegend: true,
        legend: {
            orientation: 'v',
            x: 1.02,
            y: 1
        },
        margin: {
            l: 80,
            r: 150,
            t: 80,
            b: 100
        }
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
    };

    Plotly.newPlot(elements.chart, traces, layout, config);
}

// Visualize correlation data
function visualizeCorrelation(data) {
    const traces = data.data.map(countryData => ({
        x: countryData.data_points.map(d => d.value1),
        y: countryData.data_points.map(d => d.value2),
        type: 'scatter',
        mode: 'markers',
        name: countryData.country,
        marker: { size: 8 },
        text: countryData.data_points.map(d => d.time_period),
        hovertemplate: '<b>%{fullData.name}</b><br>' +
                      `${data.metric1.name}: %{x}<br>` +
                      `${data.metric2.name}: %{y}<br>` +
                      'Period: %{text}<extra></extra>'
    }));

    const layout = {
        title: `Correlation: ${data.metric1.name} vs ${data.metric2.name}`,
        xaxis: {
            title: `${data.metric1.name} (${data.metric1.unit || ''})`
        },
        yaxis: {
            title: `${data.metric2.name} (${data.metric2.unit || ''})`
        },
        hovermode: 'closest',
        showlegend: true,
        legend: {
            orientation: 'v',
            x: 1.02,
            y: 1
        },
        margin: {
            l: 80,
            r: 150,
            t: 80,
            b: 80
        }
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
    };

    Plotly.newPlot(elements.chart, traces, layout, config);
}

// Show message
function showMessage(text, type = 'info') {
    elements.message.textContent = text;
    elements.message.className = `message ${type}`;
}

// Hide message
function hideMessage() {
    elements.message.className = 'message';
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
