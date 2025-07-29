from pydantic import BaseModel, ConfigDict, Field


class AnnotationData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    annotation_id: int = Field(alias="id")
    image_id: int
