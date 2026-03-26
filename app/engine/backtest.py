# app/engine/backtest.py
from app.engine.data import get_price_data, validate_dates
from app.engine.runner import run_user_strategy
from app.engine.simulator import simulate_portfolio
from app.engine.metrics import calculate_metrics
from typing import Dict

def run_full_backtest(
    code: str,
    ticker: str,
    start_date: str,
    end_date: str,
    initial_capital: float = 100000.0
) -> Dict:
    """
    Runs the complete backtesting pipeline.
    This is the single function the rest of the app calls.
    
    Returns either:
    {"status": "completed", "metrics": {...}, "trades": [...]}
    or
    {"status": "failed", "error": "what went wrong"}
    """

    # Step 1: Validate dates
    try:
        validate_dates(start_date, end_date)
    except ValueError as e:
        return {"status": "failed", "error": str(e)}

    # Step 2: Fetch price data
    try:
        df = get_price_data(ticker, start_date, end_date)
    except ValueError as e:
        return {"status": "failed", "error": str(e)}
    except Exception as e:
        return {"status": "failed", "error": f"Failed to fetch data: {str(e)}"}

    # Step 3: Run user strategy
    df_with_signals, error = run_user_strategy(code, df)

    if error:
        return {"status": "failed", "error": error}

    # Step 4: Simulate portfolio
    try:
        simulation = simulate_portfolio(df_with_signals, initial_capital)
    except Exception as e:
        return {"status": "failed", "error": f"Simulation failed: {str(e)}"}

    # Step 5: Calculate metrics
    try:
        metrics = calculate_metrics(
            simulation["portfolio_values"],
            initial_capital
        )
    except Exception as e:
        return {"status": "failed", "error": f"Metrics calculation failed: {str(e)}"}

    return {
        "status": "completed",
        "metrics": metrics,
        "trades": simulation["trades"],
        "portfolio_values": simulation["portfolio_values"],
        "dates": simulation["dates"]
    }