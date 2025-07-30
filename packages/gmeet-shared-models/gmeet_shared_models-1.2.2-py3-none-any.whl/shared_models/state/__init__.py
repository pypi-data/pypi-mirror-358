from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class BotState(Enum):
    INITIALIZING = (0, "initializing")
    READY = (1, "ready")

    LOGGED_GOOGLE = (2, "logged_google")
    WAITING_INVITATION_CONFIRMATION = (3, "waiting_invitation_confirmation")
    CONNECTED_MEET = (4, "connected_meet")

    RECORDING_STARTED = (5, "recording_started")
    RECORDING_STOPPED = (6, "recording_stopped")
    RECORDING_PUBLISHED = (7, "recording_published")

    DEAD = (8, "dead")

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def label(self) -> str:
        return self.value[1]

    def __str__(self):
        return self.label

    @classmethod
    def from_code(cls, code: int) -> "BotState":
        for state in cls:
            if state.code == code:
                return state
        raise ValueError(f"Invalid status code: {code}")


class StateMessage(BaseModel):
    state: BotState = Field(..., description="The current state of the bot")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="The timestamp when the state was updated",
    )
