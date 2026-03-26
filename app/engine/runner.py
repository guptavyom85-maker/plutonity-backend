# app/engine/runner.py
import pandas as pd
import numpy as np
from typing import Tuple

# ─── WHAT THE USER'S CODE MUST LOOK LIKE ────────────────
#
# The user must define ONE function called generate_signals(df)
# It receives a DataFrame with OHLCV columns
# It must return the SAME DataFrame with a new 'signal' column added
# Signal values: 1 = buy, -1 = sell, 0 = hold
#
# Example user strategy (Moving Average Crossover):
#
# def generate_signals(df):
#     df['MA20'] = df['Close'].rolling(window=20).mean()
#     df['MA50'] = df['Close'].rolling(window=50).mean()
#     df['signal'] = 0
#     df.loc[df['MA20'] > df['MA50'], 'signal'] = 1   # buy signal
#     df.loc[df['MA20'] < df['MA50'], 'signal'] = -1  # sell signal
#     return df
# ────────────────────────────────────────────────────────

# These are the ONLY things user code can access
# No os, no subprocess, no requests, no file system
SAFE_BUILTINS = {
    "len": len,
    "range": range,
    "print": print,
    "min": min,
    "max": max,
    "abs": abs,
    "round": round,
    "int": int,
    "float": float,
    "list": list,
    "dict": dict,
    "sum": sum,
    "zip": zip,
    "enumerate": enumerate,
    "isinstance": isinstance,
}

def run_user_strategy(code: str, df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Safely executes user strategy code.
    
    Returns:
        (DataFrame with signals, error_message)
        If successful: (df_with_signals, None)
        If failed:     (None, error_string)
    """

    # This is what user code can import/use
    safe_globals = {
        "__builtins__": SAFE_BUILTINS,
        "pd": pd,
        "np": np,
    }

    local_namespace = {}

    # Step 1: Execute the user's code
    # This defines their generate_signals function
    try:
        exec(code, safe_globals, local_namespace)
    except SyntaxError as e:
        return None, f"Syntax error in your code: {str(e)}"
    except Exception as e:
        return None, f"Error in strategy code: {str(e)}"

    # Step 2: Check that they defined generate_signals
    generate_signals = local_namespace.get("generate_signals")

    if not generate_signals:
        return None, "Your strategy must define a function called generate_signals(df)"

    if not callable(generate_signals):
        return None, "generate_signals must be a function"

    # Step 3: Call their function with the price data
    try:
        result_df = generate_signals(df.copy())  # .copy() protects original data
    except Exception as e:
        return None, f"Error running generate_signals: {str(e)}"

    # Step 4: Validate what they returned
    if not isinstance(result_df, pd.DataFrame):
        return None, "generate_signals must return a DataFrame"

    if "signal" not in result_df.columns:
        return None, "Your DataFrame must have a 'signal' column with values 1, -1, or 0"

    # Replace any NaN signals with 0 (hold)
    result_df["signal"] = result_df["signal"].fillna(0)

    # Clamp signals to valid values only
    result_df["signal"] = result_df["signal"].apply(
        lambda x: 1 if x > 0 else (-1 if x < 0 else 0)
    )

    return result_df, None