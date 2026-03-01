"""Pantry router — CRUD for pantry items."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.pantry_item import PantryItem
from app.routers.auth import get_current_user
from app.schemas.pantry import PantryItemCreate, PantryItemUpdate, PantryItemResponse, PantryBulkCreate

router = APIRouter(prefix="/api/pantry", tags=["pantry"])

@router.get("/", response_model=list[PantryItemResponse])
async def get_pantry(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all pantry items for the current user."""
    stmt = select(PantryItem).where(PantryItem.user_id == current_user.id).order_by(PantryItem.category, PantryItem.name)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=PantryItemResponse)
async def create_pantry_item(
    data: PantryItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new pantry item."""
    new_item = PantryItem(
        **data.model_dump(),
        user_id=current_user.id
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

@router.post("/bulk", response_model=list[PantryItemResponse])
async def bulk_create_pantry_items(
    data: PantryBulkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk create pantry items."""
    created_items = []
    for item_data in data.items:
        new_item = PantryItem(
            **item_data.model_dump(),
            user_id=current_user.id
        )
        db.add(new_item)
        created_items.append(new_item)
    
    await db.commit()
    for item in created_items:
        await db.refresh(item)
    return created_items

@router.patch("/{item_id}", response_model=PantryItemResponse)
async def update_pantry_item(
    item_id: UUID,
    data: PantryItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a pantry item."""
    stmt = select(PantryItem).where(PantryItem.id == item_id, PantryItem.user_id == current_user.id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{item_id}")
async def delete_pantry_item(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a pantry item."""
    stmt = delete(PantryItem).where(PantryItem.id == item_id, PantryItem.user_id == current_user.id)
    await db.execute(stmt)
    await db.commit()
    return {"status": "success"}
