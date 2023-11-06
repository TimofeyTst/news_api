from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Source(Base):
    __tablename__ = "source"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    texts = relationship("Text", back_populates="source")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    texts = relationship("Text", back_populates="category")


class SuperCategory(Base):
    __tablename__ = "supercategory"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    texts = relationship("Text", back_populates="supercategory")


class Text(Base):
    __tablename__ = "text"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    body = Column(String, nullable=False)
    link = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    source_id = Column(Integer, ForeignKey("source.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False, index=True)
    supercategory_id = Column(
        Integer, ForeignKey("supercategory.id"), nullable=False, index=True
    )

    source = relationship("Source", back_populates="texts")
    category = relationship("Category", back_populates="texts")
    supercategory = relationship("SuperCategory", back_populates="texts")
