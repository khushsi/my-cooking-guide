"""Prompt template for swapping a single ingredient using Gemini Flash."""

def build_ingredient_swap_prompt(
    meal: dict,
    ingredient_name: str,
    user_data: dict,
    reason: str | None = None,
) -> str:
    """Build a prompt for swapping one specific ingredient in a meal."""

    allergies = ", ".join(user_data.get("allergies", [])) or "None"
    medical_conds = ", ".join(user_data.get("medical_conditions", [])) or "None"
    loved_ingreds = ", ".join(user_data.get("loved_ingredients", [])) or "None"
    spice_tol = user_data.get("spice_tolerance", "medium")
    pref_protein = ", ".join(user_data.get("preferred_protein_sources", [])) or "No explicit preference"
    avoid_protein = ", ".join(user_data.get("avoided_protein_sources", [])) or "None"

    return f"""You are a culinary AI assistant for "My Cooking Guide."
The user wants to swap ONE specific ingredient from a meal in their plan.

CURRENT MEAL:
- Name: {meal.get('name', 'Unknown')}
- Description: {meal.get('description', '')}

INGREDIENT TO SWAP OUT: "{ingredient_name}"

USER REASON FOR SWAP: {reason or 'Wants a healthier/different alternative'}

CONSTRAINTS:
1. ALLERGIES: Strictly exclude: [{allergies}]
2. DIETARY RESTRICTIONS: Adhere strictly to "{user_data.get('diet_type', 'omnivore')}" diet.
3. MEDICAL CONDITIONS: Bear in mind: [{medical_conds}]
4. PROTEIN PREFERENCES: Prioritize: [{pref_protein}]. Avoid: [{avoid_protein}].
5. SPICE TOLERANCE: Max spice level: {spice_tol}.

Return exactly 3 suggested alternatives for "{ingredient_name}".
For each alternative, return a JSON object with this structure:
{{
  "suggestions": [
    {{
      "name": "Mashed Avocado",
      "reason": "Provides healthy fats instead of mayo",
      "estimated_weight_g": 30
    }}
  ]
}}
Return ONLY valid JSON.
"""
