import unittest

from azure.cli.core.azclierror import RequiredArgumentMissingError

from azext_connector_gateway.custom import (
    build_access_policy_body,
    build_connection_body,
    build_consent_body,
    build_gateway_body,
    build_gateway_update_body,
    build_trigger_config_body,
    extract_first_consent_link,
)
from azext_connector_gateway._validators import parse_key_value_pairs


class ConnectorGatewayUnitTests(unittest.TestCase):

    def test_build_gateway_body_defaults_identity(self):
        body = build_gateway_body('westcentralus')
        self.assertEqual(body['location'], 'westcentralus')
        self.assertEqual(body['identity']['type'], 'SystemAssigned')
        self.assertEqual(body['properties'], {})

    def test_build_gateway_update_body_omits_read_only_fields(self):
        body = build_gateway_update_body({
            'location': 'westcentralus',
            'tags': {'env': 'test'},
            'identity': {
                'type': 'SystemAssigned',
                'principalId': 'principal-id',
                'tenantId': 'tenant-id',
            },
            'properties': {
                'connectorGatewayId': 'gateway-id',
                'provisioningState': 'Succeeded',
            },
        })
        self.assertEqual(body, {
            'location': 'westcentralus',
            'properties': {},
            'tags': {'env': 'test'},
            'identity': {'type': 'SystemAssigned'},
        })

    def test_build_gateway_update_body_preserves_user_assigned_ids(self):
        body = build_gateway_update_body({
            'location': 'westcentralus',
            'identity': {
                'type': 'SystemAssigned, UserAssigned',
                'userAssignedIdentities': {
                    '/subscriptions/sub/resourcegroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id1': {
                        'principalId': 'principal-id',
                        'clientId': 'client-id',
                    },
                },
            },
        })
        self.assertEqual(body['identity'], {
            'type': 'SystemAssigned, UserAssigned',
            'userAssignedIdentities': {
                '/subscriptions/sub/resourcegroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id1': {},
            },
        })

    def test_build_connection_body(self):
        body = build_connection_body('office365')
        self.assertEqual(body['properties']['connectorName'], 'office365')

    def test_build_connection_body_requires_connector(self):
        with self.assertRaises(RequiredArgumentMissingError):
            build_connection_body(None)

    def test_build_consent_body(self):
        body = build_consent_body('https://portal.azure.com')
        self.assertEqual(body['parameters'][0]['redirectUrl'], 'https://portal.azure.com')
        self.assertEqual(body['parameters'][0]['parameterName'], 'token')

    def test_extract_first_consent_link(self):
        entry = extract_first_consent_link({'value': [{'link': 'https://example.test', 'status': 'Ready'}]})
        self.assertEqual(entry['link'], 'https://example.test')

    def test_build_access_policy_body(self):
        body = build_access_policy_body('object-id', 'tenant-id')
        identity = body['properties']['principal']['identity']
        self.assertEqual(identity['objectId'], 'object-id')
        self.assertEqual(identity['tenantId'], 'tenant-id')

    def test_parse_key_value_pairs(self):
        pairs = parse_key_value_pairs(['folderId=Inbox', 'includeSubfolders=false'])
        self.assertEqual(pairs, [
            {'name': 'folderId', 'value': 'Inbox'},
            {'name': 'includeSubfolders', 'value': 'false'},
        ])

    def test_build_trigger_config_body(self):
        body = build_trigger_config_body(
            available_connector='onedriveforbusiness',
            connection_name='onedrive-test',
            operation_name='OnNewFileV2',
            callback_url='https://example.test/callback',
            parameter=['folderId=Documents'])
        properties = body['properties']
        self.assertEqual(properties['connectionDetails']['connectorName'], 'onedriveforbusiness')
        self.assertEqual(properties['connectionDetails']['connectionName'], 'onedrive-test')
        self.assertEqual(properties['operationName'], 'OnNewFileV2')
        self.assertEqual(properties['notificationDetails']['httpMethod'], 'Post')
        self.assertEqual(properties['parameters'][0], {'name': 'folderId', 'value': 'Documents'})


if __name__ == '__main__':
    unittest.main()