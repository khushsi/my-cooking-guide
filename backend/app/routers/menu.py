from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.menu import (
    MenuGenerateRequest,
    MenuSwapRequest,
    MenuSwapIngredientRequest,
    MenuBoostMacroRequest,
    MenuResponse,
    MenuListResponse,
)
from app.services.menu_service import MenuService
from app.services.preference_service import background_evolve_persona

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
    menu_id: UUID,
    data: MenuSwapRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Swap a specific meal in a menu."""
    menu_service = MenuService(db)
    result = await menu_service.swap_meal(str(menu_id), data, current_user)
    
    if data.reason:
        background_tasks.add_task(background_evolve_persona, current_user.id, data.reason)
        
    return result


@router.post("/{menu_id}/swap-ingredient", response_model=list[dict])
async def swap_ingredient(
    menu_id: str,
    data: MenuSwapIngredientRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Suggest healthy swaps for a single ingredient in a meal."""
    menu_service = MenuService(db)
    return await menu_service.swap_ingredient(menu_id, data, current_user)


@router.post("/{menu_id}/boost-macro", response_model=list[dict])
async def boost_macro(
    menu_id: str,
    data: MenuBoostMacroRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Suggest add-ons to boost a specific macro (like protein)."""
    menu_service = MenuService(db)
    return await menu_service.boost_macro(menu_id, data, current_user)


@router.put("/{menu_id}/accept")
async def accept_menu(
    menu_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accept the generated menu (move from draft to accepted)."""
    menu_service = MenuService(db)
    return await menu_service.accept_menu(menu_id, current_user)
