"""Pydantic schemas for meal feedback."""

from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime


class FeedbackCreate(BaseModel):
    menu_id: UUID
    meal_date: date
    meal_type: str
    was_cooked: bool = False
    rating: int = 0  # -1, 0, 1
    effort_accuracy: str | None = None
    notes: str | None = None


class FeedbackResponse(BaseModel):
    id: UUID
    user_id: UUID
    menu_id: UUID
    meal_date: date
    meal_type: str
    was_cooked: bool
    rating: int
    effort_accuracy: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackBatchCreate(BaseModel):
    feedbacks: list[FeedbackCreate]
