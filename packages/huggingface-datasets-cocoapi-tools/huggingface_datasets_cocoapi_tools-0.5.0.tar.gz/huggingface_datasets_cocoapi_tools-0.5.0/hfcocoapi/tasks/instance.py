import abc
import logging
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from typing_extensions import Self

from hfcocoapi.models import ImageData
from hfcocoapi.typehint import CompressedRLE, ImageId, JsonDict, UncompressedRLE

from .annotation import AnnotationData

logger = logging.getLogger(__name__)

try:
    from pycocotools import mask as cocomask
except ImportError:
    logger.warning('Please install "pycocotools" to use this module')
    cocomask = None


def compress_rle(
    segmentation: Union[List[List[float]], UncompressedRLE],
    iscrowd: bool,
    height: int,
    width: int,
) -> CompressedRLE:
    assert cocomask is not None, "Please install 'pycocotools' to use this module"

    if iscrowd:
        rle = cocomask.frPyObjects(segmentation, h=height, w=width)
    else:
        rles = cocomask.frPyObjects(segmentation, h=height, w=width)
        rle = cocomask.merge(rles)

    return rle  # type: ignore


def rle_segmentation_to_binary_mask(
    segmentation, iscrowd: bool, height: int, width: int
) -> np.ndarray:
    rle = compress_rle(
        segmentation=segmentation, iscrowd=iscrowd, height=height, width=width
    )
    return cocomask.decode(rle)  # type: ignore


def rle_segmentation_to_mask(
    segmentation: Union[List[List[float]], UncompressedRLE],
    iscrowd: bool,
    height: int,
    width: int,
) -> np.ndarray:
    binary_mask = rle_segmentation_to_binary_mask(
        segmentation=segmentation, iscrowd=iscrowd, height=height, width=width
    )
    return binary_mask * 255


class BaseInstancesAnnotationData(AnnotationData, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def from_dict(
        cls,
        json_dict: JsonDict,
        images: Dict[ImageId, ImageData],
        decode_rle: bool,
    ) -> Self:
        """
        Convert a JSON dictionary to an instance of the annotation data class.

        Args:
            json_dict (JsonDict): The JSON dictionary containing annotation data.
            images (Dict[ImageId, ImageData]): A mapping of image IDs to image data.
            decode_rle (bool): Whether to decode RLE segmentation.

        Returns:
            Self: An instance of the annotation data class.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class InstancesAnnotationData(BaseInstancesAnnotationData):
    segmentation: Optional[Union[np.ndarray, CompressedRLE]]
    area: float
    iscrowd: bool
    bbox: Tuple[float, float, float, float]
    category_id: int

    @classmethod
    def from_dict(
        cls,
        json_dict: JsonDict,
        images: Dict[ImageId, ImageData],
        decode_rle: bool,
    ) -> Self:
        segmentation = json_dict.pop("segmentation")
        image_id = json_dict.pop("image_id")
        iscrowd = bool(json_dict.get("iscrowd", False))

        if len(segmentation) == 0:
            return cls(
                image_id=image_id,
                segmentation=None,
                iscrowd=iscrowd,
                **json_dict,
            )

        image_data = images[image_id]

        segmentation_mask = (
            rle_segmentation_to_mask(
                segmentation=segmentation,
                iscrowd=iscrowd,
                height=image_data.height,
                width=image_data.width,
            )
            if decode_rle
            else compress_rle(
                segmentation=segmentation,
                iscrowd=iscrowd,
                height=image_data.height,
                width=image_data.width,
            )
        )
        return cls(
            image_id=image_id,
            segmentation=segmentation_mask,  # type: ignore
            **json_dict,
        )
