"""Pydantic schemas for Persona data and templates."""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Dict, Any


# ---------------------------------------------------------
# Generic Persona Templates
# ---------------------------------------------------------
GENERIC_PERSONAS = {
    "indian_vegetarian": {
        "id": "indian_vegetarian",
        "title": "Indian in USA",
        "subtitle": "Vegetarian + Eggs",
        "icon": "🇮🇳",
        "description": "Balanced traditional Indian flavors using easily accessible US ingredients.",
        "defaults": {
            "dietType": "vegetarian",
            "allergies": [],
            "customAllergies": [],
            "pantryItems": ["Rice", "Paneer", "Lentils", "Onion", "Garlic", "Tomato", "Garam Masala", "Turmeric"],
        }
    },
    "fitness_enthusiast": {
        "id": "fitness_enthusiast",
        "title": "Fitness Fanatic",
        "subtitle": "High Protein Macros",
        "icon": "💪",
        "description": "Lean cuts, complex carbs, and maximum protein for muscle recovery.",
        "defaults": {
            "dietType": "omnivore",
            "allergies": [],
            "customAllergies": [],
            "pantryItems": ["Chicken", "Eggs", "Oats", "Broccoli", "Rice"],
        }
    },
    "quick_family": {
        "id": "quick_family",
        "title": "Busy Parent",
        "subtitle": "Kid-friendly, fast",
        "icon": "👨‍👩‍👧",
        "description": "Meals under 30 minutes that the whole family will actually eat.",
        "defaults": {
            "dietType": "omnivore",
            "allergies": [],
            "customAllergies": [],
            "pantryItems": ["Pasta", "Chicken", "Canned Tomatoes", "Bread"],
        }
    }
}


class PersonaTemplate(BaseModel):
    id: str
    title: str
    subtitle: str
    icon: str
    description: str
    defaults: Dict[str, Any]


class PersonaTemplatesResponse(BaseModel):
    templates: list[PersonaTemplate]


# ---------------------------------------------------------
# Persona API Schemas
# ---------------------------------------------------------
class PersonaBase(BaseModel):
    name: str
    is_primary: bool = False
    template_name: str | None = None
    
    diet_type: str = "omnivore"
    allergies: list[str] = Field(default_factory=list)
    medical_conditions: list[str] = Field(default_factory=list)
    
    disliked_ingredients: list[str] = Field(default_factory=list)
    loved_ingredients: list[str] = Field(default_factory=list)
    spice_tolerance: str = "medium"
    
    target_calories: int | None = None
    height_cm: int | None = None
    weight_kg: int | None = None


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    name: str | None = None
    diet_type: str | None = None
    allergies: list[str] | None = None
    medical_conditions: list[str] | None = None
    disliked_ingredients: list[str] | None = None
    loved_ingredients: list[str] | None = None
    spice_tolerance: str | None = None
    target_calories: int | None = None
    height_cm: int | None = None
    weight_kg: int | None = None


class PersonaResponse(PersonaBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
