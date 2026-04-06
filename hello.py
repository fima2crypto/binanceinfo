import os
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()  # đọc file .env

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("Thiếu API key! Kiểm tra file .env")

client = Client(API_KEY, API_SECRET)
account = client.get_account()
print(account)

print("=== THÔNG TIN TÀI KHOẢN ===")
print(f"Trạng thái: {account['accountType']}")
print(f"Có thể trade: {account['canTrade']}")
print(f"Có thể withdraw: {account['canWithdraw']}")
print(f"Có thể deposit: {account['canDeposit']}")

print("\n=== SỐ DƯ (chỉ hiện > 0) ===")
for asset in account['balances']:
    free = float(asset['free'])
    locked = float(asset['locked'])
    if free > 0 or locked > 0:
        print(f"{asset['asset']:10} | Free: {free:.8f} | Locked: {locked:.8f}")