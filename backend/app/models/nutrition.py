from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base

class CachedIngredient(Base):
    __tablename__ = "cached_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CachedIngredient(name='{self.name}', calories={self.calories})>"
