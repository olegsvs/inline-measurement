import anime_qq
from dataclasses import dataclass, field 
import json
from enum import Enum
import logging

logger = logging.getLogger(__name__)
class ErrorCodes(Enum):
    SUCCESS = 0
    NUDITY = 2114
    NO_FACE = 1001
    AUTH_FAILED = -2111
    USER_IP_COUNTRY = 2119
    PARAM_INVALID = -2100
    CONNECTION_CLOSED = 141
    PLEASE_WAIT = 2111


@dataclass
class AnimeResponse:
    code: int
    msg: str
    images: list = ""
    faces: list = ""
    extra: list[str] = field(default_factory=list)
    error: str = None
    videos: list = ""

    def __post_init__(self):
        success = False
        logger.info("anime_qq resp code: " + str(self.code))
        match ErrorCodes(self.code):
            case ErrorCodes.AUTH_FAILED:
                self.error = "Auth failed. Don't know how to solve this one."
            case ErrorCodes.NUDITY:
                self.error = "Image rejected. Nudity isn't allowed."
            case ErrorCodes.NO_FACE:
                self.error = "No face in image. Can't process."
            case ErrorCodes.USER_IP_COUNTRY:
                self.error = "Your ip is not from china, try using vpn or proxies."
            case ErrorCodes.PARAM_INVALID:
                self.error = "Invalid file format. Must be one of jpeg|gif|png|bmp|ico|svg|tiff|ai|drw|pct|psp|xcf|psd|raw|webp."
            case ErrorCodes.CONNECTION_CLOSED:
                self.error = "The connection was forcibly closed by the host. (Is the image too big?)"
            case ErrorCodes.PLEASE_WAIT:
                self.error = "Try again later"
            case ErrorCodes.SUCCESS:
                self.extra = json.loads(self.extra)["img_urls"]
                self.error = None
                success = True
            case _:
                self.error = "Unknown error"

