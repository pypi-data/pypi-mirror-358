from typing import Dict, Final, List, Literal

from pydantic import BaseModel
from typing_extensions import Self

from hfcocoapi.models import ImageData
from hfcocoapi.typehint import ImageId, JsonDict

from .instance import InstancesAnnotationData, compress_rle, rle_segmentation_to_mask

KeypointState = Literal["unknown", "invisible", "visible"]
KEYPOINT_STATES: Final[List[KeypointState]] = ["unknown", "invisible", "visible"]


class PersonKeypoint(BaseModel):
    x: int
    y: int
    v: int
    state: str


class PersonKeypointsAnnotationData(InstancesAnnotationData):
    num_keypoints: int
    keypoints: List[PersonKeypoint]

    @classmethod
    def v_keypoint_to_state(cls, keypoint_v: int) -> KeypointState:
        return KEYPOINT_STATES[keypoint_v]

    @classmethod
    def get_person_keypoints(
        cls, flatten_keypoints: List[int], num_keypoints: int
    ) -> List[PersonKeypoint]:
        keypoints_x = flatten_keypoints[0::3]
        keypoints_y = flatten_keypoints[1::3]
        keypoints_v = flatten_keypoints[2::3]
        assert len(keypoints_x) == len(keypoints_y) == len(keypoints_v)

        keypoints = [
            PersonKeypoint(x=x, y=y, v=v, state=cls.v_keypoint_to_state(v))
            for x, y, v in zip(keypoints_x, keypoints_y, keypoints_v)
        ]
        assert len([kp for kp in keypoints if kp.state != "unknown"]) == num_keypoints
        return keypoints

    @classmethod
    def from_dict(
        cls,
        json_dict: JsonDict,
        images: Dict[ImageId, ImageData],
        decode_rle: bool,
    ) -> Self:
        segmentation = json_dict["segmentation"]
        image_id = json_dict["image_id"]
        image_data = images[image_id]
        iscrowd = bool(json_dict["iscrowd"])

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
        flatten_keypoints = json_dict["keypoints"]
        num_keypoints = json_dict["num_keypoints"]
        keypoints = cls.get_person_keypoints(flatten_keypoints, num_keypoints)

        return cls(
            image_id=image_id,
            segmentation=segmentation_mask,  # type: ignore
            num_keypoints=num_keypoints,
            keypoints=keypoints,
            **json_dict,
        )
