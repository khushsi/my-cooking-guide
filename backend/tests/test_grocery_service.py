import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.menu import WeeklyMenu
from app.models.grocery_item import GroceryItem
from app.services.grocery_service import GroceryListService
from app.schemas.grocery import GroceryItemCreate, GroceryItemUpdate

@pytest.mark.asyncio
async def test_get_grocery_list_empty(db: AsyncSession, test_user: User):
    service = GroceryListService(db)
    items = await service.get_grocery_list(test_user)
    assert len(items) == 0

@pytest.mark.asyncio
async def test_add_grocery_item(db: AsyncSession, test_user: User):
    service = GroceryListService(db)
    data = GroceryItemCreate(name="Milk", quantity="1 gallon", category="Dairy")
    item = await service.add_item(data, test_user)
    
    assert item.name == "Milk"
    assert item.quantity == "1 gallon"
    assert item.user_id == test_user.id
    assert item.is_checked is False

@pytest.mark.asyncio
async def test_update_grocery_item(db: AsyncSession, test_user: User):
    service = GroceryListService(db)
    # Add initial item
    data = GroceryItemCreate(name="Eggs", quantity="12", category="Dairy")
    item = await service.add_item(data, test_user)
    
    # Update it
    update_data = GroceryItemUpdate(is_checked=True)
    updated_item = await service.update_item(item.id, update_data, test_user)
    
    assert updated_item.is_checked is True
    assert updated_item.name == "Eggs"

@pytest.mark.asyncio
async def test_delete_grocery_item(db: AsyncSession, test_user: User):
    service = GroceryListService(db)
    data = GroceryItemCreate(name="Bread", quantity="1 loaf")
    item = await service.add_item(data, test_user)
    
    await service.delete_item(item.id, test_user)
    items = await service.get_grocery_list(test_user)
    assert len(items) == 0

@pytest.mark.asyncio
async def test_sync_from_menu_with_pantry(db: AsyncSession, test_user: User):
    from app.models.pantry_item import PantryItem
    service = GroceryListService(db)
    
    # 1. Add "Apples" to pantry
    pantry_item = PantryItem(
        id=uuid4(),
        user_id=test_user.id,
        name="Apples",
        quantity=5,
        unit="pcs",
        category="Fruit"
    )
    db.add(pantry_item)
    await db.flush()
    
    # 2. Create a mock menu with "Apples" and "Milk"
    menu = WeeklyMenu(
        id=uuid4(),
        user_id=test_user.id,
        week_start=pytest.importorskip("datetime").date.today(),
        menu_data={},
        grocery_list=[
            {"name": "Apples", "quantity": "3", "category": "Produce"},
            {"name": "Milk", "quantity": "1 gallon", "category": "Dairy"}
        ],
        status="accepted"
    )
    db.add(menu)
    await db.flush()
    
    # 3. Sync
    items = await service.sync_from_menu(menu.id, test_user)
    
    # Should only have "Milk" (Apples skipped because they are in pantry)
    names = [i.name for i in items]
    assert "Milk" in names
    assert "Apples" not in names
    assert all(i.is_from_menu for i in items)

@pytest.mark.asyncio
async def test_sync_from_menu(db: AsyncSession, test_user: User):
    service = GroceryListService(db)
    
    # Create a mock menu
    menu = WeeklyMenu(
        id=uuid4(),
        user_id=test_user.id,
        week_start=pytest.importorskip("datetime").date.today(),
        menu_data={},
        grocery_list=[
            {"name": "Apples", "quantity": "3", "category": "Produce"},
            {"name": "Bananas", "quantity": "1 bunch", "category": "Produce"}
        ],
        status="accepted"
    )
    db.add(menu)
    await db.flush()
    
    # Sync
    items = await service.sync_from_menu(menu.id, test_user)
    
    assert len(items) == 2
    names = [i.name for i in items]
    assert "Apples" in names
    assert "Bananas" in names
    assert all(i.is_from_menu for i in items)
