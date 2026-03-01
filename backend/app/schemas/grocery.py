from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class GroceryItemBase(BaseModel):
    name: str
    quantity: str | None = None
    category: str | None = None

class GroceryItemCreate(GroceryItemBase):
    pass

class GroceryItemUpdate(BaseModel):
    name: str | None = None
    quantity: str | None = None
    category: str | None = None
    is_checked: bool | None = None

class GroceryItemResponse(GroceryItemBase):
    id: UUID
    is_checked: bool
    is_from_menu: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GroceryListResponse(BaseModel):
    items: list[GroceryItemResponse]
