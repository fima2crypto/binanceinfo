import hmac, hashlib, time, requests, os
from dotenv import load_dotenv

load_dotenv()

API_KEY    = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
BASE_URL   = "https://api.binance.com"

def _sign(params: dict) -> dict:
    params["timestamp"] = int(time.time() * 1000)
    query = "&".join(f"{k}={v}" for k, v in params.items())
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    return params

def get(endpoint: str, signed=False, params=None):
    params = params or {}
    if signed:
        params = _sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    r = requests.get(f"{BASE_URL}{endpoint}", params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()