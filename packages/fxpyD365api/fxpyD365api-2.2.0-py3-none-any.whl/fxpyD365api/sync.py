import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import BaseApiWrapperMixin
from .exceptions import D365ApiError

logger = logging.getLogger(__name__)

class SyncBaseApiWrapper(BaseApiWrapperMixin):
    DEFAULT_TIMEOUT = 20

    def __init__(self, *args, timeout=None, retries=3, backoff_factor=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self._session = requests.Session()

        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def _request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        try:
            return self._session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            logger.warning(f"D365 API request failed after retries: {e}")
            raise D365ApiError({'request': str(e)})