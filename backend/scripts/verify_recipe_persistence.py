import asyncio
import uuid
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()
import google.generativeai as genai
api_key = os.getenv("gemini_api_key")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("WARNING: gemini_api_key not found in environment!")

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.recipe import Recipe
from app.services.gemini_service import generate_weekly_menu

async def verify_persistence():
    async with AsyncSessionLocal() as db:
        # 1. Create a dummy user
        test_user = User(
            id=uuid.uuid4(),
            email=f"test_{uuid.uuid4().hex[:6]}@example.com",
            hashed_password="hashed",
            name="Test User",
            household_size=2,
            diet_type="vegetarian",
            onboarding_complete=True
        )
        db.add(test_user)
        await db.flush()
        
        user_data = {
            "household_size": 2,
            "diet_type": "vegetarian",
            "meal_types": ["breakfast", "lunch", "dinner"]
        }
        
        print("Generating menu and persisting recipes...")
        # 2. Generate menu (should persist recipes)
        await generate_weekly_menu(db, user_data, [])
        await db.commit()
        
        # 3. Check if recipes were added
        stmt = select(Recipe)
        result = await db.execute(stmt)
        recipes = result.scalars().all()
        
        print(f"Total recipes in DB: {len(recipes)}")
        for r in recipes[:3]:
            print(f"- {r.name} ({r.calories} kcal)")
            
        if len(recipes) > 0:
            print("SUCCESS: Recipes persisted to database.")
        else:
            print("FAILURE: No recipes found in database.")

if __name__ == "__main__":
    asyncio.run(verify_persistence())
