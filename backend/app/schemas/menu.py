"""Pydantic schemas for weekly menus."""

from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime


class MealSchema(BaseModel):
    name: str
    description: str
    ingredients: list[str]
    prep_time_minutes: int
    cook_time_minutes: int
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    vitamin_c_mg: float = 0.0
    iron_mg: float = 0.0
    calcium_mg: float = 0.0
    sodium_mg: float = 0.0
    uses_prepped: list[str] = []  # References to pre-prepped items


class DayPlanSchema(BaseModel):
    day: str  # "Saturday", "Sunday", etc.
    date: str
    energy_level: str  # "low", "medium", "high"
    meals: dict[str, MealSchema]  # e.g. {"breakfast": ..., "lunch": ..., "dinner": ...}


class GroceryItem(BaseModel):
    name: str
    quantity: str
    category: str  # produce, dairy, protein, grains, etc.
    already_have: bool = False


class PrepActionSchema(BaseModel):
    action: str
    estimated_time_minutes: int
    for_meals: list[str]
    day: str | None = None


class WeeklyMenuSchema(BaseModel):
    days: list[DayPlanSchema]
    total_weekly_calories: int
    total_weekly_cost_estimate: float | None = None
    grocery_list: list[GroceryItem] = []
    prep_plan: list[PrepActionSchema] = []


class MenuGenerateRequest(BaseModel):
    use_pantry_items: list[str] = []
    special_requests: str | None = None


class MenuSwapRequest(BaseModel):
    day_index: int
    meal_type: str
    reason: str | None = None


class MenuSwapIngredientRequest(BaseModel):
    day_index: int
    meal_type: str
    ingredient_name: str
    reason: str | None = None


class MenuBoostMacroRequest(BaseModel):
    day_index: int
    meal_type: str
    target_macro: str = "protein" # e.g., "protein", "healthy_fats"


class MenuResponse(BaseModel):
    id: UUID
    user_id: UUID
    week_start: date
    menu_data: dict
    grocery_list: dict | None
    prep_plan: dict | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MenuListResponse(BaseModel):
    menus: list[MenuResponse]
    total: int
