"""SQLAlchemy models for recipes."""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(String)
    
    # Core attributes for matching
    diet_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])  # ["vegetarian", "low-carb"]
    meal_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])  # ["breakfast", "lunch"]
    
    # Nutritional data
    calories: Mapped[int] = mapped_column(Integer, nullable=True)
    protein_g: Mapped[float] = mapped_column(Float, nullable=True)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=True)
    fat_g: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Recipe details
    ingredients: Mapped[list[dict]] = mapped_column(JSONB)  # Detailed list with amounts
    instructions: Mapped[list[str]] = mapped_column(JSONB)  # Step-by-step
    prep_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    cook_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "gemini-1.5-pro"
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
