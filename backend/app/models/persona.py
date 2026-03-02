"""SQLAlchemy models for personas (individual profiles within a household)."""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    
    # Core identity
    name: Mapped[str] = mapped_column(String(255))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    template_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Health & Dietary Restrictions
    diet_type: Mapped[str] = mapped_column(String(50), default="omnivore")
    allergies: Mapped[list | None] = mapped_column(JSONB, default=list)
    medical_conditions: Mapped[list | None] = mapped_column(JSONB, default=list)

    # Taste & Preferences
    disliked_ingredients: Mapped[list | None] = mapped_column(JSONB, default=list)
    loved_ingredients: Mapped[list | None] = mapped_column(JSONB, default=list)
    spice_tolerance: Mapped[str] = mapped_column(String(50), default="medium")
    
    # Advanced Nutrition Preferences
    preferred_protein_sources: Mapped[list | None] = mapped_column(JSONB, default=list)
    avoided_protein_sources: Mapped[list | None] = mapped_column(JSONB, default=list)
    sneak_in_protein: Mapped[bool] = mapped_column(Boolean, default=False)

    # Goals & Attributes
    target_calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # State
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="personas", lazy="selectin")
