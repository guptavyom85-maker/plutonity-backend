# app/routes/backtest.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas import BacktestSubmitRequest, BacktestSubmitResponse, BacktestResultResponse
from app.routes.auth import get_current_user
from app.database import supabase
from app.tasks import run_backtest_task
import uuid

router = APIRouter()


@router.post("/submit", response_model=BacktestSubmitResponse)
async def submit_backtest(
    request: BacktestSubmitRequest,
    current_user=Depends(get_current_user)
):
    try:
        # Save strategy to DB
        strategy_id = str(uuid.uuid4())
        supabase.table("strategies").insert({
            "id": strategy_id,
            "user_id": current_user.id,
            "name": request.strategy_name,
            "code": request.code,
            "ticker": request.ticker,
            "start_date": request.start_date,
            "end_date": request.end_date
        }).execute()

        # Create pending result record
        result_id = str(uuid.uuid4())
        supabase.table("backtest_results").insert({
            "id": result_id,
            "strategy_id": strategy_id,
            "user_id": current_user.id,
            "status": "pending"
        }).execute()

        # Queue the task
        run_backtest_task.delay(
            result_id=result_id,
            strategy_id=strategy_id,
            user_id=current_user.id,
            code=request.code,
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital
        )

        return BacktestSubmitResponse(
            job_id=result_id,
            strategy_id=strategy_id,
            status="pending",
            message="Backtest queued. Poll /backtest/result/{strategy_id} for updates."
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"SUBMIT ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{result_id}")
async def get_status(
    result_id: str,
    current_user=Depends(get_current_user)
):
    try:
        result = supabase.table("backtest_results")\
            .select("status, error_message")\
            .eq("id", result_id)\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "result_id": result_id,
            "status": result.data["status"],
            "error": result.data.get("error_message")
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"STATUS ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{strategy_id}", response_model=BacktestResultResponse)
async def get_result(
    strategy_id: str,
    current_user=Depends(get_current_user)
):
    try:
        result = supabase.table("backtest_results")\
            .select("*")\
            .eq("strategy_id", strategy_id)\
            .single()\
            .execute()

        print(f"RESULT DATA: {result.data}")

        if not result.data:
            raise HTTPException(status_code=404, detail="Result not found")

        data = result.data

        return BacktestResultResponse(
            strategy_id=strategy_id,
            status=data["status"],
            sharpe_ratio=data.get("sharpe_ratio"),
            cagr=data.get("cagr"),
            max_drawdown=data.get("max_drawdown"),
            total_return=data.get("total_return"),
            final_value=data.get("final_value"),
            error_message=data.get("error_message")
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"GET RESULT ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))