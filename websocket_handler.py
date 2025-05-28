import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
from database import OptionData, init_db

load_dotenv()

class DeribitWebSocket:
    def __init__(self):
        self.ws_url = "wss://test.deribit.com/ws/api/v2"
        self.client_id = os.getenv('DERIBIT_CLIENT_ID')
        self.client_secret = os.getenv('DERIBIT_CLIENT_SECRET')
        self.session_maker = init_db()
    
    async def authenticate(self, ws):
        auth_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "public/auth",
            "params": {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        }
        await ws.send(json.dumps(auth_msg))
        response = await ws.recv()
        return json.loads(response)
    
    async def subscribe(self, ws, channels):
        sub_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "public/subscribe",
            "params": {
                "channels": channels
            }
        }
        await ws.send(json.dumps(sub_msg))
    
    async def handle_message(self, message):
        data = json.loads(message)
        if "params" in data and "data" in data["params"]:
            ticker_data = data["params"]["data"]
            self.store_data(ticker_data)
            print(f"Received update for {ticker_data['instrument_name']}")
    
    def store_data(self, ticker_data):
        session = self.session_maker()
        try:
            option = OptionData(
                id=ticker_data['instrument_name'] + str(ticker_data['timestamp']),
                instrument_name=ticker_data['instrument_name'],
                price=ticker_data.get('mark_price', ticker_data.get('last_price')),
                volatility=ticker_data.get('greeks', {}).get('vega', 0),
                delta=ticker_data.get('greeks', {}).get('delta', 0)
            )
            session.add(option)
            session.commit()
        except Exception as e:
            print(f"Error storing data: {e}")
            session.rollback()
        finally:
            session.close()
    
    async def run(self, channels):
        while True:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    auth_response = await self.authenticate(ws)
                    if "error" in auth_response:
                        print(f"Authentication failed")
                        return
                    
                    await self.subscribe(ws, channels)
                    print(f"Subscribed to {channels}")
                    
                    while True:
                        message = await ws.recv()
                        await self.handle_message(message)
            except Exception as e:
                print(f"WebSocket error. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)