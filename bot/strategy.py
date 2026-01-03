import pandas as pd
import ta
from config import STOP_LOSS_PCT, TAKE_PROFIT_PCT, DCA_DROP_PCT, DCA_MAX_BUYS
from exchange_utils import  get_position_from_trades, sell_all,exchange,get_dynamic_amount
from trailing import check_adaptive_atr_trailing
from state_utils import set_highest_price

# def strategy(df, forecast_buy, forecast_sell):

def strategy(df):
    """
    Mixed Entry Strategy:
    - Pullback BUY (RSI reset)
    - Momentum BUY (but not overextended)
    """

    # --- ensure indicators ---
    if "ema50" not in df:
        df["ema50"] = ta.trend.EMAIndicator(df["close"], 50).ema_indicator()
        df["ema200"] = ta.trend.EMAIndicator(df["close"], 200).ema_indicator()
        df["rsi"] = ta.momentum.RSIIndicator(df["close"], 14).rsi()

    df = df.dropna()
    if len(df) < 3:
        return "HOLD"

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ======================
    # 1) Pullback BUY (best quality)
    # ======================
    pullback_buy = (
        last.ema50 > last.ema200 and
        prev.rsi < 50 and
        last.rsi > 50 and
        last.rsi > prev.rsi
    )

    # ======================
    # 2) Momentum BUY (careful)
    # ======================
    momentum_buy = (
        last.ema50 > last.ema200 and
        55 <= last.rsi <= 62 and          # แข็งแรง แต่ไม่ overbought
        last.rsi >= prev.rsi              # momentum ยังเพิ่ม
    )

    # ======================
    # BUY decision
    # ======================
    if pullback_buy or momentum_buy:
        return "BUY"

    # ======================
    # SELL / EXIT signal
    # ======================
    if (
        last.ema50 < last.ema200 or
        last.rsi < 45
    ):
        return "SELL"

    return "HOLD"


