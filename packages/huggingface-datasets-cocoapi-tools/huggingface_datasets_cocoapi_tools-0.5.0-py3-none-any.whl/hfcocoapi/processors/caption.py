from __future__ import annotations

import logging
import os
from collections import defaultdict
from typing import Dict, Iterator, List, Optional, Tuple, Type, TypedDict

import datasets as ds

from hfcocoapi.models import ImageData, LicenseData
from hfcocoapi.processors import MsCocoProcessor
from hfcocoapi.tasks import CaptionsAnnotationData
from hfcocoapi.typehint import (
    AnnotationId,
    BaseExample,
    ImageId,
    JsonDict,
    LicenseId,
    PathLike,
)
from hfcocoapi.utils import tqdm

logger = logging.getLogger(__name__)


class CaptionAnnotationDict(TypedDict):
    annotation_id: AnnotationId
    caption: str


class CaptionExample(BaseExample):
    annotations: List[CaptionAnnotationDict]


class CaptionsProcessor(MsCocoProcessor):
    def get_features(self, *args, **kwargs) -> ds.Features:
        import datasets as ds

        features_dict = self.get_features_base_dict()
        annotations = ds.Sequence(
            {
                "annotation_id": ds.Value("int64"),
                "image_id": ds.Value("int64"),
                "caption": ds.Value("string"),
            }
        )
        features_dict.update({"annotations": annotations})
        return ds.Features(features_dict)

    def load_data(  # type: ignore[override]
        self,
        ann_dicts: List[JsonDict],
        captions_annotation_class: Type[
            CaptionsAnnotationData
        ] = CaptionsAnnotationData,
        tqdm_desc: str = "Load captions data",
        **kwargs,
    ) -> Dict[ImageId, List[CaptionsAnnotationData]]:
        annotations = defaultdict(list)
        for ann_dict in tqdm(ann_dicts, desc=tqdm_desc):
            ann_data = captions_annotation_class(**ann_dict)
            annotations[ann_data.image_id].append(ann_data)
        return annotations

    def generate_examples(  # type: ignore[override]
        self,
        images: Dict[ImageId, ImageData],
        annotations: Dict[ImageId, List[CaptionsAnnotationData]],
        image_dir: Optional[PathLike] = None,
        licenses: Optional[Dict[LicenseId, LicenseData]] = None,
        **kwargs,
    ) -> Iterator[Tuple[int, CaptionExample]]:
        for idx, image_id in enumerate(images.keys()):
            image_data = images[image_id]
            image_anns = annotations[image_id]

            assert len(image_anns) > 0

            image = (
                self.load_image(
                    image_path=os.path.join(image_dir, image_data.file_name),
                )
                if image_dir is not None
                else None
            )
            example = image_data.model_dump()
            example["image"] = image

            if licenses and image_data.license_id is not None:
                example["license"] = licenses[image_data.license_id].model_dump()

            example["annotations"] = []
            for ann in image_anns:
                example["annotations"].append(ann.model_dump())

            yield idx, example  # type: ignore
