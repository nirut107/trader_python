import pandas as pd
import ta
from config import STOP_LOSS_PCT, TAKE_PROFIT_PCT, DCA_DROP_PCT, DCA_MAX_BUYS
from exchange_utils import  get_position_from_trades, sell_all,exchange,get_dynamic_amount
from trailing import check_adaptive_atr_trailing
from state_utils import set_highest_price

# def strategy(df, forecast_buy, forecast_sell):

def strategy(df):
    # --- indicators (ensure exist) ---
    if 'ema50' not in df:
        df['ema50'] = ta.trend.EMAIndicator(df['close'], 50).ema_indicator()
        df['ema200'] = ta.trend.EMAIndicator(df['close'], 200).ema_indicator()
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], 14).rsi()

    df = df.dropna()
    last = df.iloc[-1]

    # --- BUY condition ---
    if (
        last.ema50 > last.ema200 and
        last.rsi > 50
    ):
        return "BUY"

    # --- SELL condition ---
    if (
        last.ema50 < last.ema200 and
        last.rsi < 50
    ):
        return "SELL"

    return "HOLD"

