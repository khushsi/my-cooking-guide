"""Feedback router — meal grading for the continuous learning loop."""

from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.feedback import MealFeedback
from app.routers.auth import get_current_user
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackBatchCreate

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback for a single meal."""
    feedback = MealFeedback(
        id=uuid4(),
        user_id=current_user.id,
        menu_id=data.menu_id,
        meal_date=data.meal_date,
        meal_type=data.meal_type,
        was_cooked=data.was_cooked,
        rating=data.rating,
        effort_accuracy=data.effort_accuracy,
        notes=data.notes,
    )
    db.add(feedback)
    await db.flush()
    return FeedbackResponse.model_validate(feedback)


@router.post("/batch", response_model=list[FeedbackResponse])
async def submit_batch_feedback(
    data: FeedbackBatchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback for multiple meals at once (end-of-week)."""
    results = []
    for fb_data in data.feedbacks:
        feedback = MealFeedback(
            id=uuid4(),
            user_id=current_user.id,
            menu_id=fb_data.menu_id,
            meal_date=fb_data.meal_date,
            meal_type=fb_data.meal_type,
            was_cooked=fb_data.was_cooked,
            rating=fb_data.rating,
            effort_accuracy=fb_data.effort_accuracy,
            notes=fb_data.notes,
        )
        db.add(feedback)
        results.append(feedback)

    await db.flush()
    return [FeedbackResponse.model_validate(fb) for fb in results]


@router.get("/", response_model=list[FeedbackResponse])
async def get_feedback_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, le=100),
):
    """Get the user's feedback history."""
    result = await db.execute(
        select(MealFeedback)
        .where(MealFeedback.user_id == current_user.id)
        .order_by(desc(MealFeedback.created_at))
        .limit(limit)
    )
    feedbacks = result.scalars().all()
    return [FeedbackResponse.model_validate(fb) for fb in feedbacks]
