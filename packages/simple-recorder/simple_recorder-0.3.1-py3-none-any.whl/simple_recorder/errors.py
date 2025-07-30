from clypi import ClypiException

from .styler import error


class SimpleRecorderError(ClypiException):
    """Base class for all SimpleRecorder exceptions."""

    def __init__(self, message: str):
        super().__init__(error(message))
        self.raw_message = message
