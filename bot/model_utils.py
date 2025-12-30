from statsmodels.tsa.statespace.sarimax import SARIMAX
import joblib
import pandas as pd
import ta

MODEL_FILE = "model_year.pkl"
MODEL_FREQ = "5min"

FEATURES = [
    'ema50',
    'ema200',
    'rsi',
    'hour',
    'day'
]


def train_model(df):
    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    df = df.set_index('ts')
    df = df.asfreq(MODEL_FREQ)

    df['hour'] = df.index.hour
    df['day'] = df.index.dayofweek

    df['ema50'] = ta.trend.EMAIndicator(df['close'], 50).ema_indicator()
    df['ema200'] = ta.trend.EMAIndicator(df['close'], 200).ema_indicator()
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], 14).rsi()

    df = df.dropna()

    y = df['close']
    X = df[FEATURES]

    model = SARIMAX(
        endog=y,
        exog=X,
        order=(2,1,2),
        seasonal_order=(1,0,0,24),
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    results = model.fit(
        method='lbfgs',
        maxiter=200,
        disp=False
    )

    params = {
    "params": results.params,
    "order": results.model.order,
    "seasonal_order": results.model.seasonal_order,
    "features": FEATURES,
    "freq": MODEL_FREQ
    }

    joblib.dump(params, MODEL_FILE)
    print("✅ Saved lightweight SARIMAX params")


UP_PCT = 0.0003   # 0.03%
DOWN_PCT = 0.0003




def predict_signal(model, last_row, features):
    exog = [[last_row[f] for f in features]]

    model = model.append(
        endog=[last_row['close']],
        exog=exog,
        refit=False
    )
    forecast = model.forecast(steps=1, exog=exog).iloc[0]
    current = last_row['close']

    if forecast > current * UP_PCT:
        return model, True, False
    elif forecast < current * DOWN_PCT:
        return model, False, True
    else:
        return model, False, False


# def load_model() :
#    cfg = joblib.load("sarimax_params.pkl")

#     # ใช้ข้อมูลล่าสุดเท่านั้น (window เล็ก)
#     y = history_df['close'][-200:]
#     X = history_df[cfg["features"]][-200:]

#     model = SARIMAX(
#         endog=y,
#         exog=X,
#         order=cfg["order"],
#         seasonal_order=cfg["seasonal_order"],
#         enforce_stationarity=False,
#         enforce_invertibility=False
#     )

#     model = model.filter(cfg["params"])
