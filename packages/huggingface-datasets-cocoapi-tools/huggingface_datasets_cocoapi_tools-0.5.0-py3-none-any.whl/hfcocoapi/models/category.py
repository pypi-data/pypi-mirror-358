from pydantic import BaseModel, Field


class CategoryData(BaseModel):
    category_id: int = Field(alias="id")
    name: str
    supercategory: str
