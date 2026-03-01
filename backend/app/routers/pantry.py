"""Pantry router — CRUD for pantry items."""

from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.pantry import PantryItemCreate, PantryItemUpdate, PantryItemResponse, PantryBulkCreate
from app.services.pantry_service import PantryService
from app.services.gemini_service import analyze_fridge_image

router = APIRouter(prefix="/api/pantry", tags=["pantry"])

@router.post("/scan", response_model=list[PantryItemResponse])
async def scan_fridge_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Scan a fridge image and add items to pantry using multimodal AI."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")
        
    image_bytes = await file.read()
    
    extracted_items = await analyze_fridge_image(image_bytes, file.content_type)
    
    if not extracted_items:
        raise HTTPException(status_code=400, detail="Could not detect any items in the image.")
        
    pantry_items_data = []
    for item in extracted_items:
        try:
             # Ensure defaults if AI missed something
             if "category" not in item: item["category"] = "Pantry"
             if "unit" not in item: item["unit"] = "item"
             if "quantity" not in item: item["quantity"] = 1.0
             pantry_items_data.append(PantryItemCreate(**item))
        except Exception as e:
             print(f"Skipping malformed extracted item {item}: {e}")
             continue
             
    if not pantry_items_data:
         raise HTTPException(status_code=400, detail="Extracted items were malformed.")
    
    pantry_service = PantryService(db)
    return await pantry_service.bulk_create_items(current_user.id, pantry_items_data)

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
