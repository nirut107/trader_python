import json
import os

STATE_FILE = "position_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_highest_price(symbol):
    state = load_state()
    return state.get(symbol, {}).get("highest_price", None)

def set_highest_price(symbol, price):
    state = load_state()
    if symbol not in state:
        state[symbol] = {}
    state[symbol]["highest_price"] = price
    save_state(state)
