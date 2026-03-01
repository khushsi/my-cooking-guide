"""SQLAlchemy models for weekly menus."""

import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WeeklyMenu(Base):
    __tablename__ = "weekly_menus"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    week_start: Mapped[date] = mapped_column(Date)  # Always a Saturday

    # Gemini-generated data stored as JSONB
    menu_data: Mapped[dict] = mapped_column(JSONB)  # Full 7-day plan
    grocery_list: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    prep_plan: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20), default="draft"
    )  # draft, accepted, completed

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="menus")
    feedbacks = relationship("MealFeedback", back_populates="menu", lazy="selectin")
