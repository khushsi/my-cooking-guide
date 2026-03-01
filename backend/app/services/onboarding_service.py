from uuid import uuid4
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.persona import Persona
from app.models.menu import WeeklyMenu
from app.schemas.user import UserOnboarding, UserProfile, UserResponse
from app.schemas.persona import PersonaCreate
from app.schemas.pantry import PantryItemCreate
from app.services.gemini_service import generate_weekly_menu
from app.services.persona_service import PersonaService
from app.services.pantry_service import PantryService
from app.utils.date_utils import get_current_saturday

class OnboardingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.persona_service = PersonaService(db)
        self.pantry_service = PantryService(db)

    async def complete_onboarding(self, data: UserOnboarding, current_user: User) -> UserResponse:
        current_user.household_size = data.household_size
        current_user.diet_type = data.diet_type
        current_user.onboarding_complete = True
        
        # Create the primary persona using PersonaService
        persona_data = PersonaCreate(
            name="Primary",
            is_primary=True,
            template_name=data.selected_persona_id,
            diet_type=data.diet_type,
            allergies=data.allergies or [],
        )
        await self.persona_service.create_persona(current_user.id, persona_data)

        # Create pantry items using PantryService
        if data.pantry_staples:
            pantry_items = [
                PantryItemCreate(name=staple, category="Staples") 
                for staple in data.pantry_staples
            ]
            await self.pantry_service.bulk_create_items(current_user.id, pantry_items)

        # Generate initial menu
        user_data = {
            "household_size": data.household_size,
            "diet_type": data.diet_type,
            "allergies": data.allergies or [],
            "pantry_staples": data.pantry_staples or [],
            "meal_types": data.meal_types or ["breakfast", "lunch", "dinner"],
            "target_calories": 2000, 
        }
        
        try:
            menu_data = await generate_weekly_menu(self.db, user_data, [])
            week_start = get_current_saturday()

            initial_menu = WeeklyMenu(
                id=uuid4(),
                user_id=current_user.id,
                week_start=week_start,
                menu_data=menu_data.get("days", menu_data),
                grocery_list=menu_data.get("grocery_list"),
                prep_plan=menu_data.get("prep_plan"),
                status="draft",
            )
            self.db.add(initial_menu)
        except Exception as e:
            print(f"Failed to generate initial menu during onboarding: {e}")

        await self.db.flush()
        return UserResponse.model_validate(current_user)

    async def update_profile(self, data: UserProfile, current_user: User) -> UserResponse:
        if data.target_calories is not None:
            current_user.target_calories = data.target_calories
        if data.macro_targets is not None:
            current_user.macro_targets = data.macro_targets
        if data.energy_schedule is not None:
            current_user.energy_schedule = data.energy_schedule

        await self.db.flush()
        return UserResponse.model_validate(current_user)
