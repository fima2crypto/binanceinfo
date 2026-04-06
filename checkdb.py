import sqlite3, pandas as pd
conn = sqlite3.connect('binance.db')
print(pd.read_sql('SELECT COUNT(*) FROM balances', conn))
print(pd.read_sql('SELECT COUNT(*) FROM prices', conn))
print(pd.read_sql('SELECT COUNT(*) FROM klines', conn))
conn.close()