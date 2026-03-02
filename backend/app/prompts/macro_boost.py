"""Prompt template for suggesting macro boosters (e.g., more protein) using Gemini Flash."""

def build_macro_boost_prompt(
    meal: dict,
    target_macro: str,
    user_data: dict,
) -> str:
    """Build a prompt to suggest add-on ingredients to boost a specific macro."""

    allergies = ", ".join(user_data.get("allergies", [])) or "None"
    medical_conds = ", ".join(user_data.get("medical_conditions", [])) or "None"
    pref_protein = ", ".join(user_data.get("preferred_protein_sources", [])) or "No explicit preference"
    avoid_protein = ", ".join(user_data.get("avoided_protein_sources", [])) or "None"

    return f"""You are a culinary AI assistant for "My Cooking Guide."
The user's current meal is low in {target_macro.upper()}. They want suggestions for small add-ons or "boosters" that can be sprinkled, blended, or served alongside the meal to increase the {target_macro}.

CURRENT MEAL:
- Name: {meal.get('name', 'Unknown')}
- Description: {meal.get('description', '')}

CONSTRAINTS:
1. ALLERGIES: Strictly exclude: [{allergies}]
2. DIETARY RESTRICTIONS: Adhere strictly to "{user_data.get('diet_type', 'omnivore')}" diet.
3. MEDICAL CONDITIONS: Bear in mind: [{medical_conds}]
4. PROTEIN PREFERENCES (if boosting protein): Prioritize: [{pref_protein}]. Avoid: [{avoid_protein}].
5. The booster should make culinary sense with the meal (e.g., don't suggest adding tuna to a fruit smoothie).
6. Prioritize pantry staples, seeds, nuts, or zero-prep items (like hemp hearts, nutritional yeast, Greek yogurt, chia seeds, etc.).

Return exactly 3 suggested boosters.
For each suggestion, return a JSON object with this structure:
{{
  "suggestions": [
    {{
      "name": "Hemp Hearts",
      "amount_description": "2 tablespoons sprinkled on top",
      "estimated_weight_g": 20,
      "macro_boost_g": 6.0
    }}
  ]
}}
Return ONLY valid JSON.
"""
