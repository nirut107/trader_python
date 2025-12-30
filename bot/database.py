import sqlite3
import pandas as pd
from config import TRAIN_MONTHS
import time
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "ohlcv.db")

conn = sqlite3.connect("ohlcv.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS ohlcv (
    ts INTEGER PRIMARY KEY,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    vol REAL
)
""")
conn.commit()
conn.close()

def save_ohlcv_to_db(df):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("ohlcv", conn, if_exists="append", index=False)
    conn.close()

def load_recent_data(limit=500):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"""
        SELECT * FROM ohlcv ORDER BY ts DESC LIMIT {limit}
    """, conn)
    conn.close()

    return df.sort_values("ts")

def load_ohlcv_months(months=TRAIN_MONTHS):
    conn = sqlite3.connect(DB_PATH)
    
    now_ms = int(time.time() * 1000)
    period_ms = months * 30 * 24 * 60 * 60 * 1000

    train_start = now_ms - period_ms

    query = f"""
        SELECT *
        FROM ohlcv
        WHERE ts >= {train_start}
        ORDER BY ts
    """
    # query = f"""
    #     SELECT *
    #     FROM ohlcv
    # """

    df = pd.read_sql(query, conn)
    conn.close()
    print("Rows:", df.shape[0])
    print("Days:", df.shape[0] / (60/5*24))
    return df
