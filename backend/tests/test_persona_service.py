import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.persona import Persona
from app.models.user import User
from app.services.persona_service import PersonaService

@pytest.mark.asyncio
async def test_get_household_requirements_aggregation(db: AsyncSession, test_user: User):
    service = PersonaService(db)
    
    # 1. Create Persona 1 (Vegan, Allergic to Nuts, Loves Tofu, spicy)
    p1 = Persona(
        id=uuid4(),
        user_id=test_user.id,
        name="Alice",
        diet_type="vegan",
        allergies=["Nuts"],
        medical_conditions=["Asthma"],
        loved_ingredients=["Tofu"],
        spice_tolerance="hot",
        target_calories=2000
    )
    db.add(p1)
    
    # 2. Create Persona 2 (Omnivore, Allergic to Dairy, Loves Chicken, mild spice)
    p2 = Persona(
        id=uuid4(),
        user_id=test_user.id,
        name="Bob",
        diet_type="omnivore",
        allergies=["Dairy"],
        medical_conditions=["Diabetes"],
        loved_ingredients=["Chicken"],
        spice_tolerance="mild",
        target_calories=2500
    )
    db.add(p2)
    await db.flush()
    
    # 3. Get aggregate
    reqs = await service.get_household_requirements(test_user.id)
    
    # Assertions
    assert reqs["persona_count"] == 2
    assert reqs["diet_type"] == "vegan" # Most restrictive
    assert reqs["spice_tolerance"] == "mild" # Least spicy
    assert set(reqs["allergies"]) == {"Nuts", "Dairy"}
    assert set(reqs["medical_conditions"]) == {"Asthma", "Diabetes"}
    assert set(reqs["loved_ingredients"]) == {"Tofu", "Chicken"}
    assert reqs["suggested_total_calories"] == 4500
