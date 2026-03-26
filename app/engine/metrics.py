# app/engine/metrics.py
import numpy as np
from typing import Dict, List

def calculate_metrics(
    portfolio_values: List[float],
    initial_capital: float,
    risk_free_rate: float = 0.065   # Indian 10-year bond yield ~6.5%
) -> Dict:
    """
    Calculates standard quantitative finance performance metrics.
    """

    values = np.array(portfolio_values)
    n_days = len(values)

    # ── TOTAL RETURN ─────────────────────────────────────
    # How much did we make overall as a percentage?
    # e.g. 0.35 means 35% total return
    total_return = (values[-1] - initial_capital) / initial_capital


    # ── CAGR (Compound Annual Growth Rate) ───────────────
    # What was our annualised return?
    # Accounts for the fact that 50% over 5 years is
    # much less impressive than 50% in 1 year
    #
    # Formula: (final/initial)^(1/years) - 1
    n_years = n_days / 252    # 252 = average trading days per year
    cagr = (values[-1] / initial_capital) ** (1 / n_years) - 1


    # ── DAILY RETURNS ────────────────────────────────────
    # Percentage change in portfolio value each day
    # We need this for Sharpe and Drawdown
    daily_returns = np.diff(values) / values[:-1]


    # ── SHARPE RATIO ─────────────────────────────────────
    # Risk-adjusted return. The most important metric.
    # Answers: how much return are you getting per unit of risk?
    #
    # > 1.0 = acceptable
    # > 2.0 = good
    # > 3.0 = excellent
    #
    # Formula: (avg daily excess return / std of daily returns) * sqrt(252)
    # "Excess return" = return above risk-free rate
    daily_risk_free = risk_free_rate / 252
    excess_returns = daily_returns - daily_risk_free

    if excess_returns.std() == 0:
        sharpe_ratio = 0.0
    else:
        sharpe_ratio = float(np.sqrt(252) * excess_returns.mean() / excess_returns.std())


    # ── MAX DRAWDOWN ─────────────────────────────────────
    # Worst peak-to-trough decline during the period
    # Answers: what was the worst losing streak?
    #
    # e.g. -0.35 means at worst we lost 35% from peak
    #
    # How it works:
    # Track the running maximum (peak so far)
    # Each day: drawdown = (current value - peak) / peak
    # Max drawdown = worst of all these
    peak = np.maximum.accumulate(values)
    drawdown = (values - peak) / peak
    max_drawdown = float(drawdown.min())


    # ── SORTINO RATIO ────────────────────────────────────
    # Like Sharpe but only penalises DOWNSIDE volatility
    # More fair than Sharpe for strategies that have
    # asymmetric returns (lots of small wins, rare big losses)
    downside_returns = excess_returns[excess_returns < 0]
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        sortino_ratio = 0.0
    else:
        sortino_ratio = float(np.sqrt(252) * excess_returns.mean() / downside_returns.std())


    # ── WIN RATE ─────────────────────────────────────────
    # What percentage of days was the portfolio up?
    winning_days = np.sum(daily_returns > 0)
    win_rate = float(winning_days / len(daily_returns))

    return {
        "total_return": round(float(total_return), 4),
        "cagr": round(float(cagr), 4),
        "sharpe_ratio": round(sharpe_ratio, 4),
        "sortino_ratio": round(sortino_ratio, 4),
        "max_drawdown": round(max_drawdown, 4),
        "win_rate": round(win_rate, 4),
        "final_value": round(float(values[-1]), 2),
        "n_days": n_days,
        "n_years": round(n_years, 2)
    }