from pydantic import Field, BeforeValidator
from typing import Annotated
from .base import CommandType, BaseCommand


class PublishRecording(BaseCommand):
    recording_name: str = Field(
        examples=["recording.mp4"],
        description="The name of the recording file to be published",
    )
    type: Annotated[
        CommandType, BeforeValidator(lambda _: CommandType.PUBLISH_RECORDING)
    ] = Field(init=False, default=CommandType.PUBLISH_RECORDING, frozen=True)
