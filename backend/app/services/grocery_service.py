from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException
from app.models.user import User
from app.models.grocery_item import GroceryItem
from app.models.menu import WeeklyMenu
from app.schemas.grocery import GroceryItemCreate, GroceryItemUpdate

class GroceryListService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_grocery_list(self, current_user: User) -> list[GroceryItem]:
        result = await self.db.execute(
            select(GroceryItem)
            .where(GroceryItem.user_id == current_user.id)
            .order_by(GroceryItem.is_checked.asc(), GroceryItem.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_item(self, data: GroceryItemCreate, current_user: User) -> GroceryItem:
        item = GroceryItem(
            id=uuid4(),
            user_id=current_user.id,
            name=data.name,
            quantity=data.quantity,
            category=data.category,
            is_checked=False,
            is_from_menu=False
        )
        self.db.add(item)
        await self.db.flush()
        return item

    async def update_item(self, item_id: UUID, data: GroceryItemUpdate, current_user: User) -> GroceryItem:
        result = await self.db.execute(
            select(GroceryItem).where(
                GroceryItem.id == item_id,
                GroceryItem.user_id == current_user.id
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Grocery item not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)

        await self.db.flush()
        return item

    async def delete_item(self, item_id: UUID, current_user: User):
        await self.db.execute(
            delete(GroceryItem).where(
                GroceryItem.id == item_id,
                GroceryItem.user_id == current_user.id
            )
        )
        await self.db.flush()

    async def sync_from_menu(self, menu_id: UUID, current_user: User) -> list[GroceryItem]:
        # Get the menu
        result = await self.db.execute(
            select(WeeklyMenu).where(
                WeeklyMenu.id == menu_id,
                WeeklyMenu.user_id == current_user.id
            )
        )
        menu = result.scalar_one_or_none()
        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found")

        if not menu.grocery_list:
            return []

        # Smart sync: Only add items that aren't already in the pantry with quantity > 0
        from app.models.pantry_item import PantryItem
        pantry_result = await self.db.execute(
            select(PantryItem.name).where(
                PantryItem.user_id == current_user.id,
                PantryItem.quantity > 0
            )
        )
        pantry_names = {name.lower() for name in pantry_result.scalars().all()}
        
        # Also avoid duplicates in the grocery list itself
        existing_result = await self.db.execute(
            select(GroceryItem.name).where(GroceryItem.user_id == current_user.id)
        )
        existing_grocery_names = {name.lower() for name in existing_result.scalars().all()}

        new_items = []
        for item_data in menu.grocery_list:
            name = item_data.get("name")
            if not name:
                continue
            
            name_lower = name.lower()
            # If item is in pantry or already in grocery list, skip it
            if name_lower in pantry_names or name_lower in existing_grocery_names:
                continue

            item = GroceryItem(
                id=uuid4(),
                user_id=current_user.id,
                name=name,
                quantity=item_data.get("quantity"),
                category=item_data.get("category"),
                is_checked=False,
                is_from_menu=True
            )
            self.db.add(item)
            new_items.append(item)
        
        await self.db.flush()
        return await self.get_grocery_list(current_user)
