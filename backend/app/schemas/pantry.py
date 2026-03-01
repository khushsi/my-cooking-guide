"""Pydantic schemas for pantry data."""

from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class PantryItemBase(BaseModel):
    name: str
    quantity: float = 0.0
    unit: str | None = None
    category: str | None = None

class PantryItemCreate(PantryItemBase):
    pass

class PantryItemUpdate(BaseModel):
    name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None

class PantryItemResponse(PantryItemBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PantryBulkCreate(BaseModel):
    items: list[PantryItemCreate]
