from typing import Optional

from pydantic import BaseModel, Field


class ImageData(BaseModel):
    image_id: int = Field(alias="id")
    license_id: Optional[int] = Field(default=None, alias="license")
    file_name: str
    height: int
    width: int
    coco_url: Optional[str] = None
    date_captured: Optional[str] = None
    flickr_url: Optional[str] = None
