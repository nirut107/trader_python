import numpy as np
import ta

def detect_market_regime(df):
    if len(df) < 200:
        return "SIDEWAYS"

    ema50 = df["ema50"]
    ema200 = df["ema200"]

    slope = ema200.iloc[-1] - ema200.iloc[-20]
    price = df["close"].iloc[-1]

    atr = ta.volatility.AverageTrueRange(
        df["high"], df["low"], df["close"], window=14
    ).average_true_range().iloc[-1]

    if (
        price > ema200.iloc[-1]
        and ema50.iloc[-1] > ema200.iloc[-1]
        and slope > atr * 0.05
    ):
        return "UPTREND"

    if (
        price < ema200.iloc[-1]
        and ema50.iloc[-1] < ema200.iloc[-1]
        and slope < -atr * 0.05
    ):
        return "DOWNTREND"

    return "SIDEWAYS"

