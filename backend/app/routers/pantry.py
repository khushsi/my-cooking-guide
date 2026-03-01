"""Pantry router — CRUD for pantry items."""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.pantry import PantryItemCreate, PantryItemUpdate, PantryItemResponse, PantryBulkCreate
from app.services.pantry_service import PantryService

router = APIRouter(prefix="/api/pantry", tags=["pantry"])

@router.get("/", response_model=list[PantryItemResponse])
async def get_pantry(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all pantry items for the current user."""
    pantry_service = PantryService(db)
    return await pantry_service.get_all_items(current_user.id)

@router.post("/", response_model=PantryItemResponse)
async def create_pantry_item(
    data: PantryItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new pantry item."""
    pantry_service = PantryService(db)
    return await pantry_service.create_item(current_user.id, data)

@router.post("/bulk", response_model=list[PantryItemResponse])
async def bulk_create_pantry_items(
    data: PantryBulkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk create pantry items."""
    pantry_service = PantryService(db)
    return await pantry_service.bulk_create_items(current_user.id, data.items)

@router.patch("/{item_id}", response_model=PantryItemResponse)
async def update_pantry_item(
    item_id: UUID,
    data: PantryItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a pantry item."""
    pantry_service = PantryService(db)
    return await pantry_service.update_item(current_user.id, item_id, data)

@router.delete("/{item_id}")
async def delete_pantry_item(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a pantry item."""
    pantry_service = PantryService(db)
    await pantry_service.delete_item(current_user.id, item_id)
    return {"status": "success"}
