"""Service for evolving user personas based on meal feedback."""

import json
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import google.generativeai as genai

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.services.persona_service import PersonaService
from app.schemas.persona import PersonaUpdate

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

class PreferenceEvolutionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.persona_service = PersonaService(db)

    async def evolve_persona_from_feedback(self, user_id: UUID, feedback_text: str) -> None:
        """Analyze feedback and automatically update the user's primary persona."""
        if not feedback_text or not feedback_text.strip():
            return

        personas = await self.persona_service.get_all_personas(user_id)
        if not personas:
            return
            
        primary = next((p for p in personas if p.is_primary), personas[0])

        prompt = f"""You are an AI culinary assistant tasked with updating a user's taste preferences based on their feedback.
        
Current Profile:
- Allergies: {primary.allergies}
- Disliked Ingredients: {primary.disliked_ingredients}
- Loved Ingredients: {primary.loved_ingredients}
- Spice Tolerance: {primary.spice_tolerance}

User Feedback on Latest Meal: "{feedback_text}"

Analyze the feedback. If the user expresses a clear dislike for an ingredient, a love for an ingredient, a new allergy, or a preference for a different spice level, update their profile.

Return ONLY a valid JSON object matching this schema (include all 4 fields, even if unchanged):
{{
  "allergies": ["array of exact strings"],
  "disliked_ingredients": ["array of exact strings"],
  "loved_ingredients": ["array of exact strings"],
  "spice_tolerance": "string (must be one of: none, mild, medium, hot, extra_hot)"
}}
Keep existing preferences unless the feedback explicitly contradicts them.
"""
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )

        try:
            response = model.generate_content(prompt)
            data = json.loads(response.text)
            
            # Prepare update
            update_data = PersonaUpdate(
                allergies=data.get("allergies", primary.allergies),
                disliked_ingredients=data.get("disliked_ingredients", primary.disliked_ingredients),
                loved_ingredients=data.get("loved_ingredients", primary.loved_ingredients),
                spice_tolerance=data.get("spice_tolerance", primary.spice_tolerance)
            )
            
            # Check if there's an actual change before saving to save DB calls
            has_changes = (
                set(update_data.allergies or []) != set(primary.allergies or []) or
                set(update_data.disliked_ingredients or []) != set(primary.disliked_ingredients or []) or
                set(update_data.loved_ingredients or []) != set(primary.loved_ingredients or []) or
                update_data.spice_tolerance != primary.spice_tolerance
            )
            
            if has_changes:
                await self.persona_service.update_persona(user_id, primary.id, update_data)
                print(f"Evolved persona {primary.id} based on feedback.")
                
        except Exception as e:
            print(f"Failed to evolve persona preferences: {e}")

async def background_evolve_persona(user_id: UUID, feedback_text: str):
    """Background task to run persona evolution safely."""
    async with AsyncSessionLocal() as db:
        service = PreferenceEvolutionService(db)
        try:
            await service.evolve_persona_from_feedback(user_id, feedback_text)
            await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"Background persona evolution failed: {e}")
