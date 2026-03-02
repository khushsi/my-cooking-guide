"""System prompt templates for Gemini API calls."""


def build_weekly_generation_prompt(user_data: dict, feedback_history: list) -> str:
    """Build the system prompt for weekly menu generation using gemini-1.5-pro."""

    allergies = ", ".join(user_data.get("allergies", [])) or "None"
    pantry = ", ".join(user_data.get("pantry_staples", [])) or "Standard pantry staples"
    meal_types = ", ".join(user_data.get("meal_types", ["breakfast", "lunch", "dinner"]))
    energy_schedule = user_data.get("energy_schedule", {})
    
    medical_conds = ", ".join(user_data.get("medical_conditions", [])) or "None"
    loved_ingreds = ", ".join(user_data.get("loved_ingredients", [])) or "None"
    spice_tol = user_data.get("spice_tolerance", "medium")

    pref_protein = ", ".join(user_data.get("preferred_protein_sources", [])) or "No explicit preference"
    avoid_protein = ", ".join(user_data.get("avoided_protein_sources", [])) or "None"
    sneak_protein = user_data.get("sneak_in_protein", False)


    energy_section = ""
    if energy_schedule:
        energy_lines = [f"  - {day}: {level}" for day, level in energy_schedule.items()]
        energy_section = "ENERGY SCHEDULE:\n" + "\n".join(energy_lines)
    else:
        energy_section = "ENERGY SCHEDULE: Default medium energy all days"

    feedback_section = ""
    if feedback_history:
        feedback_lines = []
        for fb in feedback_history[-20:]:  # Last 20 feedbacks
            rating_text = {-1: "disliked", 0: "neutral", 1: "liked"}.get(
                fb.get("rating", 0), "neutral"
            )
            feedback_lines.append(
                f"  - {fb.get('meal_name', 'Unknown')}: {rating_text}"
                + (f" (Notes: {fb['notes']})" if fb.get("notes") else "")
                + (
                    f" (Effort: {fb['effort_accuracy']})"
                    if fb.get("effort_accuracy")
                    else ""
                )
            )
        feedback_section = (
            "\nHISTORICAL USER FEEDBACK (use this to improve suggestions):\n"
            + "\n".join(feedback_lines)
        )

    sneak_protein_instruction = ""
    if sneak_protein:
        sneak_protein_instruction = "\nSNEAK IN PROTEIN PROTOCOL: The user has requested to actively hide or sneak in extra protein. You MUST actively find ways to blend or hide high-protein vegetarian ingredients (like silken tofu, white beans, nutritional yeast, hemp hearts) into standard meals, sauces, and smoothies."

    return f"""You are a highly analytical culinary AI for "My Cooking Guide."
Generate a strictly formatted, nutritionally balanced 7-day meal plan starting from Saturday.

ABSOLUTE CONSTRAINTS:
1. ALLERGIES: Strictly exclude any of these ingredients: [{allergies}]
2. DIETARY RESTRICTIONS: Adhere strictly to "{user_data.get('diet_type', 'omnivore')}" diet.
3. MEDICAL CONDITIONS: Bear in mind the following medical conditions for the household: [{medical_conds}]
4. PROTEIN PREFERENCES: 
   - Strongly PRIORITIZE these protein sources (if applicable to diet): [{pref_protein}]
   - AVOID these protein sources: [{avoid_protein}]
5. CALORIES: Daily total for the ENTIRE household combined should be approximately {user_data.get('target_calories', 2000)} calories (+/- 10%).
6. ENERGY: Respect the energy schedule. Low-energy days must use weekend-prepped ingredients or take under 15 minutes of active cooking.
7. MEAL TYPES: Generate meals only for these meal types: [{meal_types}]
8. HOUSEHOLD: Portions for {user_data.get('household_size', 1)} people.
9. SPICE TOLERANCE: Max spice level should be {spice_tol}.
10. LOVED INGREDIENTS: Try to incorporate these if possible: [{loved_ingreds}]
{sneak_protein_instruction}

{energy_section}

AVAILABLE PANTRY ITEMS (prioritize using these): [{pantry}]

SATURDAY PREP PHILOSOPHY:
- Saturday is "Prep Day": generate batch cooking tasks that simplify weekday meals.
- Weeknight meals should reference pre-prepped ingredients from Saturday.
- Include estimated prep/cook times for every meal.
{feedback_section}

OUTPUT FORMAT:
Return a JSON object with this exact structure (you MUST provide weight_g for every ingredient using your best culinary estimate):
{{
  "days": [
    {{
      "day": "Saturday",
      "date": "YYYY-MM-DD",
      "energy_level": "high",
      "meals": {{
        "<meal_type>": {{
          "name": "Meal Name",
          "description": "Brief description",
          "ingredients": [
            {{"name": "chicken breast pan fried", "weight_g": 150}},
            {{"name": "olive oil", "weight_g": 14}}
          ],
          "prep_time_minutes": 10,
          "cook_time_minutes": 20,
          "calories": 450,
          "protein_g": 25.0,
          "carbs_g": 45.0,
          "fat_g": 15.0,
          "uses_prepped": ["prepped item from Saturday"]
        }}
      }}
    }}
  ],
  "prep_plan": [
    {{
      "action": "Boil quinoa for the week",
      "estimated_time_minutes": 20,
      "for_meals": ["Sunday lunch", "Tuesday dinner"]
    }}
  ],
  "grocery_list": [
    {{
      "name": "Asparagus",
      "quantity": "2 bunches",
      "category": "Produce", # MUST be one of: Produce, Dairy & Eggs, Meat & Seafood, Pantry, Frozen, Bakery
      "already_have": false
    }}
  ],
  "total_weekly_calories": 14000
}}
"""
