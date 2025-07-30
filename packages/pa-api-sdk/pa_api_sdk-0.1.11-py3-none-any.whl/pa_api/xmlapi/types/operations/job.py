import enum
import logging
from datetime import time
from typing import Annotated, Optional

from pydantic import ConfigDict, Field, PlainValidator

from pa_api.xmlapi.types.utils import (
    Datetime,
    String,
    XMLBaseModel,
    parse_datetime,
    parse_time,
)


def parse_tdeq(d):
    if "null" in d:
        return None
    try:
        return parse_time(d)
    except Exception as e:
        logging.debug(e)
    return parse_datetime(d)


def parse_progress(progress):
    try:
        return float(progress)
    except Exception as e:
        logging.debug(f"{e} => Fallback to datetime parsing")

    # When finished, progress becomes the date of the end
    if parse_datetime(progress):
        return 100.0
    return None


Progress = Annotated[float, PlainValidator(parse_progress)]
Time = Annotated[time, PlainValidator(parse_tdeq)]


class JobResult(enum.Enum):
    OK = "OK"
    FAIL = "FAIL"


class Job(XMLBaseModel):
    model_config = ConfigDict(
        # https://docs.pydantic.dev/2.0/api/alias_generators/
        # alias_generator=lambda name: name.replace("-", "_")
    )
    # TODO: Use pydantic
    type: str
    tenq: Optional[Datetime] = None
    tdeq: Optional[Time] = None
    id: str = ""
    user: String = ""
    status: str = ""
    queued: bool = False
    stoppable: bool = False
    result: str = ""
    tfin: Optional[Datetime] = None
    description: String = ""
    position_in_queue: int = Field(alias="positionInQ", default=-1)
    progress: Progress = 0.0
    details: String = ""
    warnings: String = ""
