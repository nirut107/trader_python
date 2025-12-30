import ccxt
from config import API_KEY, API_SECRET, SYMBOL, MIN_NOTIONAL

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

exchange_real = ccxt.binance({
    'enableRateLimit': True,
})

exchange.set_sandbox_mode(True)

def fetch_balance():
    return exchange.fetch_balance()

def has_position():
    balance = fetch_balance()
    return balance['free'].get('BTC', 0) > 0.0001

def get_current_price(symbol=SYMBOL):
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']


def get_dynamic_amount():
    balance = exchange.fetch_balance()
    usdt = balance['free']['USDT']

    current_price = exchange.fetch_ticker('BTC/USDT')['last']

    RISK_PER_TRADE = 0.05

    usd_to_use = usdt * RISK_PER_TRADE

    if usd_to_use < MIN_NOTIONAL:
        usd_to_use = MIN_NOTIONAL

    amount = usd_to_use / current_price

    return amount

def get_position_from_trades(symbol=SYMBOL):
    trades = exchange.fetch_my_trades(symbol, limit=100)
    total_qty = 0.0
    total_cost = 0.0

    for t in trades:
        price = t['price']
        qty = t['amount']

        if t['side'] == 'buy':
            total_qty += qty
            total_cost += price * qty
        elif t['side'] == 'sell':
            total_qty -= qty
            total_cost -= price * qty

    if total_qty <= 0:
        return None, 0

    avg_price = total_cost / total_qty
    return avg_price, total_qty


def sell_all(qty, symbol=SYMBOL):
    if qty <= 0:
        return

    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']

    notional = qty * price
    print(qty,price,notional)
    if notional < MIN_NOTIONAL:
        return
    order = exchange.create_market_sell_order(symbol, qty)
    print("SELL ALL @", order['average'])
