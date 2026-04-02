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
                user_id,
                strategies(name),
                backtest_results(total_return)
            """)\
            .order("score", desc=True)\
            .limit(10)\
            .execute()

        print(f"LEADERBOARD RAW DATA: {result.data}")

        if not result.data:
            return LeaderboardResponse(entries=[])

        entries = []
        for i, row in enumerate(result.data):
            try:
                # Fetch username separately
                profile = supabase.table("profiles")\
                    .select("username")\
                    .eq("id", row["user_id"])\
                    .single()\
                    .execute()

                username = profile.data["username"] if profile.data else "unknown"

                entry = LeaderboardEntry(
                    rank=i + 1,
                    username=username,
                    strategy_name=row["strategies"]["name"],
                    score=round(row["score"], 3),
                    total_return=round(
                        row["backtest_results"]["total_return"], 3
                    )
                )
                entries.append(entry)
            except Exception as row_error:
                print(f"ROW {i} FAILED: {str(row_error)}")
                continue

        return LeaderboardResponse(entries=entries)

    except Exception as e:
        print(f"LEADERBOARD ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))