# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# ─── AUTH SCHEMAS ────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr        # pydantic validates this is a real email format
    password: str
    username: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    username: str

# ─── BACKTEST SCHEMAS ────────────────────────────────────

class BacktestSubmitRequest(BaseModel):
    strategy_name: str
    code: str              # the user's Python strategy code
    ticker: str            # e.g. "RELIANCE", "TCS", "NIFTY50"
    start_date: str        # e.g. "2015-01-01"
    end_date: str          # e.g. "2024-01-01"
    initial_capital: float = 100000.0   # default 1 lakh

class BacktestSubmitResponse(BaseModel):
    job_id: str
    strategy_id: str
    status: str
    message: str

class BacktestResultResponse(BaseModel):
    strategy_id: str
    status: str
    sharpe_ratio: Optional[float] = None
    cagr: Optional[float] = None
    max_drawdown: Optional[float] = None
    total_return: Optional[float] = None
    final_value: Optional[float] = None
    sortino_ratio: Optional[float] = None
    win_rate: Optional[float] = None
    n_days: Optional[int] = None
    n_years: Optional[float] = None
    error_message: Optional[str] = None
# ─── LEADERBOARD SCHEMAS ─────────────────────────────────

class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    strategy_name: str
    score: float           # sharpe ratio
    total_return: float

class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]