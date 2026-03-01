from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, TokenResponse, UserCreate, UserLogin
from app.services.auth_service import AuthService
from app.services.user_service import UserService
import httpx

router = APIRouter(prefix="/api/auth", tags=["auth"])

async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and validate JWT from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]
    payload = AuthService.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/google", response_model=TokenResponse)
async def google_auth(request: Request, db: AsyncSession = Depends(get_db)):
    """Accept Google OAuth token from frontend."""
    body = await request.json()
    credential = body.get("credential")

    if not credential:
        raise HTTPException(status_code=400, detail="Missing Google credential")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        google_data = resp.json()

    user_service = UserService(db)
    user = await user_service.get_or_create_google_user(google_data)
    token = AuthService.create_access_token(str(user.id))

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user with email and password."""
    user_service = UserService(db)
    if await user_service.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await user_service.create_user(user_data)
    token = AuthService.create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    user_service = UserService(db)
    user = await user_service.get_user_by_email(credentials.email)

    if not user or not user.hashed_password or not AuthService.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = AuthService.create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user."""
    return UserResponse.model_validate(current_user)
