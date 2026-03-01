from pydantic import BaseModel, Field
from typing import List, Optional

class NutrientInfo(BaseModel):
    nutrient_id: int = Field(alias="nutrientId")
    nutrient_name: str = Field(alias="nutrientName")
    nutrient_number: str = Field(alias="nutrientNumber")
    unit_name: str = Field(alias="unitName")
    value: float
    derivation_code: Optional[str] = Field(None, alias="derivationCode")
    derivation_description: Optional[str] = Field(None, alias="derivationDescription")

class FoodSearchItem(BaseModel):
    fdc_id: int = Field(alias="fdcId")
    description: str
    food_category: Optional[str] = Field(None, alias="foodCategory")
    scientific_name: Optional[str] = Field(None, alias="scientificName")
    additional_descriptions: Optional[str] = Field(None, alias="additionalDescriptions")
    ndb_number: Optional[str] = Field(None, alias="ndbNumber")
    published_date: Optional[str] = Field(None, alias="publishedDate")
    food_nutrients: Optional[List[NutrientInfo]] = Field(None, alias="foodNutrients")

class FoodSearchResponse(BaseModel):
    total_hits: int = Field(alias="totalHits")
    current_page: int = Field(alias="currentPage")
    total_pages: int = Field(alias="totalPages")
    page_list: List[int] = Field(alias="pageList")
    food_search_criteria: dict = Field(alias="foodSearchCriteria")
    foods: List[FoodSearchItem]

class FoodProfile(BaseModel):
    fdc_id: int = Field(alias="fdcId")
    description: str
    food_category: Optional[dict] = Field(None, alias="foodCategory")
    food_nutrients: List[dict] = Field(alias="foodNutrients")
    
    # Optional fields that might be useful
    ndb_number: Optional[str] = Field(None, alias="ndbNumber")
    scientific_name: Optional[str] = Field(None, alias="scientificName")
