from hfcocoapi.processors.processor import MsCocoProcessor  # NOQA

from hfcocoapi.processors.caption import CaptionsProcessor
from hfcocoapi.processors.instances import InstancesProcessor
from hfcocoapi.processors.person_keypoint import PersonKeypointsProcessor


__all__ = [
    "MsCocoProcessor",
    "CaptionsProcessor",
    "InstancesProcessor",
    "PersonKeypointsProcessor",
]
