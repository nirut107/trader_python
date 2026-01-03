import time
import pandas as pd
from config import SYMBOL, TIMEFRAME, LIMIT,TRAIN_INTERVAL
from exchange_utils import exchange,exchange_real
from strategy import strategy,sell_all
from model_utils import train_model,predict_signal
import sqlite3
from database import save_ohlcv_to_db, load_recent_data,load_ohlcv_months
import joblib
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd
import ta
import time
from datetime import datetime
from exit import check_exit_5m 
import requests
from strategy_utils import detect_market_regime
from telegram_utils import send_telegram
import sys
from fetchdata import load_ohlcv_from_db, get_realtime_price
import gc



MODEL_FILE = "model_year.pkl"

def fetch_data():
    ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=LIMIT)
    df = pd.DataFrame(ohlcv, columns=['ts','open','high','low','close','vol'])
    return df



def add_features(df):
    df = df.copy()

    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    df = df.set_index('ts')
    df = df.sort_index()


    df['hour'] = df.index.hour
    df['day'] = df.index.dayofweek

    df['ema50'] = ta.trend.EMAIndicator(df['close'], 50).ema_indicator()
    df['ema200'] = ta.trend.EMAIndicator(df['close'], 200).ema_indicator()
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], 14).rsi()

    return df.dropna()

last_train_time = 0


cfg = joblib.load(MODEL_FILE)
print("MODEL FEATURES:", cfg["features"])
WINDOW = 200

df = load_ohlcv_from_db()
df = add_features(df)
history_df = df.tail(WINDOW).copy()

y = history_df['close']
X = history_df[cfg["features"]]

model = SARIMAX(
    endog=y,
    exog=X,
    order=cfg["order"],
    seasonal_order=cfg["seasonal_order"],
    enforce_stationarity=False,
    enforce_invertibility=False
)

model = model.filter(cfg["params"])

in_position = False
entry_price = None
entry_time = None

LOG_FILE = "trade.log"




def log_trade(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# SENT="http://localhost:3000/api/push"
SENT="https://trader-python.vercel.app/api/push"

def push_summary(summary):
    print(summary)
    try:
        r = requests.post(
            SENT
            ,
            json=summary,
            timeout=5
        )
        print("push_summary:", r.status_code)
    except Exception as e:
        print("push_summary ERROR:", e)

in_position = False
entry_price = None
entry_time = None
max_price = 0
last_candle_ts =None
ALLOW_REGIME = "UPTREND"
MAX_CANDLES = 500
loop_count = 0




while True:
    df = load_ohlcv_from_db()
    df = df.tail(MAX_CANDLES).copy()
    last_candle = df.iloc[-1]
    current_candle_ts = last_candle.name
    now = datetime.utcnow()

    # --------- STRATEGY (5m) ----------
    if current_candle_ts != last_candle_ts:
        df = add_features(df)
        last_candle_ts = current_candle_ts

        regime = detect_market_regime(df)
        signal = strategy(df)

        print("NEW CANDLE:", current_candle_ts)
        print("REGIME:", regime, "SIGNAL:", signal)

    # ---------- BUY ----------
    if signal == "BUY" and not in_position:
        if regime != ALLOW_REGIME:
            print("BLOCK BUY:", regime)
        else:
            price = get_realtime_price(
                exchange_real,
                SYMBOL,
                side="buy"
            )
            
            in_position = True
            entry_price = price
            entry_time = now
            max_price = price

            log_trade(f"BUY @ {price:.2f} | {now}")

            push_summary({
                "time": str(now),
                "price": price,
                "signal": "BUY",
                "regime": regime
            })

            send_telegram(
                f"🟢 *BUY*\n"
                f"Price: {price:.2f}\n"
                f"Regime: {regime}"
            )

    # ---------- IN POSITION ----------
    elif in_position:
        price = get_realtime_price(
            exchange_real,
            SYMBOL,
            side="sell"
        )
        if price is not None:
            now = datetime.utcnow()
        max_price = max(max_price, price)

        exit_reason, pnl = check_exit_5m(
            price,
            entry_price,
            entry_time,
            max_price
        )

        print("EXIT_CHECK:", exit_reason, pnl)
        print("REAL TIME PRICE", price)

        if exit_reason:
            log_trade(f"{exit_reason} @ {price:.2f} | PnL={pnl:.2f}%")

            push_summary({
                "time": str(now),
                "price": price,
                "signal": exit_reason,
                "pnl": pnl,
                "regime": regime
            })

            send_telegram(
                f"🔴 *{exit_reason}*\n"
                f"Price: {price:.2f}\n"
                f"PnL: {pnl:.2f}%"
            )

            # reset state
            in_position = False
            entry_price = None
            entry_time = None
            max_price = None
    if loop_count == 50:
        gc.collect()
        loop_count = 0
    loop_count += 1
    time.sleep(2)



# 8559021305:AAGWBCaz0-aNWiRsTY0BN9Pq02J-NE_FZLs