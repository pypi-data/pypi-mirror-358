from pydantic import BaseModel


class AnnotationInfo(BaseModel):
    description: str
    url: str
    version: str
    year: str
    contributor: str
    date_created: str
