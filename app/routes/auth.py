# app/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas import RegisterRequest, LoginRequest, AuthResponse
from app.database import supabase

router = APIRouter()
security = HTTPBearer()


# ─── REGISTER ────────────────────────────────────────────

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    try:
        # Step 1: Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Registration failed")

        user_id = auth_response.user.id

        # Step 2: Update the auto-created profile with chosen username
        supabase.table("profiles").update({
            "username": request.username
        }).eq("id", user_id).execute()

        # Step 3: Log them in immediately to get a token
        login_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        return AuthResponse(
            access_token=login_response.session.access_token,
            user_id=user_id,
            username=request.username
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"REGISTER ERROR: {str(e)}")  # add this line
        raise HTTPException(status_code=400, detail=str(e))


# ─── LOGIN ───────────────────────────────────────────────

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Get username from profiles table
        profile = supabase.table("profiles")\
            .select("username")\
            .eq("id", response.user.id)\
            .single()\
            .execute()

        return AuthResponse(
            access_token=response.session.access_token,
            user_id=response.user.id,
            username=profile.data["username"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")


# ─── GET CURRENT USER (reusable dependency) ──────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        user = supabase.auth.get_user(token)

        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user.user

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")