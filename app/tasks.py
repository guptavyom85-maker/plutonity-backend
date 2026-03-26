# app/tasks.py
from worker import celery_app
from app.engine.backtest import run_full_backtest
from app.database import supabase

@celery_app.task(bind=True, max_retries=2)
def run_backtest_task(
    self,
    result_id: str,
    strategy_id: str,
    user_id: str,
    code: str,
    ticker: str,
    start_date: str,
    end_date: str,
    initial_capital: float
):
    """
    The actual background task that runs the backtest.
    
    `bind=True` means `self` refers to the task instance
    This lets us retry the task if it fails
    """

    try:
        # Step 1: Mark as running in DB
        supabase.table("backtest_results").update({
            "status": "running"
        }).eq("id", result_id).execute()

        # Step 2: Run the full backtest pipeline
        result = run_full_backtest(
            code=code,
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )

        # Step 3a: If successful, save metrics
        if result["status"] == "completed":
            supabase.table("backtest_results").update({
                "status": "completed",
                **result["metrics"]
            }).eq("id", result_id).execute()

            # Add to leaderboard if positive Sharpe
            if result["metrics"]["sharpe_ratio"] > 0:
                # Check if user already has an entry for this strategy
                existing = supabase.table("leaderboard")\
                    .select("id")\
                    .eq("strategy_id", strategy_id)\
                    .execute()

                if existing.data:
                    # Update existing entry if score improved
                    supabase.table("leaderboard").update({
                        "score": result["metrics"]["sharpe_ratio"],
                        "result_id": result_id,
                    }).eq("strategy_id", strategy_id).execute()
                else:
                    # Insert new entry
                    supabase.table("leaderboard").insert({
                        "user_id": user_id,
                        "strategy_id": strategy_id,
                        "result_id": result_id,
                        "score": result["metrics"]["sharpe_ratio"]
                    }).execute()

            return {"status": "completed", "result_id": result_id}

        # Step 3b: If failed, save error
        else:
            supabase.table("backtest_results").update({
                "status": "failed",
                "error_message": result["error"]
            }).eq("id", result_id).execute()

            return {"status": "failed", "error": result["error"]}

    except Exception as e:
        # If something unexpected crashes, mark as failed
        # and optionally retry
        supabase.table("backtest_results").update({
            "status": "failed",
            "error_message": f"Unexpected error: {str(e)}"
        }).eq("id", result_id).execute()

        # Retry up to 2 times with 60 second delay
        raise self.retry(exc=e, countdown=60)