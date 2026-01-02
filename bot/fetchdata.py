import sqlite3
from database import save_ohlcv_to_db, load_recent_data,load_ohlcv_months
from exchange_utils import exchange,exchange_real
from config import SYMBOL, TIMEFRAME, LIMIT,TRAIN_INTERVAL
import time
import pandas as pd

def load_ohlcv_from_db():
    conn = sqlite3.connect("ohlcv.db")
    c = conn.cursor()

    c.execute("SELECT MAX(ts) FROM ohlcv")
    result = c.fetchone()
    last_ts = result[0] if result[0] else None
    
    if last_ts:
        since = last_ts + 60 * 1000
    else:
        since = exchange_real.parse8601('2024-09-01T00:00:00Z')

    all_new = []

    while True:
        ohlcv = exchange_real.fetch_ohlcv(SYMBOL, TIMEFRAME, since=since, limit=1000)
        # print(since)
        if not ohlcv:
            break
        all_new.extend(ohlcv)
        since = ohlcv[-1][0] + 60 * 1000
        if len(ohlcv) < 1000:
            break
        time.sleep(0.2)

    if all_new:
        df_new = pd.DataFrame(all_new, columns=['ts','open','high','low','close','vol'])
        save_ohlcv_to_db(df_new)

    df_all = load_recent_data()
    conn.close()
    return df_all


_last_ticker_time = 0
_last_ticker_price = None

def get_realtime_price(exchange, symbol, side=None, min_interval=2):
    """
    side: 'buy', 'sell', or None
    min_interval: seconds between API calls
    return: float price or None
    """
    global _last_ticker_time, _last_ticker_price

    now = time.time()

    # ---- Rate limit guard ----
    if _last_ticker_price is not None and (now - _last_ticker_time) < min_interval:
        return _last_ticker_price

    try:
        ticker = exchange.fetch_ticker(symbol)

        # ใช้ราคาที่ "สมจริง" ตามฝั่ง
        if side == "buy":
            price = ticker.get("ask") or ticker["last"]
        elif side == "sell":
            price = ticker.get("bid") or ticker["last"]
        else:
            price = ticker["last"]

        if price is None:
            return _last_ticker_price

        _last_ticker_price = float(price)
        _last_ticker_time = now
        return _last_ticker_price

    except Exception as e:
        print("⚠️ ticker error:", e)
        return _last_ticker_price
