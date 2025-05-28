import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DeribitRestClient:
    def __init__(self):
        self.base_url = os.getenv('DERIBIT_TESTNET_URL', 'https://test.deribit.com')
        self.client_id = os.getenv('DERIBIT_CLIENT_ID')
        self.client_secret = os.getenv('DERIBIT_CLIENT_SECRET')
        self.token = None
    
    def authenticate(self):
        url = f"{self.base_url}/api/v2/public/auth"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            self.token = response.json()['result']['access_token']
            return True
        return False
    
    def get_instruments(self, currency="BTC", kind="option", expired=False):
        if not self.token and not self.authenticate():
            raise Exception("Authentication failed")
            
        url = f"{self.base_url}/api/v2/public/get_instruments"
        params = {
            "currency": currency,
            "kind": kind,
            "expired": str(expired).lower()
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()['result']
        return None