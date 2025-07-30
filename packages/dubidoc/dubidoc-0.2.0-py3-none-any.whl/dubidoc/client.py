import logging
from urllib.parse import urljoin

import requests

from dubidoc import __version__
from dubidoc._modules import (
    AccessTokenAPI,
    AuthenticationAPI,
    DeviceAPI,
    DocumentAPI,
    DocumentLinkAPI,
    ParticipantAPI,
    DownloadAPI,
    OrganizationAPI,
)
from dubidoc.enum import HttpMethod
from dubidoc.response import DubidocAPIResponse

logger = logging.getLogger('dubidoc')


class DubidocAPIClient:
    """
    - https://my.dubidoc.com.ua/auth - production URL
    - https://docs-stage.navkolo.one/auth - staging URL
    """

    API_VERSION = 'v1'
    DEFAULT_HEADERS = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'user-agent': f'python-dubidoc/{__version__} | (https://github.com/DmytroLitvinov/python-dubidoc)',
    }

    def __init__(self, api_token: str, organization_uuid: str = '', *, is_stage_env: bool = False):
        self.api_token = api_token
        self.organization_uuid = organization_uuid
        if is_stage_env:
            self.base_url = 'https://docs-stage.navkolo.one'
        else:
            self.base_url = 'https://my.dubidoc.com.ua'
        # FIXME: The prefix should be "api/v1" instead of "api/api/v1"
        #  Dubidoc will notify when it will be fixed
        self.prefix = f'api/api/{self.API_VERSION}/'
        self.endpoint = urljoin(self.base_url, self.prefix)

        self._modules = {}

        # Modules
        self.document_api = self._get_module(DocumentAPI)
        self.document_link_api = self._get_module(DocumentLinkAPI)
        self.participant_api = self._get_module(ParticipantAPI)
        self.download_api = self._get_module(DownloadAPI)
        self.organization_api = self._get_module(OrganizationAPI)

        if is_stage_env == 'stage':
            self.access_token_api = self._get_module(AccessTokenAPI)
            self.authentication_api = self._get_module(AuthenticationAPI)
            self.device_api = self._get_module(DeviceAPI)
            # Not yet implemented and probably not needed
            # self.organization_user_api = OrganizationUserAPI(self)
            # self.organization_api = OrganizationAPI(self)
            # self.shortcode_api = ShortcodeAPI(self)

    def _get_headers(self):
        headers = self.DEFAULT_HEADERS.copy()
        headers.update({'X-Access-Token': f'{self.api_token}', 'X-Organization': self.organization_uuid})
        return headers

    def _get_module(self, cls):
        if cls not in self._modules:
            self._modules[cls] = cls(self)
        return self._modules[cls]

    def make_request(self, method: HttpMethod, path: str, body: dict = {}) -> DubidocAPIResponse:
        """
        Fetches the given path in the Dubidoc API.
        :param method: HTTP method
        :param path: Api path
        :param body: body of request
        :return: Serialized server response or error
        """
        url = urljoin(self.endpoint, path)
        headers = self._get_headers()

        logger.debug(f'Making {method.value} request to {url} with headers {headers} and body {body}')
        # https://github.com/psf/requests/issues/3070
        response = requests.request(method.value, url, headers=headers, json=body, timeout=10)
        logger.debug(f'Received response with status code {response.status_code} and body {response.text}')

        return DubidocAPIResponse(response.json(), response.status_code)
