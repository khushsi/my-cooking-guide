"""Package init — import all models so Alembic can discover them."""

from app.models.user import User
from app.models.menu import WeeklyMenu
from app.models.feedback import MealFeedback
from app.models.persona import Persona
from app.models.recipe import Recipe
from app.models.pantry_item import PantryItem
from app.models.nutrition import CachedIngredient

__all__ = ["User", "WeeklyMenu", "MealFeedback", "Persona", "Recipe", "PantryItem", "CachedIngredient"]

