import os
import datetime
import msal
import pytz

class BaseApiWrapperMixin:
    """Mixin that provides shared logic for both sync and async API wrappers."""

    entity_type = None
    __base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def __init__(self, crmorg=None, token=None, tenant=None, client_id=None,
                 client_secret=None, api_url='/api/data/v9.0/', extra_headers=None,
                 page_size=100, impersonate=None):
        self.crmorg = crmorg or self.get_crmorg()
        self.tenant = tenant
        self.client_id = client_id
        self.client_secret = client_secret
        self.page_size = page_size
        self._api_url = api_url
        self.impersonate = impersonate
        self.current_page = None
        self.page_urls = {}

        if token:
            self._token = token
            self.token_expires_at = datetime.datetime.fromisoformat(token['expires_on'])
        else:
            self._token = self._get_token(self.tenant, self.client_id, self.client_secret)

        self.__headers = extra_headers or {}

    @staticmethod
    def get_crmorg():
        org = os.getenv('D365_ORG_URL')
        if org is None:
            raise ValueError('Missing required environment variable: D365_ORG_URL')
        return org

    def _get_token(self, tenant, client_id, client_secret):
        tenant = tenant or os.getenv('D365_TENANT')
        client_id = client_id or os.getenv('D365_CLIENT_ID')
        client_secret = client_secret or os.getenv('D365_CLIENT_SECRET')

        if not all([tenant, client_id, client_secret]):
            raise ValueError('D365_TENANT, D365_CLIENT_ID, and D365_CLIENT_SECRET are required')

        app = msal.ConfidentialClientApplication(
            authority=f'https://login.microsoftonline.com/{tenant}',
            client_id=client_id,
            client_credential=client_secret,
        )
        token = app.acquire_token_for_client(scopes=[f'{self.crmorg}/.default'])

        if 'access_token' not in token:
            raise D365ApiError({'error': 'Failed to acquire token', 'details': token})

        self.token_expires_at = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=token.get('expires_in', 3600) - 60)
        return token

    @property
    def token(self):
        if datetime.datetime.now(pytz.utc) + datetime.timedelta(minutes=5) > self.token_expires_at:
            self._token = self._get_token(self.tenant, self.client_id, self.client_secret)
        return self._token['access_token']

    @property
    def headers(self):
        headers = self.__base_headers.copy()
        headers['Authorization'] = f'Bearer {self.token}'
        if self.impersonate:
            headers['MSCRMCallerID'] = self.impersonate
        return headers

    @property
    def api_url(self):
        if not self.entity_type:
            raise NotImplementedError('"entity_type" must be defined in subclasses')
        return f"{self.crmorg}{self._api_url}{self.entity_type}"

    @staticmethod
    def _update_prefer_header(headers_dict, key, value):
        p_header = headers_dict.get('Prefer', '')
        hdrs = {}
        if p_header:
            for s in p_header.split(','):
                if '=' in s:
                    k, v = s.split('=', 1)
                    hdrs[k.strip()] = v.strip()
        hdrs[key] = value
        headers_dict['Prefer'] = ','.join([f'{k}={v}' for k, v in hdrs.items()])
        return headers_dict
