import os
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET,testnet=True)

def get_usdt_price(symbol):
    """Lấy giá coin theo USDT, trả về None nếu không có cặp"""
    if symbol == "USDT":
        return 1.0
    try:
        ticker = client.get_symbol_ticker(symbol=f"{symbol}USDT")
        return float(ticker["price"])
    except:
        # Thử qua BTC nếu không có cặp USDT trực tiếp
        try:
            btc_price = float(client.get_symbol_ticker(symbol="BTCUSDT")["price"])
            coin_btc = float(client.get_symbol_ticker(symbol=f"{symbol}BTC")["price"])
            return coin_btc * btc_price
        except:
            return None

def get_account_summary():
    account = client.get_account()
    
    balances = []
    total_usdt = 0.0

    for asset in account["balances"]:
        if asset["asset"] != "BTC": 
            continue
        free = float(asset["free"])
        locked = float(asset["locked"])
        total = free + locked
        
        if total <= 0:
            continue
        
        symbol = asset["asset"]
        price = get_usdt_price(symbol)
        usdt_value = total * price if price else None
        
        if usdt_value is not None:
            total_usdt += usdt_value
        
        balances.append({
            "symbol": symbol,
            "free": free,
            "locked": locked,
            "total": total,
            "price_usdt": price,
            "value_usdt": usdt_value,
        })

    # Sắp xếp theo giá trị USDT giảm dần
    balances.sort(key=lambda x: x["value_usdt"] or 0, reverse=True)
    return balances, total_usdt

# ===== HIỂN THỊ =====
print("=" * 65)
print(f"{'COIN':<8} {'SỐ LƯỢNG':>15} {'GIÁ (USDT)':>14} {'GIÁ TRỊ (USDT)':>15}")
print("=" * 65)

balances, total_usdt = get_account_summary()

for b in balances:
    price_str = f"{b['price_usdt']:,.4f}" if b["price_usdt"] else "N/A"
    value_str = f"{b['value_usdt']:,.2f}" if b["value_usdt"] else "N/A"
    print(f"{b['symbol']:<8} {b['total']:>15.6f} {price_str:>14} {value_str:>15}")

print("=" * 65)
print(f"{'TỔNG TÀI SẢN':<38} {'≈ $' + f'{total_usdt:,.2f}':>20}")
print("=" * 65)