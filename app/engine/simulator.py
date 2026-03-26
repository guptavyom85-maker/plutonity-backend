# app/engine/simulator.py
import pandas as pd
import numpy as np
from typing import Dict

def simulate_portfolio(
    df: pd.DataFrame,
    initial_capital: float = 100000.0
) -> Dict:
    """
    Simulates trading based on signals in df['signal'].
    
    Rules:
    - Signal 1:  buy as many shares as we can afford
    - Signal -1: sell all shares we hold
    - Signal 0:  do nothing
    - We go LONG only (no short selling for simplicity)
    - No transaction costs for now (can add later)
    
    Returns a dict with portfolio history and trade log.
    """

    cash = initial_capital       # money not invested
    shares_held = 0              # number of shares currently owned
    portfolio_values = []        # total portfolio value each day
    trades = []                  # log of every buy/sell

    for i in range(len(df)):
        date = df.index[i]
        close_price = float(df["Close"].iloc[i])
        signal = int(df["signal"].iloc[i])

        # ── BUY ──────────────────────────────────────────
        if signal == 1 and shares_held == 0:
            # How many shares can we buy with all our cash?
            shares_to_buy = int(cash // close_price)

            if shares_to_buy > 0:
                cost = shares_to_buy * close_price
                cash -= cost
                shares_held += shares_to_buy

                trades.append({
                    "date": str(date.date()),
                    "action": "BUY",
                    "price": round(close_price, 2),
                    "shares": shares_to_buy,
                    "value": round(cost, 2)
                })

        # ── SELL ─────────────────────────────────────────
        elif signal == -1 and shares_held > 0:
            proceeds = shares_held * close_price
            cash += proceeds

            trades.append({
                "date": str(date.date()),
                "action": "SELL",
                "price": round(close_price, 2),
                "shares": shares_held,
                "value": round(proceeds, 2)
            })

            shares_held = 0

        # ── CALCULATE TOTAL PORTFOLIO VALUE TODAY ────────
        # Cash on hand + current value of shares we hold
        portfolio_value = cash + (shares_held * close_price)
        portfolio_values.append(portfolio_value)

    # If we're still holding shares at the end, sell at last price
    if shares_held > 0:
        final_price = float(df["Close"].iloc[-1])
        cash += shares_held * final_price
        portfolio_values[-1] = cash

    return {
        "portfolio_values": portfolio_values,
        "dates": [str(d.date()) for d in df.index],
        "trades": trades,
        "final_value": round(cash, 2),
        "initial_capital": initial_capital
    }