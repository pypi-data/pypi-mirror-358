from __future__ import annotations

import logging
import os
from collections import defaultdict
from typing import Dict, Iterator, List, Optional, Sequence, Tuple, Type, TypedDict

import numpy as np

import datasets as ds
from hfcocoapi.const import COCO_CATEGORIES, COCO_SUPER_CATEGORIES
from hfcocoapi.models import CategoryData, ImageData, LicenseData
from hfcocoapi.processors import MsCocoProcessor
from hfcocoapi.tasks import InstancesAnnotationData
from hfcocoapi.typehint import (
    AnnotationId,
    BaseExample,
    Bbox,
    CategoryDict,
    CategoryId,
    ImageId,
    JsonDict,
    LicenseId,
    PathLike,
)
from hfcocoapi.utils import tqdm

logger = logging.getLogger(__name__)


class InstanceAnnotationDict(TypedDict):
    annotation_id: AnnotationId
    area: float
    bbox: Bbox
    image_id: ImageId
    category_id: CategoryId
    category: CategoryDict
    iscrowd: bool
    segmentation: np.ndarray


class InstanceExample(BaseExample):
    annotations: List[InstanceAnnotationDict]


class InstancesProcessor(MsCocoProcessor):
    def get_features_instance_dict(
        self,
        decode_rle: bool,
        categories: Sequence[str] = COCO_CATEGORIES,
        super_categories: Sequence[str] = COCO_SUPER_CATEGORIES,
    ):
        import datasets as ds

        segmentation_feature = (
            ds.Image()
            if decode_rle
            else {
                "counts": ds.Sequence(ds.Value("int64")),
                "size": ds.Sequence(ds.Value("int32")),
            }
        )
        return {
            "annotation_id": ds.Value("int64"),
            "image_id": ds.Value("int64"),
            "segmentation": segmentation_feature,
            "area": ds.Value("float32"),
            "iscrowd": ds.Value("bool"),
            "bbox": ds.Sequence(ds.Value("float32"), length=4),
            "category_id": ds.Value("int32"),
            "category": {
                "category_id": ds.Value("int32"),
                "name": ds.ClassLabel(
                    num_classes=len(categories),
                    names=categories,
                ),
                "supercategory": ds.ClassLabel(
                    num_classes=len(super_categories),
                    names=super_categories,
                ),
            },
        }

    def get_features(
        self,
        decode_rle: bool,
        categories: Sequence[str] = COCO_CATEGORIES,
        super_categories: Sequence[str] = COCO_SUPER_CATEGORIES,
    ) -> ds.Features:
        features_dict = self.get_features_base_dict()
        annotations = ds.Sequence(
            self.get_features_instance_dict(
                decode_rle=decode_rle,
                categories=categories,
                super_categories=super_categories,
            )
        )
        features_dict.update({"annotations": annotations})
        return ds.Features(features_dict)

    def load_data(  # type: ignore[override]
        self,
        ann_dicts: List[JsonDict],
        images: Dict[ImageId, ImageData],
        decode_rle: bool,
        instances_annotation_class: Type[
            InstancesAnnotationData
        ] = InstancesAnnotationData,
        tqdm_desc: str = "Load instances data",
    ) -> Dict[ImageId, List[InstancesAnnotationData]]:
        annotations = defaultdict(list)
        ann_dicts = sorted(ann_dicts, key=lambda d: d["image_id"])

        for ann_dict in tqdm(ann_dicts, desc=tqdm_desc):
            ann_data = instances_annotation_class.from_dict(
                ann_dict, images=images, decode_rle=decode_rle
            )
            annotations[ann_data.image_id].append(ann_data)

        return annotations

    def generate_examples(  # type: ignore[override]
        self,
        image_dir: PathLike,
        images: Dict[ImageId, ImageData],
        annotations: Dict[ImageId, List[InstancesAnnotationData]],
        categories: Dict[CategoryId, CategoryData],
        licenses: Optional[Dict[LicenseId, LicenseData]] = None,
    ) -> Iterator[Tuple[int, InstanceExample]]:
        for idx, image_id in enumerate(images.keys()):
            image_data = images[image_id]
            image_anns = annotations[image_id]

            if len(image_anns) < 1:
                logger.warning(f"No annotation found for image id: {image_id}.")
                continue

            image = self.load_image(
                image_path=os.path.join(image_dir, image_data.file_name),
            )
            example = image_data.model_dump()
            example["image"] = image

            if licenses and image_data.license_id is not None:
                example["license"] = licenses[image_data.license_id].model_dump()

            example["annotations"] = []
            for ann in image_anns:
                ann_dict = ann.model_dump()
                category = categories[ann.category_id]
                ann_dict["category"] = category.model_dump()
                example["annotations"].append(ann_dict)

            yield idx, example  # type: ignore
