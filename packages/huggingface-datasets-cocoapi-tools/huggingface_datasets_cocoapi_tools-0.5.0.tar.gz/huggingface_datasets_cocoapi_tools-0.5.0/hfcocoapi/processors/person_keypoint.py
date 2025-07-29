from __future__ import annotations

import logging
import os
from collections import defaultdict
from typing import Dict, Iterator, List, Optional, Sequence, Tuple, TypedDict

import datasets as ds
from hfcocoapi.const import COCO_CATEGORIES, COCO_SUPER_CATEGORIES
from hfcocoapi.models import CategoryData, ImageData, LicenseData
from hfcocoapi.tasks import PersonKeypointsAnnotationData
from hfcocoapi.typehint import BaseExample, CategoryId, ImageId, JsonDict, LicenseId
from hfcocoapi.utils import tqdm

from .instances import InstanceAnnotationDict, InstancesProcessor

logger = logging.getLogger(__name__)


class KeypointDict(TypedDict):
    x: int
    y: int
    v: int
    state: str


class PersonKeypointAnnotationDict(InstanceAnnotationDict):
    num_keypoints: int
    keypoints: List[KeypointDict]


class PersonKeypointExample(BaseExample):
    annotations: List[PersonKeypointAnnotationDict]


class PersonKeypointsProcessor(InstancesProcessor):
    def get_features(
        self,
        decode_rle: bool,
        categories: Sequence[str] = COCO_CATEGORIES,
        super_categories: Sequence[str] = COCO_SUPER_CATEGORIES,
    ) -> ds.Features:
        features_dict = self.get_features_base_dict()
        features_instance_dict = self.get_features_instance_dict(
            decode_rle=decode_rle,
            categories=categories,
            super_categories=super_categories,
        )
        features_instance_dict.update(
            {
                "keypoints": ds.Sequence(
                    {
                        "state": ds.Value("string"),
                        "x": ds.Value("int32"),
                        "y": ds.Value("int32"),
                        "v": ds.Value("int32"),
                    }
                ),
                "num_keypoints": ds.Value("int32"),
            }
        )
        annotations = ds.Sequence(features_instance_dict)
        features_dict.update({"annotations": annotations})
        return ds.Features(features_dict)

    def load_data(  # type: ignore[override]
        self,
        ann_dicts: List[JsonDict],
        images: Dict[ImageId, ImageData],
        decode_rle: bool,
        tqdm_desc: str = "Load person keypoints data",
    ) -> Dict[ImageId, List[PersonKeypointsAnnotationData]]:
        annotations = defaultdict(list)
        ann_dicts = sorted(ann_dicts, key=lambda d: d["image_id"])

        for ann_dict in tqdm(ann_dicts, desc=tqdm_desc):
            ann_data = PersonKeypointsAnnotationData.from_dict(
                ann_dict, images=images, decode_rle=decode_rle
            )
            annotations[ann_data.image_id].append(ann_data)
        return annotations

    def generate_examples(  # type: ignore[override]
        self,
        image_dir: str,
        images: Dict[ImageId, ImageData],
        annotations: Dict[ImageId, List[PersonKeypointsAnnotationData]],
        categories: Dict[CategoryId, CategoryData],
        licenses: Optional[Dict[LicenseId, LicenseData]] = None,
    ) -> Iterator[Tuple[int, PersonKeypointExample]]:
        for idx, image_id in enumerate(images.keys()):
            image_data = images[image_id]
            image_anns = annotations[image_id]

            if len(image_anns) < 1:
                # If there are no persons in the image,
                # no keypoint annotations will be assigned.
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
