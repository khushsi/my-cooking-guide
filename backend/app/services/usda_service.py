import httpx
from typing import Optional
from fastapi import HTTPException
from app.config import get_settings

settings = get_settings()

class USDAService:
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"

    def __init__(self):
        self.api_key = settings.usda_api_key
        if not self.api_key:
            print("WARNING: USDA_API_KEY is not set. USDA integration will fail.")

    async def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Helper method to make async requests to the USDA API."""
        if params is None:
            params = {}
        params['api_key'] = self.api_key

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/{endpoint}", params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # USDA API specific error handling
                error_msg = f"USDA API returned status {e.response.status_code}"
                try:
                    error_detail = e.response.json()
                    if 'error' in error_detail:
                        error_msg = f"USDA API Error: {error_detail['error'].get('message', 'Unknown error')}"
                except ValueError:
                    pass
                raise HTTPException(status_code=e.response.status_code, detail=error_msg)
            except httpx.RequestError as e:
                raise HTTPException(status_code=503, detail=f"Failed to connect to USDA API: {str(e)}")

    async def search_foods(self, query: str, require_all_words: bool = True, page_number: int = 1) -> dict:
        """
        Search for foods by keywords.
        Supports filtering by data type in the future (e.g., Foundation, SR Legacy).
        """
        params = {
            "query": query,
            "requireAllWords": str(require_all_words).lower(),
            "pageNumber": page_number,
        }
        return await self._make_request("foods/search", params)

    async def get_food_details(self, fdc_id: int) -> dict:
        """Fetch extensive details, including macronutrients, for a given fdc_id."""
        return await self._make_request(f"food/{fdc_id}")

usda_service = USDAService()
