"""Google Gemini AI service for menu generation and meal swaps."""

import json
import asyncio
import google.generativeai as genai
from rapidfuzz import process, fuzz

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.config import get_settings
from app.prompts.weekly_generation import build_weekly_generation_prompt
from app.prompts.swap_prompt import build_swap_prompt
from app.prompts.ingredient_swap import build_ingredient_swap_prompt
from app.prompts.macro_boost import build_macro_boost_prompt
from app.services.usda_service import usda_service
from app.schemas.menu import WeeklyMenuSchema, MealSchema
from app.models.recipe import Recipe
from app.models.nutrition import CachedIngredient
from app.schemas.recipe import RecipeCreate, RecipeIngredient

settings = get_settings()

# Configure the Gemini API
genai.configure(api_key=settings.gemini_api_key)


async def _correct_meal_macros(meal_data: dict, db: AsyncSession) -> dict:
    """Uses USDA API to calculate authentic macros based on AI-generated ingredients and weights."""
    total_cal: float = 0.0
    total_pro: float = 0.0
    total_fat: float = 0.0
    total_carb: float = 0.0
    total_vit_c: float = 0.0
    total_iron: float = 0.0
    total_calcium: float = 0.0
    total_sodium: float = 0.0
    
    ingredients = meal_data.get("ingredients", [])
    
    for ing in ingredients:
        if not isinstance(ing, dict):
            continue  # Fallback if Gemini hallucinated strings instead of dictionaries
            
        name = ing.get("name")
        weight_g = float(ing.get("weight_g", 0))
        
        if not name or weight_g <= 0:
            continue
            
        try:
            # 1. Check Cache
            result = await db.execute(select(CachedIngredient).where(CachedIngredient.name == name))
            cached = result.scalar_one_or_none()
            
            if cached:
                multiplier = weight_g / 100.0
                total_pro += cached.protein_g * multiplier
                total_fat += cached.fat_g * multiplier
                total_carb += cached.carbs_g * multiplier
                total_cal += cached.calories * multiplier
                total_vit_c += (cached.vitamin_c_mg or 0.0) * multiplier
                total_iron += (cached.iron_mg or 0.0) * multiplier
                total_calcium += (cached.calcium_mg or 0.0) * multiplier
                total_sodium += (cached.sodium_mg or 0.0) * multiplier
                continue

            # 2. Cache Miss: Query USDA
            search = await usda_service.search_foods(query=name)
            foods = search.get("foods", [])
            if not foods:
                continue
                
            # Fuzzy match top 5 to find best FdcId
            top_candidates = {food["description"].lower(): food["fdcId"] for food in foods[:5]}
            best_match = process.extractOne(str(name).lower(), list(top_candidates.keys()), scorer=fuzz.WRatio)
            
            if best_match:
                matched_desc = best_match[0]
                top_fdc_id = top_candidates[matched_desc]
            else:
                top_fdc_id = foods[0].get("fdcId")
                
            details = await usda_service.get_food_details(top_fdc_id)
            
            # Base data per 100g
            base_pro, base_fat, base_carb, base_cal = 0.0, 0.0, 0.0, 0.0
            base_vit_c, base_iron, base_calcium, base_sodium = 0.0, 0.0, 0.0, 0.0
            nutrients = details.get("foodNutrients", [])
            
            for n in nutrients:
                n_info = n.get("nutrient", {})
                n_name = n_info.get("name", "")
                amount = float(n.get("amount", 0.0))
                
                if n_name == "Protein": base_pro = amount
                elif n_name == "Total lipid (fat)": base_fat = amount
                elif "Carbohydrate" in n_name: base_carb = amount
                elif n_name == "Energy": base_cal = amount
                elif "Vitamin C" in n_name: base_vit_c = amount
                elif "Iron" in n_name: base_iron = amount
                elif "Calcium" in n_name: base_calcium = amount
                elif "Sodium" in n_name: base_sodium = amount

            # Save to Cache
            new_cache = CachedIngredient(
                name=name,
                protein_g=base_pro,
                fat_g=base_fat,
                carbs_g=base_carb,
                calories=base_cal,
                vitamin_c_mg=base_vit_c,
                iron_mg=base_iron,
                calcium_mg=base_calcium,
                sodium_mg=base_sodium
            )
            db.add(new_cache)
            await db.flush() # Keep it in transaction

            # Calculate for this meal
            multiplier = weight_g / 100.0
            total_pro += base_pro * multiplier
            total_fat += base_fat * multiplier
            total_carb += base_carb * multiplier
            total_cal += base_cal * multiplier
            total_vit_c += base_vit_c * multiplier
            total_iron += base_iron * multiplier
            total_calcium += base_calcium * multiplier
            total_sodium += base_sodium * multiplier

        except Exception as e:
            print(f"Correction failed for '{name}': {e}")
            continue

    # Overwrite the Gemini guesses if we successfully calculated anything
    if total_cal > 0:
        meal_data["calories"] = int(round(float(total_cal)))
        meal_data["protein_g"] = float(round(float(total_pro), 1))
        meal_data["fat_g"] = float(round(float(total_fat), 1))
        meal_data["carbs_g"] = float(round(float(total_carb), 1))
        meal_data["vitamin_c_mg"] = float(round(float(total_vit_c), 1))
        meal_data["iron_mg"] = float(round(float(total_iron), 1))
        meal_data["calcium_mg"] = float(round(float(total_calcium), 1))
        meal_data["sodium_mg"] = float(round(float(total_sodium), 1))

        
    return meal_data


async def _find_local_recipes(db: AsyncSession, diet_type: str, meal_types: list[str], count: int = 5) -> list[dict]:
    """Search for existing recipes in the DB that match the criteria."""
    # Simple overlap check for diet_types
    stmt = (
        select(Recipe)
        .where(Recipe.diet_types.overlap([diet_type]))
        .order_by(func.random())
        .limit(count)
    )
    result = await db.execute(stmt)
    recipes = result.scalars().all()
    
    return [
        {
            "name": r.name,
            "description": r.description,
            "ingredients": r.ingredients,
            "prep_time_minutes": r.prep_time_minutes or 0,
            "cook_time_minutes": r.cook_time_minutes or 0,
            "calories": r.calories or 0,
            "protein_g": r.protein_g or 0,
            "carbs_g": r.carbs_g or 0,
            "fat_g": r.fat_g or 0,
            "instructions": r.instructions or [],
        }
        for r in recipes
    ]


async def generate_weekly_menu(db: AsyncSession, user_data: dict, feedback_history: list) -> dict:
    """Generate a full 7-day meal plan using Gemini 1.5 Pro."""

    # 1. Search for existing suitable recipes in our DB
    diet_type = user_data.get("diet_type", "omnivore")
    local_recipes = await _find_local_recipes(db, diet_type, user_data.get("meal_types", []))
    
    # Update prompt to mention these available recipes
    recipe_context = ""
    if local_recipes:
        recipe_context = "\nAvailable local recipes you can reuse:\n" + json.dumps(local_recipes, indent=2)

    system_prompt = build_weekly_generation_prompt(user_data, feedback_history)
    if recipe_context:
        system_prompt += f"\n\nIMPORTANT: Prioritize using these existing recipes if they fit well: {recipe_context}"

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )

    response = model.generate_content(system_prompt)

    try:
        raw_data = json.loads(response.text)
        validated_data = WeeklyMenuSchema.model_validate(raw_data)
        menu_data = validated_data.model_dump()
    except Exception as e:
        text = response.text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                raw_data = json.loads(text[start:end])
                validated_data = WeeklyMenuSchema.model_validate(raw_data)
                menu_data = validated_data.model_dump()
            except Exception:
                 raise ValueError(f"Failed to validate Gemini response: {e}")
        else:
            raise ValueError(f"Failed to parse Gemini response as JSON: {e}")

    # Correct macros with USDA for every generated meal and persist them
    for day in menu_data.get("days", []):
        meals = day.get("meals", {})
        for meal_type, meal_info in meals.items():
            corrected_meal = await _correct_meal_macros(meal_info, db)
            day["meals"][meal_type] = corrected_meal
            # Persist to local recipe DB
            await _persist_recipe(db, corrected_meal, diet_type=user_data.get("diet_type", "omnivore"))

    return menu_data


async def swap_single_meal(
    db: AsyncSession,
    current_meal: dict,
    day_info: dict,
    user_data: dict,
    reason: str | None = None,
) -> dict:
    """Swap a single meal using Gemini 1.5 Flash for speed."""

    prompt = build_swap_prompt(current_meal, day_info, user_data, reason)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.8,
        ),
    )

    response = model.generate_content(prompt)

    try:
        raw_meal = json.loads(response.text)
        validated_meal = MealSchema.model_validate(raw_meal)
        meal_data = validated_meal.model_dump()
    except Exception as e:
        text = response.text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                raw_meal = json.loads(text[start:end])
                validated_meal = MealSchema.model_validate(raw_meal)
                meal_data = validated_meal.model_dump()
            except Exception:
                raise ValueError(f"Failed to validate Gemini swap: {e}")
        else:
            raise ValueError(f"Failed to parse Gemini swap response: {e}")

    # Correct macros with USDA for the swapped meal
    meal_data = await _correct_meal_macros(meal_data, db)
    
    # Persist the swapped meal
    await _persist_recipe(db, meal_data, diet_type=user_data.get("diet_type", "omnivore"))

    return meal_data


async def swap_single_ingredient(
    meal: dict,
    ingredient_name: str,
    user_data: dict,
    reason: str | None = None,
) -> list[dict]:
    """Suggest 3 healthy swaps for a single ingredient."""
    prompt = build_ingredient_swap_prompt(meal, ingredient_name, user_data, reason)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.8,
        ),
    )

    response = model.generate_content(prompt)
    try:
        data = json.loads(response.text)
        return data.get("suggestions", [])
    except Exception as e:
        print(f"Failed to parse AI ingredient swap: {e}")
        return []


async def suggest_macro_boosters(
    meal: dict,
    target_macro: str,
    user_data: dict,
) -> list[dict]:
    """Suggest 3 macro boosters (e.g., high protein add-ons) for a meal."""
    prompt = build_macro_boost_prompt(meal, target_macro, user_data)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )

    response = model.generate_content(prompt)
    try:
        data = json.loads(response.text)
        return data.get("suggestions", [])
    except Exception as e:
        print(f"Failed to parse AI macro boost: {e}")
        return []



async def _persist_recipe(db: AsyncSession, meal_data: dict, diet_type: str = "omnivore") -> None:
    """Helper to save a generated meal to the recipes table if it doesn't already exist."""
    # Check if a recipe with this name already exists to avoid duplicates
    stmt = select(Recipe).where(Recipe.name == meal_data["name"])
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return

    # Map MealSchema fields to Recipe model
    recipe_ingredients = []
    for ing in meal_data.get("ingredients", []):
        if isinstance(ing, dict):
            recipe_ingredients.append(ing)
        else:
            recipe_ingredients.append({"name": str(ing)})

    new_recipe = Recipe(
        name=meal_data["name"],
        description=meal_data["description"],
        calories=meal_data.get("calories"),
        protein_g=meal_data.get("protein_g"),
        carbs_g=meal_data.get("carbs_g"),
        fat_g=meal_data.get("fat_g"),
        prep_time_minutes=meal_data.get("prep_time_minutes", 0),
        cook_time_minutes=meal_data.get("cook_time_minutes", 0),
        ingredients=recipe_ingredients,
        instructions=meal_data.get("instructions", []),
        diet_types=[diet_type],
        meal_types=[],
        is_ai_generated=True,
        source_id="gemini-1.5-pro"
    )
    db.add(new_recipe)
    await db.flush()


async def analyze_fridge_image(image_bytes: bytes, mime_type: str) -> list[dict]:
    """Parse an image of a fridge/pantry to extract ingredients using Gemini 1.5 Pro vision."""
    prompt = (
        "You are an expert culinary assistant. I have provided an image of a fridge or pantry. "
        "Analyze the image and list all the recognizable food ingredients. "
        "For each item, return a JSON object with: "
        "'name' (string, standard name like 'Milk' or 'Eggs'), "
        "'category' (string, e.g., 'Dairy', 'Produce', 'Meat', 'Pantry'), "
        "'quantity' (float, best guess or default to 1.0), "
        "'unit' (string, e.g., 'item', 'lb', 'gallon', 'oz'). "
        "Return ONLY a JSON array containing these objects. If you cannot identify anything, return an empty array []."
    )

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    
    image_part = {
        "mime_type": mime_type,
        "data": image_bytes
    }

    try:
        response = model.generate_content([prompt, image_part])
        text = response.text
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        else:
            items = json.loads(text)
            return items if isinstance(items, list) else []
    except Exception as e:
        print(f"Failed to analyze fridge image: {e}")
        return []
