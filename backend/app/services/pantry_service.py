from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException
from app.models.pantry_item import PantryItem
from app.schemas.pantry import PantryItemCreate, PantryItemUpdate

class PantryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_items(self, user_id: UUID) -> list[PantryItem]:
        stmt = select(PantryItem).where(PantryItem.user_id == user_id).order_by(PantryItem.category, PantryItem.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_item(self, user_id: UUID, data: PantryItemCreate) -> PantryItem:
        new_item = PantryItem(
            **data.model_dump(),
            user_id=user_id
        )
        self.db.add(new_item)
        await self.db.flush()
        return new_item

    async def bulk_create_items(self, user_id: UUID, items: list[PantryItemCreate]) -> list[PantryItem]:
        created_items = []
        for item_data in items:
            new_item = PantryItem(
                **item_data.model_dump(),
                user_id=user_id
            )
            self.db.add(new_item)
            created_items.append(new_item)
        await self.db.flush()
        return created_items

    async def update_item(self, user_id: UUID, item_id: UUID, data: PantryItemUpdate) -> PantryItem:
        stmt = select(PantryItem).where(PantryItem.id == item_id, PantryItem.user_id == user_id)
        result = await self.db.execute(stmt)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Pantry item not found")
            
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
            
        await self.db.flush()
        return item

    async def delete_item(self, user_id: UUID, item_id: UUID):
        stmt = delete(PantryItem).where(PantryItem.id == item_id, PantryItem.user_id == user_id)
        await self.db.execute(stmt)
        await self.db.flush()

    async def get_staples_for_menu(self, user_id: UUID) -> list[str]:
        """Get names of all pantry items to assist Gemini in meal planning."""
        stmt = select(PantryItem.name).where(PantryItem.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
