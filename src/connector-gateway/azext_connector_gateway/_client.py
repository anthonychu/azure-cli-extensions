import json
from urllib.parse import quote, urlencode

from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request


API_VERSION = '2026-05-01-preview'
PROVIDER = 'Microsoft.Web'
GATEWAY_TYPE = 'connectorGateways'


def _segment(value):
    return quote(str(value), safe='')


class ConnectorGatewayClient:

    def __init__(self, cmd):
        self.cli_ctx = cmd.cli_ctx
        self.subscription_id = get_subscription_id(cmd.cli_ctx)
        self.management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager.strip('/')

    def gateway_collection_path(self, resource_group_name=None):
        if resource_group_name:
            return '/subscriptions/{}/resourceGroups/{}/providers/{}/{}'.format(
                _segment(self.subscription_id), _segment(resource_group_name), PROVIDER, GATEWAY_TYPE)
        return '/subscriptions/{}/providers/{}/{}'.format(_segment(self.subscription_id), PROVIDER, GATEWAY_TYPE)

    def gateway_path(self, resource_group_name, gateway_name):
        return '{}/{}'.format(self.gateway_collection_path(resource_group_name), _segment(gateway_name))

    def child_collection_path(self, resource_group_name, gateway_name, collection):
        return '{}/{}'.format(self.gateway_path(resource_group_name, gateway_name), collection)

    def child_path(self, resource_group_name, gateway_name, collection, name):
        return '{}/{}'.format(self.child_collection_path(resource_group_name, gateway_name, collection), _segment(name))

    def access_policy_collection_path(self, resource_group_name, gateway_name, connection_name):
        return '{}/accessPolicies'.format(self.child_path(resource_group_name, gateway_name, 'connections', connection_name))

    def access_policy_path(self, resource_group_name, gateway_name, connection_name, policy_name):
        return '{}/{}'.format(
            self.access_policy_collection_path(resource_group_name, gateway_name, connection_name), _segment(policy_name))

    def request(self, method, path, body=None, query=None):
        params = {'api-version': API_VERSION}
        if query:
            params.update({key: _query_value(value) for key, value in query.items() if value is not None})
        url = '{}{}?{}'.format(self.management_hostname, path, urlencode(params))
        headers = ['Content-Type=application/json'] if body is not None else None
        response = send_raw_request(
            self.cli_ctx, method.upper(), url, headers=headers, body=json.dumps(body) if body is not None else None)
        try:
            return response.json()
        except ValueError:
            return None


def _query_value(value):
    if isinstance(value, bool):
        return str(value).lower()
    return value