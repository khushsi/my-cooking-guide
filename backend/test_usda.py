import asyncio
import os
from app.services.usda_service import USDAService

async def test_usda_api():
    # Retrieve the key from the environment
    api_key = os.getenv("USDA_API_KEY")
    if not api_key:
        print("ERROR: USDA_API_KEY environment variable is missing.")
        print("Please add it to your .env file or export it in your terminal.")
        return
        
    print(f"Testing USDA API with key: {api_key[:5]}...")

    # We manually map the key to test since the settings might not reload in this isolated script
    usda_service = USDAService()
    usda_service.api_key = api_key
    
    try:
        print("\n--- Testing Search (query: 'chicken breast pan fried') ---")
        search_results = await usda_service.search_foods(query="chicken breast pan fried")
        
        foods = search_results.get("foods", [])
        print(f"Found {len(foods)} results.")
        
        if foods:
            first_food = foods[0]
            fdc_id = first_food.get("fdcId")
            desc = first_food.get("description")
            print(f"Top result: [{fdc_id}] {desc}")
            
            print(f"\n--- Testing Details (fdc_id: {fdc_id}) ---")
            details = await usda_service.get_food_details(fdc_id)
            print(f"Details fetched successfully for {details.get('description')}")
            
            # Print some macros
            print("Macronutrients:")
            nutrients = details.get("foodNutrients", [])
            for n in nutrients:
                n_info = n.get("nutrient", {})
                name = n_info.get("name", "")
                if name in ["Protein", "Total lipid (fat)", "Carbohydrate, by difference", "Energy"]:
                    print(f"- {name}: {n.get('amount')} {n_info.get('unitName')}")
        else:
            print("No foods found.")
            
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_usda_api())
