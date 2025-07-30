from .sync import SyncBaseApiWrapper
from .async_ import AsyncBaseApiWrapper

def get_wrapper(entity_type, async_mode=False, **kwargs):
    wrapper_cls = AsyncBaseApiWrapper if async_mode else SyncBaseApiWrapper
    instance = wrapper_cls(**kwargs)
    instance.entity_type = entity_type
    return instance