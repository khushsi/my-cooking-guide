import os
import re
import json
import requests
from typing import List, Dict

# The user's list provided in the prompt
RAW_LIST = """
Vegetables
Bottle gourd (1)
Cabbage
Carrot
Carrot Red (for raw eating)
Cauliflower
Chaudi (Sabji)
Chilli Long
Cucumber (9)
Eggplant (small - 5)
Garlic
Gooseberries (amla)
Okra

Leafy Greens & Herbs
Coriander
Curry Leaves
Methi
Mint
Spinach

Fruits
Apple (5)
Banana
Blueberries (2 servings)
Cantaloupe
Oranges (10)
Strawberries (6oz)

Dairy & Eggs
Eggs
Kirkland egg whites
Milk
Paneer
Yogurt (2kg)

Frozen & Refrigerated
Frozen karela
Frozen tindoda
Grana Valor frozen
Olives (platters 1.7 lb)

Pantry & Snacks
Chana masala (ready to eat - 5 packs)
Deep Plantain Chips (200GM)
Maggie

Bakery
Bread (homemade - good for next week)
"""

def parse_grocery_list(text: str) -> List[Dict]:
    items = []
    current_category = "General"
    
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # If the line is a known category header
        if line in ["Vegetables", "Leafy Greens & Herbs", "Fruits", "Dairy & Eggs", "Frozen & Refrigerated", "Pantry & Snacks", "Bakery"]:
            current_category = line
            continue
            
        # Try to parse name and quantity/unit
        # Examples: "Bottle gourd (1)", "Cucumber (9)", "Eggplant (small - 5)", "Yogurt (2kg)", "Strawberries (6oz)"
        
        name = line
        quantity = 1.0
        unit = "unit"
        
        # Regex to find (quantity unit) or (quantity)
        match = re.search(r'\((.*?)\)', line)
        if match:
            content = match.group(1)
            name = line.replace(match.group(0), "").strip()
            
            # Try to split quality and unit
            # "2kg" -> 2.0, "kg"
            # "6oz" -> 6.0, "oz"
            # "1" -> 1.0, "unit"
            unit_match = re.search(r'([\d\.]+)\s*([a-zA-Z]*)', content)
            if unit_match:
                quantity = float(unit_match.group(1))
                unit = unit_match.group(2) or "unit"
            else:
                unit = content # fallback
        
        items.append({
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "category": current_category
        })
        
    return items

def upload_to_pantry(items: List[Dict], api_base: str, token: str):
    url = f"{api_base}/api/pantry/bulk"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json={"items": items}, headers=headers)
    if response.status_code == 200:
        print(f"Successfully uploaded {len(items)} items to pantry.")
    else:
        print(f"Failed to upload items: {response.status_code} - {response.text}")

if __name__ == "__main__":
    parsed_items = parse_grocery_list(RAW_LIST)
    print(f"Parsed {len(parsed_items)} items.")
    
    # In a real scenario, we'd need a valid token. 
    # For now, we'll just save the JSON to a file or print it.
    with open("parsed_pantry.json", "w") as f:
        json.dump({"items": parsed_items}, f, indent=2)
    
    print("Parsed items saved to parsed_pantry.json")
