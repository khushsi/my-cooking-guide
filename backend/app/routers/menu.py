from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.menu import (
    MenuGenerateRequest,
    MenuSwapRequest,
    MenuResponse,
    MenuListResponse,
)
from app.services.menu_service import MenuService

router = APIRouter(prefix="/api/menu", tags=["menu"])


@router.post("/generate", response_model=MenuResponse)
async def generate_menu(
    data: MenuGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new weekly menu using Gemini AI."""
    menu_service = MenuService(db)
    return await menu_service.generate_menu(data, current_user)


@router.get("/current", response_model=MenuResponse | None)
async def get_current_menu(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the menu for the current week."""
    menu_service = MenuService(db)
    return await menu_service.get_current_menu(current_user)


@router.get("/history", response_model=MenuListResponse)
async def get_menu_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=10, le=50),
    offset: int = Query(default=0, ge=0),
):
    """Get past weekly menus for the user (calendar history)."""
    menu_service = MenuService(db)
    return await menu_service.get_menu_history(current_user, limit, offset)


@router.get("/{menu_id}", response_model=MenuResponse)
async def get_menu(
    menu_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific menu by ID."""
    menu_service = MenuService(db)
    menu = await menu_service.get_menu_by_id(menu_id, current_user)
    return MenuResponse.model_validate(menu)


@router.post("/{menu_id}/swap", response_model=MenuResponse)
async def swap_meal(
    menu_id: str,
    data: MenuSwapRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Swap a single meal in an existing menu using Gemini Flash."""
    menu_service = MenuService(db)
    return await menu_service.swap_meal(menu_id, data, current_user)


@router.put("/{menu_id}/accept")
async def accept_menu(
    menu_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accept the generated menu (move from draft to accepted)."""
    menu_service = MenuService(db)
    return await menu_service.accept_menu(menu_id, current_user)
