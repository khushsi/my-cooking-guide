from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.user import UserOnboarding, UserProfile, UserResponse
from app.services.onboarding_service import OnboardingService

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


@router.post("/basics", response_model=UserResponse)
async def complete_onboarding(
    data: UserOnboarding,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Step 1-3: Save onboarding data and create primary persona."""
    onboarding_service = OnboardingService(db)
    return await onboarding_service.complete_onboarding(data, current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: UserProfile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Progressive profiling: update calories, macros, energy schedule."""
    onboarding_service = OnboardingService(db)
    return await onboarding_service.update_profile(data, current_user)
