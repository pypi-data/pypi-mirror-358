from .sync import SyncBaseApiWrapper
from .async_ import AsyncBaseApiWrapper

class GenericWrapper:
    def __new__(cls, entity_type, async_mode=False, *args, **kwargs):
        wrapper_cls = AsyncBaseApiWrapper if async_mode else SyncBaseApiWrapper
        instance = wrapper_cls(*args, **kwargs)
        instance.entity_type = entity_type
        return instance