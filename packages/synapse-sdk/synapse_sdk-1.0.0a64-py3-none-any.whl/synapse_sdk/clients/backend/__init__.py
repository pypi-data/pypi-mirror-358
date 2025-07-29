from synapse_sdk.clients.backend.annotation import AnnotationClientMixin
from synapse_sdk.clients.backend.core import CoreClientMixin
from synapse_sdk.clients.backend.data_collection import DataCollectionClientMixin
from synapse_sdk.clients.backend.hitl import HITLClientMixin
from synapse_sdk.clients.backend.integration import IntegrationClientMixin
from synapse_sdk.clients.backend.ml import MLClientMixin


class BackendClient(
    AnnotationClientMixin,
    CoreClientMixin,
    DataCollectionClientMixin,
    IntegrationClientMixin,
    MLClientMixin,
    HITLClientMixin,
):
    name = 'Backend'
    access_token = None
    agent_token = None

    def __init__(self, base_url, access_token=None, agent_token=None, **kwargs):
        super().__init__(base_url)
        self.access_token = access_token
        self.agent_token = agent_token

    def _get_headers(self):
        headers = {}
        if self.access_token:
            headers['Synapse-Access-Token'] = f'Token {self.access_token}'
        if self.agent_token:
            headers['SYNAPSE-Agent'] = f'Token {self.agent_token}'
        return headers
