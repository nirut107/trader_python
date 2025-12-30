

def check_exit_5m(df, entry_price, entry_time, max_price):
    last = df.iloc[-1]
    price = float(last.close)
    now = last.name

    pnl_pct = (price - entry_price) / entry_price * 100
    hold_min = (now - entry_time).total_seconds() / 60

    # 1) HARD STOP
    if pnl_pct <= -0.4:
        return "STOP_LOSS", pnl_pct

    # 2) TIME STOP
    if hold_min >= 45 and pnl_pct < 0.2:
        return "TIME_EXIT", pnl_pct

    # 3) TRAILING PROFIT
    if pnl_pct >= 0.3:
        trail_price = max_price * (1 - 0.2/100)
        if price <= trail_price:
            return "TRAIL_STOP", pnl_pct

    # 4) TECH EXIT
    if last.rsi < 45 and last.ema50 < last.ema200:
        return "TECH_EXIT", pnl_pct

    return None, pnl_pct
