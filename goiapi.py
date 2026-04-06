import hmac
import hashlib
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
BASE_URL = "https://api.binance.com"

# ===== CLIENT =====

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

# ===== CÁC HÀM LẤY DATA =====

def get_account():
    """Thông tin tài khoản + số dư tất cả coin"""
    return get("/api/v3/account", signed=True)

def get_balances():
    """Chỉ lấy coin có số dư > 0"""
    account = get_account()
    return [
        b for b in account["balances"]
        if float(b["free"]) > 0 or float(b["locked"]) > 0
    ]

def get_price(symbol: str):
    """Giá hiện tại của 1 cặp, ví dụ BTCUSDT"""
    data = get("/api/v3/ticker/price", params={"symbol": symbol})
    return float(data["price"])

def get_all_prices():
    """Giá tất cả các cặp"""
    return get("/api/v3/ticker/price")

def get_ticker_24h(symbol: str):
    """Thống kê 24h: giá, khối lượng, % thay đổi"""
    return get("/api/v3/ticker/24hr", params={"symbol": symbol})

def get_klines(symbol: str, interval: str = "1h", limit: int = 100):
    """
    OHLCV (nến) — interval: 1m, 5m, 15m, 1h, 4h, 1d
    Trả về list các nến, mỗi nến là:
    [open_time, open, high, low, close, volume, ...]
    """
    return get("/api/v3/klines", params={
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    })

def get_open_orders(symbol: str = None):
    """Lệnh đang mở, truyền symbol để lọc hoặc bỏ trống lấy tất cả"""
    params = {}
    if symbol:
        params["symbol"] = symbol
    return get("/api/v3/openOrders", signed=True, params=params)

def get_order_history(symbol: str, limit: int = 10):
    """Lịch sử lệnh của 1 cặp"""
    return get("/api/v3/allOrders", signed=True, params={
        "symbol": symbol,
        "limit": limit,
    })

def get_trade_history(symbol: str, limit: int = 10):
    """Lịch sử giao dịch đã khớp"""
    return get("/api/v3/myTrades", signed=True, params={
        "symbol": symbol,
        "limit": limit,
    })

# ===== DEMO =====

if __name__ == "__main__":
    # 1. Số dư
    print("=== SỐ DƯ ===")
    for b in get_balances():
        print(f"  {b['asset']}: free={b['free']} | locked={b['locked']}")

    # 2. Giá BTC
    print("\n=== GIÁ BTCUSDT ===")
    print(f"  ${get_price('BTCUSDT'):,.2f}")

    # 3. Thống kê 24h ETH
    print("\n=== ETH 24H ===")
    eth = get_ticker_24h("ETHUSDT")
    print(f"  Giá hiện tại : ${float(eth['lastPrice']):,.2f}")
    print(f"  Thay đổi 24h : {eth['priceChangePercent']}%")
    print(f"  Cao nhất 24h : ${float(eth['highPrice']):,.2f}")
    print(f"  Thấp nhất 24h: ${float(eth['lowPrice']):,.2f}")

    # 4. Nến 1h BTC (5 nến gần nhất)
    print("\n=== BTC NẾN 1H (5 NẾN GẦN NHẤT) ===")
    klines = get_klines("BTCUSDT", interval="1h", limit=5)
    for k in klines:
        print(f"  O={float(k[1]):,.0f} H={float(k[2]):,.0f} L={float(k[3]):,.0f} C={float(k[4]):,.0f} V={float(k[5]):,.2f}")