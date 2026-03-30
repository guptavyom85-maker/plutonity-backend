# app/routes/leaderboard.py
from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.schemas import LeaderboardResponse, LeaderboardEntry

router = APIRouter()

@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboard():
    try:
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

        print(f"LEADERBOARD DATA: {result.data}")

        if not result.data:
            print("LEADERBOARD: no entries found")
            return LeaderboardResponse(entries=[])

        entries = []
        for i, row in enumerate(result.data):
            print(f"ROW {i}: {row}")
            try:
                entries.append(LeaderboardEntry(
                    rank=i + 1,
                    username=row["profiles"]["username"],
                    strategy_name=row["strategies"]["name"],
                    score=round(row["score"], 3),
                    total_return=round(row["backtest_results"]["total_return"], 3)
                ))
            except Exception as row_error:
                print(f"ROW {i} ERROR: {str(row_error)} — row data: {row}")
                continue

        return LeaderboardResponse(entries=entries)

    except Exception as e:
        print(f"LEADERBOARD ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))