from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    cooking_time = Column(Integer, nullable=False)
    views = Column(Integer, default=0)
    ingredients = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
