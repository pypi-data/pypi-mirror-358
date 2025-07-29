from enum import StrEnum
from pydantic import BaseModel, Field


class ExceptionType(StrEnum):
    UNKNOWN = "unknown"
    STATE_EXCEPTION = "state_exception"
    ELEMENT_NOT_FOUND = "element_not_found"

    # Initialization errors
    EMAIL_FROM_ENV_IS_NOT_SET = "email_from_env_is_not_set"
    PASSWORD_FROM_ENV_IS_NOT_SET = "password_from_env_is_not_set"
    CANNOT_START_BROWSER = "cannot_start_browser"

    # Google login errors
    EMAIL_FROM_ENV_AND_FROM_MESSAGE_DOES_NOT_MATCH = (
        "email_from_env_and_from_message_does_not_match"
    )
    ## Elements not found
    EMAIL_FIELD_NOT_FOUND = "email_field_not_found"
    NEXT_BUTTON_NOT_FOUND = "next_button_not_found"
    PASSWORD_FIELD_NOT_FOUND = "password_field_not_found"
    SUBMIT_BUTTON_NOT_FOUND = "submit_button_not_found"

    # Join meet errors
    CANNOT_LOAD_MEET_PAGE = "cannot_load_page"
    JOIN_BUTTON_NOT_FOUND = "join_button_not_found"
    BUTTON_CHECK_PEOPLE_NOT_FOUND = "button_check_people_not_found"
    JOIN_TIMEOUT = "join_timeout"
    
    # Start recording error
    RECORDING_ALREADY_STARTED = "recording_already_started"
    
    # Stop recording errors
    RECORDING_ALREADY_STOPPED = "recording_already_stopped"
    RECORDING_NOT_STARTED = "recording_not_started"


class ErrorMessage(BaseModel):
    exception_type: ExceptionType = Field(
        ...,
        description="Type of the exception that occurred",
    )
    message: str | None = Field(
        default=None,
        description="Detailed message describing the error",
    )
