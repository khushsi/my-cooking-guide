"""System prompt templates for Gemini API calls."""


def build_weekly_generation_prompt(user_data: dict, feedback_history: list) -> str:
    """Build the system prompt for weekly menu generation using gemini-1.5-pro."""

    allergies = ", ".join(user_data.get("allergies", [])) or "None"
    pantry = ", ".join(user_data.get("pantry_staples", [])) or "Standard pantry staples"
    meal_types = ", ".join(user_data.get("meal_types", ["breakfast", "lunch", "dinner"]))
    energy_schedule = user_data.get("energy_schedule", {})

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

    return f"""You are a highly analytical culinary AI for "My Cooking Guide."
Generate a strictly formatted, nutritionally balanced 7-day meal plan starting from Saturday.

ABSOLUTE CONSTRAINTS:
1. ALLERGIES: Strictly exclude any of these ingredients: [{allergies}]
2. DIETARY RESTRICTIONS: Adhere strictly to "{user_data.get('diet_type', 'omnivore')}" diet.
3. CALORIES: Daily total should be approximately {user_data.get('target_calories', 2000)} calories (+/- 10%).
4. ENERGY: Respect the energy schedule. Low-energy days must use weekend-prepped ingredients or take under 15 minutes of active cooking.
5. MEAL TYPES: Generate meals only for these meal types: [{meal_types}]
6. HOUSEHOLD: Portions for {user_data.get('household_size', 1)} people.

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
      "category": "produce",
      "already_have": false
    }}
  ],
  "total_weekly_calories": 14000
}}
"""
