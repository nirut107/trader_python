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


MODEL_FILE = "model_year.pkl"

def fetch_data():
    ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=LIMIT)
    df = pd.DataFrame(ohlcv, columns=['ts','open','high','low','close','vol'])
    return df

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
STOP_LOSS = -0.5    # %
TAKE_PROFIT = 0.5  # %
MAX_HOLD_MIN = 60  # นาที


def log_trade(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")




def push_summary(summary):
    print(summary)
    try:
        r = requests.post(
            # "https://trader-python.vercel.app/api/push",
            "http://localhost:3000/api/push",
            json=summary,
            timeout=5
        )
        print("push_summary:", r.status_code)
    except Exception as e:
        print("push_summary ERROR:", e)

is_hold = False

while True:
    df = load_ohlcv_from_db()
    df = add_features(df)
    last = df.iloc[-1]

    model, buy, sell = predict_signal(model, last, cfg["features"])
    signal = strategy(df, buy, sell)

    price = float(last["close"])
    now = last.name
    print(buy,sell)
    regime = detect_market_regime(df)


    # ---------- BUY ----------
    if signal == "BUY" and not in_position:
        in_position = True
        entry_price = price
        entry_time = now
        max_price = price

        log_trade(f"BUY @ {entry_price:.2f} | time={entry_time}")

        push_summary({
            "time": str(now),
            "price": price,
            "signal": "BUY"
        })

    # ---------- IN POSITION ----------
    elif in_position:
        max_price = max(max_price, price)

        exit_reason, pnl = check_exit_5m(
            df,
            entry_price,
            entry_time,
            max_price
        )

        # ----- EXIT -----
        if exit_reason:
            log_trade(f"{exit_reason} @ {price:.2f} | PnL={pnl:.2f}%")

            push_summary({
                "time": str(now),
                "price": price,
                "signal": exit_reason,
                "pnl": pnl
            })

            in_position = False
            entry_price = None
            entry_time = None
            max_price = None
            is_hold = False

        # ----- HOLD -----
        elif not is_hold:
            push_summary({
                "time": str(now),
                "price": price,
                "signal": ""
                "HOLD"
            })
            is_hold = True
    time.sleep(20)

