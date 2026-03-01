"""SQLAlchemy models for meal feedback (learning loop)."""

import uuid
from datetime import date, datetime

from sqlalchemy import String, Integer, Boolean, Date, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MealFeedback(Base):
    __tablename__ = "meal_feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    menu_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("weekly_menus.id", ondelete="CASCADE"),
        index=True,
    )

    meal_date: Mapped[date] = mapped_column(Date)
    meal_type: Mapped[str] = mapped_column(
        String(20)
    )  # breakfast, lunch, dinner, snack

    was_cooked: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[int] = mapped_column(
        Integer, default=0
    )  # -1 (dislike), 0 (neutral), 1 (like)
    effort_accuracy: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # too_hard, just_right, too_easy
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="feedbacks")
    menu = relationship("WeeklyMenu", back_populates="feedbacks")
