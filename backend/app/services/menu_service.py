from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from fastapi import HTTPException
from app.models.user import User
from app.models.menu import WeeklyMenu
from app.models.feedback import MealFeedback
from app.schemas.menu import (
    MenuGenerateRequest,
    MenuSwapRequest,
    MenuResponse,
    MenuListResponse,
)
from app.services.gemini_service import generate_weekly_menu, swap_single_meal
from app.services.persona_service import PersonaService
from app.services.pantry_service import PantryService
from app.utils.date_utils import get_current_saturday

class MenuService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.persona_service = PersonaService(db)
        self.pantry_service = PantryService(db)

    async def generate_menu(self, data: MenuGenerateRequest, current_user: User) -> MenuResponse:
        week_start = get_current_saturday()

        # Phase 2: Aggregate dietary requirements from all personas
        household_reqs = await self.persona_service.get_household_requirements(current_user.id)
        
        # Phase 2: Fetch actual pantry items
        pantry_staples = await self.pantry_service.get_staples_for_menu(current_user.id)

        user_data = {
            "household_size": household_reqs.get("persona_count") or current_user.household_size,
            "diet_type": household_reqs.get("diet_type", current_user.diet_type),
            "allergies": household_reqs.get("allergies", []),
            "disliked_ingredients": household_reqs.get("disliked_ingredients", []),
            "medical_conditions": household_reqs.get("medical_conditions", []),
            "loved_ingredients": household_reqs.get("loved_ingredients", []),
            "spice_tolerance": household_reqs.get("spice_tolerance", "medium"),
            "pantry_staples": list(set(pantry_staples + data.use_pantry_items)),
            "meal_types": current_user.meal_types or ["breakfast", "lunch", "dinner"],
            "target_calories": household_reqs.get("suggested_total_calories") or current_user.target_calories or 2000,
            "macro_targets": current_user.macro_targets,
            "energy_schedule": current_user.energy_schedule,
        }

        # Get historical feedback
        feedback_result = await self.db.execute(
            select(MealFeedback)
            .where(MealFeedback.user_id == current_user.id)
            .order_by(desc(MealFeedback.created_at))
            .limit(20)
        )
        feedbacks = feedback_result.scalars().all()
        feedback_history = [
            {
                "rating": fb.rating,
                "effort_accuracy": fb.effort_accuracy,
                "notes": fb.notes,
                "meal_type": fb.meal_type,
            }
            for fb in feedbacks
        ]

        menu_data = await generate_weekly_menu(self.db, user_data, feedback_history)

        menu = WeeklyMenu(
            id=uuid4(),
            user_id=current_user.id,
            week_start=week_start,
            menu_data=menu_data.get("days", menu_data),
            grocery_list=menu_data.get("grocery_list"),
            prep_plan=menu_data.get("prep_plan"),
            status="draft",
        )
        self.db.add(menu)
        await self.db.flush()

        return MenuResponse.model_validate(menu)

    async def get_current_menu(self, current_user: User) -> MenuResponse | None:
        week_start = get_current_saturday()

        result = await self.db.execute(
            select(WeeklyMenu)
            .where(
                WeeklyMenu.user_id == current_user.id,
                WeeklyMenu.week_start == week_start,
            )
            .order_by(desc(WeeklyMenu.created_at))
            .limit(1)
        )
        menu = result.scalar_one_or_none()
        if not menu:
            return None
        return MenuResponse.model_validate(menu)

    async def get_menu_history(self, current_user: User, limit: int, offset: int) -> MenuListResponse:
        result = await self.db.execute(
            select(WeeklyMenu)
            .where(WeeklyMenu.user_id == current_user.id)
            .order_by(desc(WeeklyMenu.week_start))
            .offset(offset)
            .limit(limit)
        )
        menus = result.scalars().all()

        count_result = await self.db.execute(
            select(func.count())
            .select_from(WeeklyMenu)
            .where(WeeklyMenu.user_id == current_user.id)
        )
        total = count_result.scalar()

        return MenuListResponse(
            menus=[MenuResponse.model_validate(m) for m in menus],
            total=total,
        )

    async def get_menu_by_id(self, menu_id: str, current_user: User) -> WeeklyMenu:
        result = await self.db.execute(
            select(WeeklyMenu).where(
                WeeklyMenu.id == menu_id,
                WeeklyMenu.user_id == current_user.id,
            )
        )
        menu = result.scalar_one_or_none()
        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found")
        return menu

    async def swap_meal(self, menu_id: str, data: MenuSwapRequest, current_user: User) -> MenuResponse:
        menu = await self.get_menu_by_id(menu_id, current_user)

        days = menu.menu_data if isinstance(menu.menu_data, list) else menu.menu_data.get("days", [])
        if data.day_index < 0 or data.day_index >= len(days):
            raise HTTPException(status_code=400, detail="Invalid day index")

        day = days[data.day_index]
        meals = day.get("meals", {})
        current_meal = meals.get(data.meal_type)
        if not current_meal:
            raise HTTPException(status_code=400, detail="Meal type not found for this day")

        # Phase 2: Use household requirements for swaps too
        household_reqs = await self.persona_service.get_household_requirements(current_user.id)

        user_data = {
            "household_size": household_reqs.get("persona_count") or current_user.household_size,
            "diet_type": household_reqs.get("diet_type", current_user.diet_type),
            "allergies": household_reqs.get("allergies", []),
            "disliked_ingredients": household_reqs.get("disliked_ingredients", []),
            "medical_conditions": household_reqs.get("medical_conditions", []),
            "loved_ingredients": household_reqs.get("loved_ingredients", []),
            "spice_tolerance": household_reqs.get("spice_tolerance", "medium"),
            "target_calories": 2000, # Per meal calorie logic is handled later in GeminiService
        }

        day_info = {
            "day": day.get("day", ""),
            "energy_level": day.get("energy_level", "medium"),
            "meal_type": data.meal_type,
        }

        new_meal = await swap_single_meal(self.db, current_meal, day_info, user_data, data.reason)

        days[data.day_index]["meals"][data.meal_type] = new_meal
        if isinstance(menu.menu_data, list):
            menu.menu_data = days
        else:
            menu.menu_data["days"] = days

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(menu, "menu_data")

        await self.db.flush()
        return MenuResponse.model_validate(menu)

    async def accept_menu(self, menu_id: str, current_user: User) -> dict:
        menu = await self.get_menu_by_id(menu_id, current_user)
        menu.status = "accepted"
        await self.db.flush()
        return {"status": "accepted"}
