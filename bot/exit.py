from datetime import datetime

def check_exit_5m(
    price,
    entry_price,
    entry_time,
    max_price
):
    now = datetime.utcnow()

    pnl_pct = (price - entry_price) / entry_price * 100
    hold_min = (now - entry_time).total_seconds() / 60

    # ---- PARAMS (SAFE SCALP) ----
    ENTRY_SL = -0.15
    TAKE_PROFIT = 0.2
    TRAIL_PCT = 0.1
    MAX_HOLD_MIN = 10
    MIN_MOVE = 0.05

    # 0) ENTRY STOP
    if pnl_pct <= ENTRY_SL:
        return "STOP_LOSS", pnl_pct

    # 1) TAKE PROFIT
    if pnl_pct >= TAKE_PROFIT:
        return "TAKE_PROFIT", pnl_pct

    # 2) TIME EXIT
    if hold_min >= MAX_HOLD_MIN and pnl_pct < MIN_MOVE and pnl_pct > 0:
        return "TIME_EXIT", pnl_pct

    # 3) TRAIL (after TP)
    if pnl_pct > TAKE_PROFIT:
        trail_price = max_price * (1 - TRAIL_PCT / 100)
        if price <= trail_price:
            return "TRAIL_STOP", pnl_pct

    return None, pnl_pct
