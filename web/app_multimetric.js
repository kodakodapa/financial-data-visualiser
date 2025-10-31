// Economic Data Visualizer - Frontend Application (Multi-metric Support)

const API_BASE = 'http://localhost:5000/api';

// Application state
const state = {
    metrics: [],
    countries: [],
    availablePeriods: [],
    selectedMetrics: new Set(),
    selectedMetric2: null,
    selectedCountries: new Set(),
    startDate: null,
    endDate: null,
    rebaseToStart: false,
    viewMode: 'timeseries' // 'timeseries' or 'correlation'
};

// DOM Elements
const elements = {
    metricList: document.getElementById('metric-list'),
    selectAllMetricsBtn: document.getElementById('select-all-metrics'),
    clearMetricsBtn: document.getElementById('clear-metrics'),
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
    try {
        await loadMetrics();
        setupEventListeners();
    } catch (error) {
        showMessage('Failed to initialize application: ' + error.message, 'error');
    }
}

// Setup event listeners
function setupEventListeners() {
    elements.selectAllMetricsBtn.addEventListener('click', selectAllMetrics);
    elements.clearMetricsBtn.addEventListener('click', clearMetrics);
    elements.selectAllBtn.addEventListener('click', selectAllCountries);
    elements.clearBtn.addEventListener('click', clearCountries);
    elements.loadDataBtn.addEventListener('click', loadData);
    elements.viewTimeseriesBtn.addEventListener('click', () => switchViewMode('timeseries'));
    elements.viewCorrelationBtn.addEventListener('click', () => switchViewMode('correlation'));
    elements.startDateSelect.addEventListener('change', handleStartDateChange);
    elements.endDateSelect.addEventListener('change', handleEndDateChange);
    elements.resetDatesBtn.addEventListener('click', resetDateRange);
    elements.rebaseCheckbox.addEventListener('change', handleRebaseChange);

    if (elements.metric2Select) {
        elements.metric2Select.addEventListener('change', handleMetric2Change);
    }
}

// Load available metrics
async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`);
        state.metrics = await response.json();

        // Populate metric list with checkboxes
        elements.metricList.innerHTML = '';
        state.metrics.forEach(metric => {
            const div = document.createElement('div');
            div.className = 'metric-item';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `metric-${metric.name}`;
            checkbox.value = metric.name;
            checkbox.addEventListener('change', handleMetricChange);

            const label = document.createElement('label');
            label.htmlFor = `metric-${metric.name}`;
            label.textContent = `${metric.name} (${metric.unit || ''})`;

            div.appendChild(checkbox);
            div.appendChild(label);
            elements.metricList.appendChild(div);
        });

        // Also populate metric2 select for correlation mode
        if (elements.metric2Select) {
            elements.metric2Select.innerHTML = '<option value="">Select metric...</option>';
            state.metrics.forEach(metric => {
                const option = document.createElement('option');
                option.value = metric.name;
                option.textContent = `${metric.name} (${metric.unit || ''})`;
                elements.metric2Select.appendChild(option);
            });
        }
    } catch (error) {
        showMessage('Failed to load metrics: ' + error.message, 'error');
    }
}

// Handle metric checkbox change
async function handleMetricChange(event) {
    const metric = event.target.value;
    if (event.target.checked) {
        state.selectedMetrics.add(metric);
    } else {
        state.selectedMetrics.delete(metric);
    }

    // Reload countries and periods when metrics change
    if (state.selectedMetrics.size > 0) {
        await loadCountries();
        await loadAvailablePeriods();
    }
}

// Select all metrics
function selectAllMetrics() {
    const checkboxes = elements.metricList.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(cb => {
        cb.checked = true;
        state.selectedMetrics.add(cb.value);
    });
    loadCountries();
    loadAvailablePeriods();
}

// Clear all metrics
function clearMetrics() {
    const checkboxes = elements.metricList.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(cb => {
        cb.checked = false;
    });
    state.selectedMetrics.clear();
    elements.countryList.innerHTML = 'Select a metric first';
}

// Load countries for selected metrics
async function loadCountries() {
    if (state.selectedMetrics.size === 0) {
        elements.countryList.innerHTML = 'Select a metric first';
        return;
    }

    try {
        // Get countries that have data for ALL selected metrics
        const countrySets = await Promise.all(
            Array.from(state.selectedMetrics).map(async metric => {
                const response = await fetch(`${API_BASE}/countries?metric=${metric}`);
                const countries = await response.json();
                return new Set(countries.map(c => c.name));
            })
        );

        // Find intersection of all country sets
        const allCountries = Array.from(countrySets[0]).filter(country =>
            countrySets.every(set => set.has(country))
        ).sort();

        state.countries = allCountries.map(name => ({ name }));

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
            label.textContent = country.name;

            div.appendChild(checkbox);
            div.appendChild(label);
            elements.countryList.appendChild(div);
        });
    } catch (error) {
        showMessage('Failed to load countries: ' + error.message, 'error');
    }
}

// Load available periods for selected metrics
async function loadAvailablePeriods() {
    if (state.selectedMetrics.size === 0) return;

    try {
        const firstMetric = Array.from(state.selectedMetrics)[0];
        const response = await fetch(`${API_BASE}/data?metric=${firstMetric}`);
        const data = await response.json();

        const periodsSet = new Set();
        data.data.forEach(countryData => {
            countryData.time_series.forEach(point => {
                periodsSet.add(point.time_period);
            });
        });

        state.availablePeriods = Array.from(periodsSet).sort();

        // Populate date selects
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
    } catch (error) {
        console.error('Failed to load periods:', error);
    }
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
    if (state.selectedMetrics.size === 0) {
        showMessage('Please select at least one metric', 'error');
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

// Load time series data for multiple metrics
async function loadTimeSeriesData() {
    try {
        showMessage('Loading data...', 'info');
        elements.loadDataBtn.disabled = true;

        const countries = Array.from(state.selectedCountries).join(',');

        // Fetch data for all selected metrics
        const metricsData = await Promise.all(
            Array.from(state.selectedMetrics).map(async metric => {
                let url = `${API_BASE}/data?metric=${metric}&countries=${countries}`;

                if (state.startDate) {
                    url += `&start_date=${state.startDate}`;
                }
                if (state.endDate) {
                    url += `&end_date=${state.endDate}`;
                }

                const response = await fetch(url);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return await response.json();
            })
        );

        visualizeMultiMetricTimeSeries(metricsData);
        hideMessage();
    } catch (error) {
        showMessage('Failed to load data: ' + error.message, 'error');
    } finally {
        elements.loadDataBtn.disabled = false;
    }
}

// Visualize multi-metric time series data
function visualizeMultiMetricTimeSeries(metricsData) {
    const traces = [];

    metricsData.forEach(data => {
        // Normalize data
        let displayData = normalizeTimeSeries(data);

        // Apply rebase if enabled
        if (state.rebaseToStart && state.startDate) {
            displayData = rebaseTimeSeries(displayData);
        }

        // Create traces for each country in this metric
        displayData.data.forEach(countryData => {
            traces.push({
                x: countryData.time_series.map(d => d.time_period),
                y: countryData.time_series.map(d => d.value),
                type: 'scatter',
                mode: 'lines+markers',
                name: `${countryData.country} - ${data.metric}`,
                line: { width: 2 },
                marker: { size: 4 },
                connectgaps: false
            });
        });
    });

    const isRebased = state.rebaseToStart && state.startDate;
    const chartTitle = isRebased
        ? `Multiple Metrics Over Time (Rebased to 100 at ${state.startDate})`
        : `Multiple Metrics Over Time`;
    const yAxisTitle = isRebased
        ? `Value (Index, base=100 at ${state.startDate})`
        : `Value`;

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
            r: 200,
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

// Normalize time series data to handle missing quarters
function normalizeTimeSeries(data) {
    const allPeriods = new Set();
    data.data.forEach(countryData => {
        countryData.time_series.forEach(point => {
            allPeriods.add(point.time_period);
        });
    });

    const sortedPeriods = Array.from(allPeriods).sort();

    const normalizedData = {
        ...data,
        data: data.data.map(countryData => {
            const periodMap = new Map();
            countryData.time_series.forEach(point => {
                periodMap.set(point.time_period, point.value);
            });

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

// Rebase time series to start at 100
function rebaseTimeSeries(data) {
    return {
        ...data,
        data: data.data.map(countryData => {
            if (countryData.time_series.length === 0) {
                return countryData;
            }

            const baseValue = countryData.time_series[0].value;

            const rebasedSeries = countryData.time_series.map((point, index) => {
                if (index === 0) {
                    return { ...point, value: 100 };
                }
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

// Handle date changes
function handleStartDateChange() {
    state.startDate = elements.startDateSelect.value || null;
}

function handleEndDateChange() {
    state.endDate = elements.endDateSelect.value || null;
}

function resetDateRange() {
    state.startDate = null;
    state.endDate = null;
    elements.startDateSelect.value = '';
    elements.endDateSelect.value = '';
}

// Handle rebase checkbox
function handleRebaseChange() {
    state.rebaseToStart = elements.rebaseCheckbox.checked;
}

// Handle second metric change (for correlation)
function handleMetric2Change() {
    state.selectedMetric2 = elements.metric2Select.value;
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
}

// Show message
function showMessage(text, type = 'info') {
    elements.message.textContent = text;
    elements.message.className = `message ${type}`;
}

// Hide message
function hideMessage() {
    elements.message.textContent = '';
    elements.message.className = 'message';
}

// Correlation mode (placeholder - not updated for multi-metric yet)
async function loadCorrelationData() {
    showMessage('Correlation mode not yet updated for multi-metric support', 'error');
}

// Start the application
init();
