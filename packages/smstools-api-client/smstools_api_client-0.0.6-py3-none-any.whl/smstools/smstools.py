from smstools.api_client import ApiClient
from smstools.exceptions import ApiException
from smstools.configuration import Configuration

from smstools.api.default_api import DefaultApi


class Smstools(DefaultApi):
    def __init__(self, client_id, client_secret):
        self._configuration = Configuration(
            api_key=dict(
                clientId=client_id,
                clientSecret=client_secret,
            )
        )

        with ApiClient(self._configuration) as self._api_client:
            super().__init__(self._api_client)
