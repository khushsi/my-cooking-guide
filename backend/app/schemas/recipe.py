"""Pydantic schemas for recipes."""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class RecipeIngredient(BaseModel):
    name: str
    amount: str | None = None
    unit: str | None = None
    weight_g: float | None = None


class RecipeBase(BaseModel):
    name: str
    description: str
    diet_types: list[str] = []
    meal_types: list[str] = []
    calories: int | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    ingredients: list[RecipeIngredient]
    instructions: list[str] = []
    prep_time_minutes: int = 0
    cook_time_minutes: int = 0


class RecipeCreate(RecipeBase):
    is_ai_generated: bool = True
    source_id: str | None = None


class RecipeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    diet_types: list[str] | None = None
    meal_types: list[str] | None = None
    calories: int | None = None
    calories: int | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    instructions: list[str] | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None


class RecipeResponse(RecipeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
