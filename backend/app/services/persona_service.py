from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException
from app.models.persona import Persona
from app.schemas.persona import PersonaCreate, PersonaUpdate

class PersonaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_personas(self, user_id: UUID) -> list[Persona]:
        query = select(Persona).where(Persona.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_persona(self, user_id: UUID, data: PersonaCreate) -> Persona:
        new_persona = Persona(
            user_id=user_id,
            name=data.name,
            is_primary=data.is_primary,
            template_name=data.template_name,
            diet_type=data.diet_type,
            allergies=data.allergies,
            medical_conditions=data.medical_conditions,
            disliked_ingredients=data.disliked_ingredients,
            loved_ingredients=data.loved_ingredients,
            spice_tolerance=data.spice_tolerance,
            target_calories=data.target_calories,
            height_cm=data.height_cm,
            weight_kg=data.weight_kg,
        )
        self.db.add(new_persona)
        await self.db.flush()
        return new_persona

    async def update_persona(self, user_id: UUID, persona_id: UUID, data: PersonaUpdate) -> Persona:
        query = select(Persona).where(
            Persona.id == persona_id, Persona.user_id == user_id
        )
        result = await self.db.execute(query)
        persona = result.scalar_one_or_none()

        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(persona, key, value)

        await self.db.flush()
        return persona

    async def delete_persona(self, user_id: UUID, persona_id: UUID):
        query = select(Persona).where(
            Persona.id == persona_id, Persona.user_id == user_id
        )
        result = await self.db.execute(query)
        persona = result.scalar_one_or_none()

        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")

        await self.db.delete(persona)
        await self.db.flush()

    async def get_household_requirements(self, user_id: UUID) -> dict:
        """
        Aggregate dietary requirements from all personas in the household.
        Returns a dict with combined allergies, diet type (most restrictive),
        and combined dislikes.
        """
        personas = await self.get_all_personas(user_id)
        if not personas:
            return {}

        combined_allergies = set()
        combined_dislikes = set()
        diet_priority = {"vegan": 4, "vegetarian": 3, "pescatarian": 2, "omnivore": 1}
        most_restrictive_diet = "omnivore"
        
        total_calories = 0
        persona_count = 0

        for p in personas:
            if p.allergies:
                combined_allergies.update(p.allergies)
            if p.disliked_ingredients:
                combined_dislikes.update(p.disliked_ingredients)
            
            p_diet = p.diet_type.lower()
            if diet_priority.get(p_diet, 0) > diet_priority.get(most_restrictive_diet, 0):
                most_restrictive_diet = p_diet
            
            if p.target_calories:
                total_calories += p.target_calories
                persona_count += 1

        return {
            "diet_type": most_restrictive_diet,
            "allergies": list(combined_allergies),
            "disliked_ingredients": list(combined_dislikes),
            "suggested_total_calories": total_calories if persona_count > 0 else None
        }
