"""SQLAlchemy models for user profiles."""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Persona data (Primary user)
    persona_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Onboarding data
    household_size: Mapped[int] = mapped_column(Integer, default=1)
    diet_type: Mapped[str] = mapped_column(
        String(50), default="omnivore"
    )  # vegetarian, vegan, omnivore, pescatarian
    allergies: Mapped[dict | None] = mapped_column(JSONB, default=list)
    pantry_staples: Mapped[dict | None] = mapped_column(JSONB, default=list)
    meal_types: Mapped[dict | None] = mapped_column(
        JSONB, default=lambda: ["breakfast", "lunch", "dinner"]
    )

    # Advanced profile (progressive profiling)
    target_calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    macro_targets: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    energy_schedule: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # State
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    menus = relationship("WeeklyMenu", back_populates="user", lazy="selectin")
    feedbacks = relationship("MealFeedback", back_populates="user", lazy="selectin")
    personas = relationship("Persona", back_populates="user", lazy="selectin", cascade="all, delete-orphan")
