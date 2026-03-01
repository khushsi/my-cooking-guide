"""Prompt template for single-meal swaps using gemini-1.5-flash."""


def build_swap_prompt(
    current_meal: dict,
    day_info: dict,
    user_data: dict,
    reason: str | None = None,
) -> str:
    """Build a targeted prompt for swapping a single meal."""

    allergies = ", ".join(user_data.get("allergies", [])) or "None"

    return f"""You are a culinary AI assistant for "My Cooking Guide."
The user wants to swap one specific meal from their weekly plan.

CURRENT MEAL TO REPLACE:
- Name: {current_meal.get('name', 'Unknown')}
- Day: {day_info.get('day', 'Unknown')}
- Energy level for this day: {day_info.get('energy_level', 'medium')}
- Meal type: {day_info.get('meal_type', 'dinner')}

USER REASON FOR SWAP: {reason or 'No specific reason given'}

CONSTRAINTS:
1. ALLERGIES: Strictly exclude: [{allergies}]
2. DIET: {user_data.get('diet_type', 'omnivore')}
3. CALORIES: Target approximately {current_meal.get('calories', 500)} calories for this meal.
4. If this is a low-energy day, the replacement must take under 15 minutes or use pre-prepped ingredients.

Return a JSON object with this structure (you MUST provide weight_g for every ingredient using your best culinary estimate):
{{
  "name": "New Meal Name",
  "description": "Brief description",
  "ingredients": [
     {{"name": "chicken breast pan fried", "weight_g": 150}},
     {{"name": "olive oil", "weight_g": 14}}
  ],
  "prep_time_minutes": 10,
  "cook_time_minutes": 15,
  "calories": 450,
  "protein_g": 25.0,
  "carbs_g": 45.0,
  "fat_g": 15.0,
  "uses_prepped": []
}}
"""
