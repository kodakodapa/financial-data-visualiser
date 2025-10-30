#!/usr/bin/env python3
"""
Flask backend for the Economic Data Visualizer.
Provides API endpoints for querying and analyzing economic data.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)

DB_PATH = os.path.join('data', 'economic_data.db')

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Serve the main application page."""
    return send_from_directory('web', 'index.html')

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get list of all available metrics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT
                metric_name,
                unit,
                source,
                COUNT(*) as data_points,
                MIN(time_period) as earliest,
                MAX(time_period) as latest
            FROM economic_data
            GROUP BY metric_name, unit, source
            ORDER BY metric_name
        ''')

        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'name': row['metric_name'],
                'unit': row['unit'],
                'source': row['source'],
                'data_points': row['data_points'],
                'time_range': {
                    'start': row['earliest'],
                    'end': row['latest']
                }
            })

        conn.close()
        return jsonify(metrics)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get list of all countries, optionally filtered by metric."""
    try:
        metric = request.args.get('metric')

        conn = get_db_connection()
        cursor = conn.cursor()

        if metric:
            cursor.execute('''
                SELECT DISTINCT country, COUNT(*) as data_points
                FROM economic_data
                WHERE metric_name = ?
                GROUP BY country
                ORDER BY country
            ''', (metric,))
        else:
            cursor.execute('''
                SELECT DISTINCT country, COUNT(*) as data_points
                FROM economic_data
                GROUP BY country
                ORDER BY country
            ''')

        countries = []
        for row in cursor.fetchall():
            countries.append({
                'name': row['country'],
                'data_points': row['data_points']
            })

        conn.close()
        return jsonify(countries)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Get time series data for specified metric(s) and country(ies).

    Query parameters:
        metric: Metric name (required)
        countries: Comma-separated list of countries (optional, returns all if not specified)
        start_date: Start time period (optional)
        end_date: End time period (optional)
    """
    try:
        metric = request.args.get('metric')
        if not metric:
            return jsonify({'error': 'metric parameter is required'}), 400

        countries = request.args.get('countries', '').split(',') if request.args.get('countries') else None
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query dynamically
        query = '''
            SELECT country, time_period, value, unit
            FROM economic_data
            WHERE metric_name = ?
        '''
        params = [metric]

        if countries and countries[0]:  # Check if countries list is not empty
            placeholders = ','.join('?' * len(countries))
            query += f' AND country IN ({placeholders})'
            params.extend(countries)

        if start_date:
            query += ' AND time_period >= ?'
            params.append(start_date)

        if end_date:
            query += ' AND time_period <= ?'
            params.append(end_date)

        query += ' ORDER BY country, time_period'

        cursor.execute(query, params)

        # Organize data by country
        data = {}
        unit = None

        for row in cursor.fetchall():
            country = row['country']
            if country not in data:
                data[country] = {
                    'country': country,
                    'time_series': []
                }

            data[country]['time_series'].append({
                'time_period': row['time_period'],
                'value': row['value']
            })

            if unit is None:
                unit = row['unit']

        conn.close()

        return jsonify({
            'metric': metric,
            'unit': unit,
            'data': list(data.values())
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/correlate', methods=['GET'])
def correlate():
    """
    Correlate two metrics for specified countries.

    Query parameters:
        metric1: First metric name (required)
        metric2: Second metric name (required)
        countries: Comma-separated list of countries (optional)
    """
    try:
        metric1 = request.args.get('metric1')
        metric2 = request.args.get('metric2')

        if not metric1 or not metric2:
            return jsonify({'error': 'Both metric1 and metric2 are required'}), 400

        countries = request.args.get('countries', '').split(',') if request.args.get('countries') else None

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query to join the two metrics on country and time_period
        query = '''
            SELECT
                m1.country,
                m1.time_period,
                m1.value as value1,
                m1.unit as unit1,
                m2.value as value2,
                m2.unit as unit2
            FROM economic_data m1
            INNER JOIN economic_data m2
                ON m1.country = m2.country
                AND m1.time_period = m2.time_period
            WHERE m1.metric_name = ?
                AND m2.metric_name = ?
        '''
        params = [metric1, metric2]

        if countries and countries[0]:
            placeholders = ','.join('?' * len(countries))
            query += f' AND m1.country IN ({placeholders})'
            params.extend(countries)

        query += ' ORDER BY m1.country, m1.time_period'

        cursor.execute(query, params)

        # Organize data by country
        data = {}
        unit1 = None
        unit2 = None

        for row in cursor.fetchall():
            country = row['country']
            if country not in data:
                data[country] = {
                    'country': country,
                    'data_points': []
                }

            data[country]['data_points'].append({
                'time_period': row['time_period'],
                'value1': row['value1'],
                'value2': row['value2']
            })

            if unit1 is None:
                unit1 = row['unit1']
                unit2 = row['unit2']

        conn.close()

        return jsonify({
            'metric1': {
                'name': metric1,
                'unit': unit1
            },
            'metric2': {
                'name': metric2,
                'unit': unit2
            },
            'data': list(data.values())
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get general database statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM economic_data')
        total = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(DISTINCT metric_name) as count FROM economic_data')
        metrics = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(DISTINCT country) as count FROM economic_data')
        countries = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(DISTINCT time_period) as count FROM economic_data')
        periods = cursor.fetchone()['count']

        cursor.execute('SELECT MIN(time_period) as earliest, MAX(time_period) as latest FROM economic_data')
        time_range = cursor.fetchone()

        conn.close()

        return jsonify({
            'total_records': total,
            'unique_metrics': metrics,
            'unique_countries': countries,
            'unique_periods': periods,
            'time_range': {
                'start': time_range['earliest'],
                'end': time_range['latest']
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        print("Please run: python scripts/init_database.py")
        print("Then run: python scripts/ingest_data.py data/processed/gdp-data-extracted.csv")
        exit(1)

    print("=" * 60)
    print("Economic Data Visualizer")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print("Starting server at http://localhost:5000")
    print("=" * 60)

    app.run(debug=True, port=5000)
