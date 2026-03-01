"""Pydantic schemas for user data."""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    email: str
    name: str
    avatar_url: str | None = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOnboarding(BaseModel):
    selected_persona_id: str | None = None
    household_size: int = 1
    diet_type: str = "omnivore"
    allergies: list[str] = []
    pantry_staples: list[str] = []
    meal_types: list[str] = ["breakfast", "lunch", "dinner"]


class UserProfile(BaseModel):
    target_calories: int | None = None
    macro_targets: dict | None = None
    energy_schedule: dict | None = None


class UserResponse(UserBase):
    id: UUID
    persona_type: str | None
    height_cm: int | None
    weight_kg: int | None
    household_size: int
    diet_type: str
    allergies: list[str]
    pantry_staples: list[str]
    meal_types: list[str]
    target_calories: int | None
    macro_targets: dict | None
    energy_schedule: dict | None
    onboarding_complete: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
