# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, backtest, leaderboard

app = FastAPI(
    title="Plutonity API",
    description="India's gamified quant backtesting platform",
    version="1.0.0"
)

# CORS middleware
# This allows your frontend (running on localhost:3000)
# to make requests to your backend (running on localhost:8000)
# Without this, browsers block cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://plutonity-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],    # allow GET, POST, PUT, DELETE etc
    allow_headers=["*"],    # allow all headers including Authorization
)

# Register all routers with their prefixes
# Every route in auth.py will start with /auth/
# Every route in backtest.py will start with /backtest/
# Every route in leaderboard.py will start with /leaderboard/
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(backtest.router, prefix="/backtest", tags=["Backtesting"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])

@app.get("/")
def root():
    return {"message": "Plutonity API is live"}

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}