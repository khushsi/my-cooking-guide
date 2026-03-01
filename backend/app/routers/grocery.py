from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.grocery import (
    GroceryItemCreate,
    GroceryItemUpdate,
    GroceryItemResponse,
    GroceryListResponse,
)
from app.services.grocery_service import GroceryListService

router = APIRouter(prefix="/api/grocery-list", tags=["grocery"])

@router.get("", response_model=GroceryListResponse)
async def get_grocery_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GroceryListService(db)
    items = await service.get_grocery_list(current_user)
    return GroceryListResponse(items=items)

@router.post("", response_model=GroceryItemResponse)
async def add_grocery_item(
    data: GroceryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GroceryListService(db)
    return await service.add_item(data, current_user)

@router.patch("/{item_id}", response_model=GroceryItemResponse)
async def update_grocery_item(
    item_id: UUID,
    data: GroceryItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GroceryListService(db)
    return await service.update_item(item_id, data, current_user)

@router.delete("/{item_id}")
async def delete_grocery_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GroceryListService(db)
    await service.delete_item(item_id, current_user)
    return {"status": "deleted"}

@router.post("/sync/{menu_id}", response_model=GroceryListResponse)
async def sync_from_menu(
    menu_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GroceryListService(db)
    items = await service.sync_from_menu(menu_id, current_user)
    return GroceryListResponse(items=items)
