import ta
from config import BASE_ATR_MULT, MIN_ATR_MULT, MAX_ATR_MULT, ATR_PERIOD, ATR_MEAN_PERIOD,SYMBOL
from exchange_utils import sell_all
from state_utils import get_highest_price, set_highest_price


highest_price = None

def calculate_atr_and_volatility(df):
    atr_series = ta.volatility.AverageTrueRange(
        high=df['high'],
        low=df['low'],
        close=df['close'],
        window=ATR_PERIOD
    ).average_true_range()

    atr_now = atr_series.iloc[-1]
    atr_mean = atr_series.tail(ATR_MEAN_PERIOD).mean()

    vol_ratio = atr_now / atr_mean if atr_mean > 0 else 1

    adaptive_mult = BASE_ATR_MULT * vol_ratio
    adaptive_mult = max(MIN_ATR_MULT, min(MAX_ATR_MULT, adaptive_mult))

    return atr_now, adaptive_mult



def check_adaptive_atr_trailing(df, current_price, avg_price, position_size, symbol=SYMBOL):
    atr, atr_mult = calculate_atr_and_volatility(df)

    highest_price = get_highest_price(symbol)
    if highest_price is None:
        highest_price = current_price
        set_highest_price(symbol, highest_price)

    if current_price > highest_price:
        highest_price = current_price
        set_highest_price(symbol, highest_price)

    if current_price < avg_price + atr:
        return False

    trailing_stop = highest_price - atr * atr_mult

    print(f"ATR:{atr:.2f}  Mult:{atr_mult:.2f}  High:{highest_price:.2f}  SL:{trailing_stop:.2f}")
    
    if current_price <= trailing_stop:
        sell_all(position_size)
        set_highest_price(symbol, None)
        return True

    return False

