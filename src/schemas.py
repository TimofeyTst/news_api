from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class SourceBase(BaseModel):
    name: str


class SourceCreate(SourceBase):
    pass


class SourceRead(SourceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)  # type: ignore


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int


class SuperCategoryBase(BaseModel):
    name: str


class SuperCategoryCreate(SuperCategoryBase):
    pass


class SuperCategoryRead(SuperCategoryBase):
    id: int


class TextBase(BaseModel):
    title: str
    body: str
    link: Optional[HttpUrl]
    source_id: int
    category_id: int
    supercategory_id: int


class TextCreate(TextBase):
    pass


class TextRead(TextBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)  # type: ignore
