# app/routes/leaderboard.py
from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.schemas import LeaderboardResponse, LeaderboardEntry

router = APIRouter()

@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboard():
    try:
        # Join leaderboard + strategies + profiles in one query
        result = supabase.table("leaderboard")\
            .select("""
                score,
                strategies(name),
                profiles(username),
                backtest_results(total_return)
            """)\
            .order("score", desc=True)\
            .limit(10)\
            .execute()

        entries = []
        for i, row in enumerate(result.data):
            entries.append(LeaderboardEntry(
                rank=i + 1,
                username=row["profiles"]["username"],
                strategy_name=row["strategies"]["name"],
                score=round(row["score"], 3),
                total_return=round(row["backtest_results"]["total_return"], 3)
            ))

        return LeaderboardResponse(entries=entries)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))