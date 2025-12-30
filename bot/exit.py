def check_exit_5m(df, entry_price, entry_time, max_price, tighten=False):
    last = df.iloc[-1]
    price = float(last.close)
    now = last.name

    pnl_pct = (price - entry_price) / entry_price * 100
    hold_min = (now - entry_time).total_seconds() / 60

    # -------------------------
    # PARAMS (ปรับตาม tighten)
    # -------------------------
    HARD_SL = -0.4 if not tighten else -0.25
    TIME_LIMIT = 45 if not tighten else 25
    MIN_PROFIT_TIME_EXIT = 0.2 if not tighten else 0.1
    TRAIL_PCT = 0.2 if not tighten else 0.12
    RSI_EXIT = 45 if not tighten else 50

    # 1) HARD STOP
    if pnl_pct <= HARD_SL:
        return "STOP_LOSS", pnl_pct

    # 2) TIME STOP
    if hold_min >= TIME_LIMIT and pnl_pct < MIN_PROFIT_TIME_EXIT:
        return "TIME_EXIT", pnl_pct

    # 3) TRAILING PROFIT
    if pnl_pct >= 0.3:
        trail_price = max_price * (1 - TRAIL_PCT / 100)
        if price <= trail_price:
            return "TRAIL_STOP", pnl_pct

    # 4) TECH EXIT
    if last.rsi < RSI_EXIT and last.ema50 < last.ema200:
        return "TECH_EXIT", pnl_pct

    return None, pnl_pct
