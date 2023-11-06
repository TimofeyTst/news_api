from pydantic import BaseModel, ConfigDict

from src.schemas import CategoryRead, SourceRead, SuperCategoryRead, TextRead


class DatasetRead(BaseModel):
    sources: list[SourceRead]
    categories: list[CategoryRead]
    supercategories: list[SuperCategoryRead]
    texts: list[TextRead]

    model_config = ConfigDict(from_attributes=True)  # type: ignore
