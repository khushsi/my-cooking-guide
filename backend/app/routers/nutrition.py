from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional

from app.schemas.nutrition import FoodSearchResponse, FoodProfile
from app.services.usda_service import usda_service
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/nutrition", tags=["nutrition"])

@router.get("/search", response_model=FoodSearchResponse)
async def search_ingredient(
    query: str = Query(..., description="Search term, e.g., 'chicken breast pan fried'"),
    require_all_words: bool = Query(True, description="Require all words in search query"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    current_user: User = Depends(get_current_user)
):
    """
    Search for food ingredients in the USDA FoodData Central database.
    This can be used to search for specific cooked ingredients.
    """
    try:
        response_data = await usda_service.search_foods(
            query=query, 
            require_all_words=require_all_words, 
            page_number=page
        )
        return response_data
    except Exception as e:
        # HTTPExceptions are raised from the service layer directly if the USDA API fails
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/food/{fdc_id}", response_model=FoodProfile)
async def get_food_profile(
    fdc_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get extensive details about a specific food item, including its complete nutrient profile.
    Extract the fdcId from the /search endpoint.
    """
    try:
        response_data = await usda_service.get_food_details(fdc_id)
        return response_data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

