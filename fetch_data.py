import sqlite3
from datetime import datetime, timezone
from binance_client import get

DB = "binance.db"

def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS balances (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            fetched_at TEXT,
            asset     TEXT,
            free      REAL,
            locked    REAL
        );

        CREATE TABLE IF NOT EXISTS prices (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            fetched_at TEXT,
            symbol    TEXT,
            price     REAL
        );

        CREATE TABLE IF NOT EXISTS klines (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol     TEXT,
            interval   TEXT,
            open_time  TEXT,
            open       REAL,
            high       REAL,
            low        REAL,
            close      REAL,
            volume     REAL,
            UNIQUE(symbol, interval, open_time)
        );

        CREATE TABLE IF NOT EXISTS trades (
            trade_id   INTEGER PRIMARY KEY,
            symbol     TEXT,
            price      REAL,
            qty        REAL,
            quote_qty  REAL,
            is_buyer   INTEGER,
            time       TEXT
        );
    """)
    conn.commit()

def fetch_balances(conn):
    now = datetime.now(timezone.utc).isoformat()
    account = get("/api/v3/account", signed=True)
    rows = [
        (now, b["asset"], float(b["free"]), float(b["locked"]))
        for b in account["balances"]
        if float(b["free"]) > 0 or float(b["locked"]) > 0
    ]
    conn.executemany(
        "INSERT INTO balances (fetched_at, asset, free, locked) VALUES (?,?,?,?)", rows
    )
    conn.commit()
    print(f"  Balances: {len(rows)} coins")

def fetch_prices(conn, symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]):
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for symbol in symbols:
        data = get("/api/v3/ticker/price", params={"symbol": symbol})
        rows.append((now, symbol, float(data["price"])))
    conn.executemany(
        "INSERT INTO prices (fetched_at, symbol, price) VALUES (?,?,?)", rows
    )
    conn.commit()
    print(f"  Prices: {len(rows)} symbols")

def fetch_klines(conn, symbols=["BTCUSDT", "ETHUSDT"], interval="1h", limit=100):
    for symbol in symbols:
        data = get("/api/v3/klines", params={
            "symbol": symbol, "interval": interval, "limit": limit
        })
        rows = [(
            symbol, interval,
            str(k[0]),           # open_time (timestamp ms)
            float(k[1]),         # open
            float(k[2]),         # high
            float(k[3]),         # low
            float(k[4]),         # close
            float(k[5]),         # volume
        ) for k in data]
        conn.executemany("""
            INSERT OR IGNORE INTO klines
            (symbol, interval, open_time, open, high, low, close, volume)
            VALUES (?,?,?,?,?,?,?,?)
        """, rows)
    conn.commit()
    print(f"  Klines: {len(symbols)} symbols × {limit} candles")

def fetch_trades(conn, symbols=["BTCUSDT", "ETHUSDT"]):
    for symbol in symbols:
        try:
            data = get("/api/v3/myTrades", signed=True, params={
                "symbol": symbol, "limit": 50
            })
            rows = [(
                t["id"], symbol,
                float(t["price"]), float(t["qty"]), float(t["quoteQty"]),
                int(t["isBuyer"]), str(t["time"])
            ) for t in data]
            conn.executemany("""
                INSERT OR IGNORE INTO trades
                (trade_id, symbol, price, qty, quote_qty, is_buyer, time)
                VALUES (?,?,?,?,?,?,?)
            """, rows)
        except:
            pass
    conn.commit()
    print(f"  Trades: done")

if __name__ == "__main__":
    print(f"Fetching... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    conn = sqlite3.connect(DB)
    init_db(conn)
    fetch_balances(conn)
    fetch_prices(conn)
    fetch_klines(conn)
    fetch_trades(conn)
    conn.close()
    print("Done ✓")