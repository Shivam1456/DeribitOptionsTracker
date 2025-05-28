import asyncio
import threading
from flask import Flask, render_template
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import time
from rest_client import DeribitRestClient
from websocket_handler import DeribitWebSocket
from database import get_last_records, init_db

app = Flask(__name__)

def find_closest_expiry(options):
    expiry_counts = {}
    for opt in options:
        expiry = opt['expiration_timestamp'] // 1000
        expiry_counts[expiry] = expiry_counts.get(expiry, 0) + 1
    
    if not expiry_counts:
        return None
    
    closest_expiry = max(expiry_counts.items(), key=lambda x: x[1])[0]
    return datetime.fromtimestamp(closest_expiry).strftime("%d%b%y").upper()

def create_price_chart(data):
    df = pd.DataFrame([{
        'instrument': record.instrument_name,
        'price': record.price,
        'timestamp': record.timestamp
    } for record in data])
    
    fig = go.Figure()
    
    for instrument in df['instrument'].unique():
        instrument_data = df[df['instrument'] == instrument]
        fig.add_trace(go.Scatter(
            x=instrument_data['timestamp'],
            y=instrument_data['price'],
            mode='lines+markers',
            name=instrument
        ))
    
    fig.update_layout(
        title='Option Prices Over Time',
        xaxis_title='Time',
        yaxis_title='Price',
        hovermode='x unified'
    )
    
    return fig.to_html(full_html=False)

def create_greeks_chart(data):
    df = pd.DataFrame([{
        'instrument': record.instrument_name,
        'delta': record.delta,
        'volatility': record.volatility,
        'timestamp': record.timestamp
    } for record in data])
    
    fig = go.Figure()
    
    for instrument in df['instrument'].unique():
        instrument_data = df[df['instrument'] == instrument]
        fig.add_trace(go.Scatter(
            x=instrument_data['timestamp'],
            y=instrument_data['delta'],
            mode='lines+markers',
            name=f'{instrument} Delta',
            yaxis='y1'
        ))
    
    for instrument in df['instrument'].unique():
        instrument_data = df[df['instrument'] == instrument]
        fig.add_trace(go.Scatter(
            x=instrument_data['timestamp'],
            y=instrument_data['volatility'],
            mode='lines+markers',
            name=f'{instrument} Volatility',
            yaxis='y2'
        ))
    
    fig.update_layout(
        title='Greeks Analysis',
        xaxis_title='Time',
        yaxis_title='Delta',
        yaxis2=dict(
            title='Volatility',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified'
    )
    
    return fig.to_html(full_html=False)

@app.route('/')
def dashboard():
    Session = init_db()
    session = Session()
    try:
        records = get_last_records(session, limit=100)
        if not records:
            return "No data available yet. Please wait for WebSocket updates."
        
        price_chart = create_price_chart(records)
        greeks_chart = create_greeks_chart(records)
        
        latest_data = []
        for record in records[:10]:
            latest_data.append({
                'instrument': record.instrument_name,
                'price': record.price,
                'delta': record.delta,
                'volatility': record.volatility,
                'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return render_template(
            'dashboard.html',
            price_chart=price_chart,
            greeks_chart=greeks_chart,
            latest_data=latest_data
        )
    finally:
        session.close()

def run_flask_app():
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

async def main():
    Session = init_db()
    rest_client = DeribitRestClient()
    options = rest_client.get_instruments(currency="BTC")
    
    if not options:
        print("Could not fetch any option instruments")
        return
    
    expiry_date = find_closest_expiry(options)
    if not expiry_date:
        print("Could not determine expiry date")
        return
    
    print(f"Selected expiry date: {expiry_date}")
    
    selected_options = [
        opt for opt in options 
        if expiry_date in opt['instrument_name']
    ]
    
    if len(selected_options) < 5:
        print(f"Only found {len(selected_options)} instruments for {expiry_date}")
        if not selected_options:
            print("No instruments found for selected expiry")
            return
    
    selected_options = selected_options[:5]
    channels = [f"ticker.{opt['instrument_name']}.raw" for opt in selected_options]
    
    print(f"Selected options: {[opt['instrument_name'] for opt in selected_options]}")
    
    ws_client = DeribitWebSocket()
    await ws_client.run(channels)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"Error: {e}. Restarting in 10 seconds...")
            time.sleep(10)