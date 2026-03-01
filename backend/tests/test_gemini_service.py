import pytest
from unittest.mock import AsyncMock, patch
from app.services.gemini_service import _correct_meal_macros
from app.models.nutrition import CachedIngredient
from sqlalchemy import select

@pytest.mark.asyncio
async def test_correct_meal_macros_cache_hit(db):
    # 1. Pre-populate cache
    ingredient_name = "test chicken"
    cached = CachedIngredient(
        name=ingredient_name,
        protein_g=20.0,
        fat_g=5.0,
        carbs_g=0.0,
        calories=125.0
    )
    db.add(cached)
    await db.commit()

    meal_data = {
        "name": "Test Meal",
        "ingredients": [
            {"name": ingredient_name, "weight_g": 200}
        ]
    }

    # 2. Call function (should hit cache)
    # We patch usda_service to ensure it's NOT called
    with patch("app.services.gemini_service.usda_service") as mock_usda:
        result = await _correct_meal_macros(meal_data, db)
        
        mock_usda.search_foods.assert_not_called()
        
        # 200g should double the base 100g macros
        assert result["protein_g"] == 40.0
        assert result["fat_g"] == 10.0
        assert result["calories"] == 250

@pytest.mark.asyncio
async def test_correct_meal_macros_cache_miss(db):
    ingredient_name = "new apple"
    meal_data = {
        "name": "Apple Snack",
        "ingredients": [
            {"name": ingredient_name, "weight_g": 100}
        ]
    }

    # Mock USDA responses
    mock_search = {"foods": [{"fdcId": 123}]}
    mock_details = {
        "foodNutrients": [
            {"nutrient": {"name": "Protein"}, "amount": 0.3},
            {"nutrient": {"name": "Total lipid (fat)"}, "amount": 0.2},
            {"nutrient": {"name": "Carbohydrate, by difference"}, "amount": 14.0},
            {"nutrient": {"name": "Energy"}, "amount": 52.0},
        ]
    }

    with patch("app.services.gemini_service.usda_service.search_foods", new_callable=AsyncMock) as mock_search_fn, \
         patch("app.services.gemini_service.usda_service.get_food_details", new_callable=AsyncMock) as mock_details_fn:
        
        mock_search_fn.return_value = mock_search
        mock_details_fn.return_value = mock_details
        
        result = await _correct_meal_macros(meal_data, db)
        
        # Verify USDA was called
        mock_search_fn.assert_called_once_with(query=ingredient_name)
        
        # Verify result
        assert result["calories"] == 52
        assert result["carbs_g"] == 14.0
        
        # Verify it was cached in DB
        stmt = select(CachedIngredient).where(CachedIngredient.name == ingredient_name)
        cache_result = await db.execute(stmt)
        cached = cache_result.scalar_one()
        assert cached.calories == 52.0
        assert cached.protein_g == 0.3
