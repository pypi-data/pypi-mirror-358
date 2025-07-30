from .exceptions import D365ApiError, D365ApiWrapperError
from .sync import SyncBaseApiWrapper
from .async_ import AsyncBaseApiWrapper
from .factory import get_wrapper
from .generic import GenericWrapper  # legacy support

__all__ = [
    "get_wrapper",
    "GenericWrapper",
    "D365ApiError",
    "D365ApiWrapperError",
    "SyncBaseApiWrapper",
    "AsyncBaseApiWrapper"
]