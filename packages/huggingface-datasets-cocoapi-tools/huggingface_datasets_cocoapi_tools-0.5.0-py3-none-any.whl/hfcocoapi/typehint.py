import pathlib
from typing import Annotated, Any, Dict, List, Literal, Tuple, Union

from PIL.Image import Image
from typing_extensions import TypedDict

JsonDict = Annotated[
    Dict[str, Any],
    "Type for JSON-like dictionary",
]
ImageId = Annotated[
    int,
    "Type for image ID",
]
AnnotationId = Annotated[
    int,
    "Type for annotation ID",
]
LicenseId = Annotated[
    int,
    "Type for license ID",
]
CategoryId = Annotated[
    int,
    "Type for category ID",
]
Bbox = Annotated[
    Tuple[float, float, float, float],
    "Type for bounding box",
]

MscocoSplits = Literal["train", "val", "test"]

PilImage = Annotated[Image, "Pillow Image"]

PathLike = Annotated[
    Union[str, pathlib.Path],
    "Type for path-like object",
]


class CategoryDict(TypedDict):
    category_id: CategoryId
    name: str
    supercategory: str


class LicenseDict(TypedDict):
    license_id: LicenseId
    name: str
    url: str


class UncompressedRLE(TypedDict):
    counts: List[int]
    size: Tuple[int, int]


class CompressedRLE(TypedDict):
    counts: bytes
    size: Tuple[int, int]


class BaseExample(TypedDict):
    image_id: ImageId
    image: PilImage
    file_name: str
    coco_url: str
    height: int
    width: int
    date_captured: str
    flickr_url: str
    license_id: LicenseId
    license: LicenseDict
