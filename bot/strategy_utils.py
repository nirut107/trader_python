import numpy as np
import ta

def detect_market_regime(df):
    """
    Detect market regime from 5m data by resampling to HTF (30m)
    Return: 'UPTREND', 'DOWNTREND', 'SIDEWAYS'
    """

    if len(df) < 300:
        return "SIDEWAYS"

    # =========================
    # 1) Resample 5m → 30m
    # =========================
    htf = df.resample("30min").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "vol": "sum"
    }).dropna()

    if len(htf) < 120:
        return "SIDEWAYS"

    close = htf["close"]

    # =========================
    # 2) EMA200 (HTF)
    # =========================
    ema200 = ta.trend.EMAIndicator(close, 200).ema_indicator()

    price = close.iloc[-1]

    # =========================
    # 3) EMA200 slope (normalized)
    # =========================
    slope_lookback = 10
    slope = ema200.iloc[-1] - ema200.iloc[-slope_lookback]

    atr = ta.volatility.AverageTrueRange(
        htf["high"], htf["low"], close, window=14
    ).average_true_range().iloc[-1]

    # =========================
    # 4) Structure
    # =========================
    recent_high = htf["high"].iloc[-10:].max()
    recent_low = htf["low"].iloc[-10:].min()

    # =========================
    # 5) Regime rules
    # =========================
    if (
        price > ema200.iloc[-1] and
        slope > atr * 0.03 and
        htf["low"].iloc[-1] > recent_low
    ):
        return "UPTREND"

    if (
        price < ema200.iloc[-1] and
        slope < -atr * 0.03 and
        htf["high"].iloc[-1] < recent_high
    ):
        return "DOWNTREND"

    return "SIDEWAYS"


