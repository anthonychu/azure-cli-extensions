import unittest

from azure.cli.core.azclierror import HTTPError, InvalidArgumentValueError, RequiredArgumentMissingError

from azext_connector_namespace.custom import (
    build_operation_summary,
    build_runtime_parameters,
    build_runtime_url,
    build_schema_example,
    build_access_policy_body,
    build_connection_body,
    build_consent_body,
    build_gateway_body,
    build_gateway_update_body,
    build_trigger_config_body,
    build_trigger_config_runs_query,
    collect_paged_values,
    extract_first_consent_link,
    find_swagger_operation,
    format_runtime_http_error,
    iter_swagger_operations,
    operation_matches_type,
    resolve_swagger_schema,
    validate_required_body,
)
from azext_connector_namespace._transformers import transform_trigger_config_run_table
from azext_connector_namespace._validators import parse_key_value_pairs


SAMPLE_SWAGGER = {
    'paths': {
        '/{connectionId}/v2/Mail': {
            'post': {
                'operationId': 'SendEmailV2',
                'summary': 'Send an email',
                'parameters': [
                    {'name': 'connectionId', 'in': 'path', 'required': True, 'type': 'string'},
                    {'name': 'emailMessage', 'in': 'body', 'required': True,
                     'schema': {'$ref': '#/definitions/ClientSendHtmlMessage'}},
                ],
            },
        },
        '/{connectionId}/Draft/Send/{messageId}': {
            'post': {
                'operationId': 'SendDraftEmail',
                'parameters': [
                    {'name': 'connectionId', 'in': 'path', 'required': True, 'type': 'string'},
                    {'name': 'messageId', 'in': 'path', 'required': True, 'type': 'string'},
                ],
            },
        },
        '/{connectionId}/codeless/httprequest': {
            'post': {
                'operationId': 'HttpRequest',
                'parameters': [
                    {'name': 'connectionId', 'in': 'path', 'required': True, 'type': 'string'},
                    {'name': 'Uri', 'in': 'header', 'required': True, 'type': 'string'},
                    {'name': 'api-version', 'in': 'query', 'required': False, 'type': 'string'},
                ],
            },
        },
        '/{connectionId}/v4/Mail/OnFlaggedEmail': {
            'get': {
                'operationId': 'OnFlaggedEmailV4',
                'summary': 'When an email is flagged',
                'x-ms-trigger': 'batch',
                'x-ms-trigger-hint': 'To see it work now, flag an email in your inbox.',
                'x-ms-notification': {'operationId': 'CreateGraphOnFlaggedEmailPokeSubscription'},
                'parameters': [
                    {'name': 'connectionId', 'in': 'path', 'required': True, 'type': 'string'},
                ],
            },
        },
    },
    'definitions': {
        'ClientSendHtmlMessage': {
            'type': 'object',
            'required': ['To', 'Subject', 'Body'],
            'properties': {
                'To': {'type': 'string', 'description': 'Recipient email address.'},
                'Subject': {'type': 'string'},
                'Body': {'type': 'string'},
                'Importance': {'type': 'string', 'enum': ['Low', 'Normal', 'High']},
            },
        },
    },
}


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


class FakePageClient:
    def __init__(self, pages):
        self.pages = pages
        self.requested_urls = []

    def request_url(self, method, url):
        self.requested_urls.append((method, url))
        return self.pages[url]


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

    def test_build_trigger_config_runs_query(self):
        self.assertIsNone(build_trigger_config_runs_query())
        self.assertEqual(build_trigger_config_runs_query(50), {'$top': 50})
        with self.assertRaises(InvalidArgumentValueError):
            build_trigger_config_runs_query(0)
        with self.assertRaises(InvalidArgumentValueError):
            build_trigger_config_runs_query(50, all_runs=True)

    def test_collect_paged_values_returns_first_page_by_default(self):
        first_page = {'value': [{'id': 'run-1'}], 'nextLink': 'https://example.test/next'}
        client = FakePageClient({'https://example.test/next': {'value': [{'id': 'run-2'}]}})
        values = collect_paged_values(client, first_page)
        self.assertEqual(values, [{'id': 'run-1'}])
        self.assertEqual(client.requested_urls, [])

    def test_collect_paged_values_follows_next_link_to_limit(self):
        first_page = {'value': [{'id': 'run-1'}], 'nextLink': 'https://example.test/page-2'}
        client = FakePageClient({
            'https://example.test/page-2': {
                'value': [{'id': 'run-2'}, {'id': 'run-3'}, {'id': 'run-4'}],
                'nextLink': 'https://example.test/page-3',
            },
        })
        values = collect_paged_values(client, first_page, limit=3, follow_next=True)
        self.assertEqual(values, [{'id': 'run-1'}, {'id': 'run-2'}, {'id': 'run-3'}])
        self.assertEqual(client.requested_urls, [('GET', 'https://example.test/page-2')])

    def test_transform_trigger_config_run_table_uses_flat_run_fields(self):
        run = {
            'id': '08584228874171720428436904333CU11',
            'status': 'Succeeded',
            'startTime': '2026-05-14T00:44:28.6300239Z',
            'endTime': '2026-05-14T00:44:30.8390339Z',
        }
        rows = transform_trigger_config_run_table([run])
        self.assertEqual(rows[0]['Id'], run['id'])
        self.assertEqual(rows[0]['Status'], 'Succeeded')
        self.assertEqual(rows[0]['StartTime'], run['startTime'])
        self.assertEqual(rows[0]['EndTime'], run['endTime'])

    def test_iter_swagger_operations(self):
        operations = list(iter_swagger_operations(SAMPLE_SWAGGER))
        self.assertEqual(len(operations), 4)
        self.assertIn(('post', 'SendEmailV2'), [(method, operation.get('operationId'))
                                                for _, method, operation in operations])

    def test_find_swagger_operation(self):
        path, method, operation = find_swagger_operation(SAMPLE_SWAGGER, 'SendEmailV2')
        self.assertEqual(path, '/{connectionId}/v2/Mail')
        self.assertEqual(method, 'post')
        self.assertEqual(operation['summary'], 'Send an email')

    def test_find_swagger_operation_not_found(self):
        with self.assertRaises(InvalidArgumentValueError):
            find_swagger_operation(SAMPLE_SWAGGER, 'MissingOperation')

    def test_resolve_swagger_schema(self):
        resolved = resolve_swagger_schema(SAMPLE_SWAGGER, {'$ref': '#/definitions/ClientSendHtmlMessage'})
        self.assertEqual(resolved['type'], 'object')
        self.assertEqual(resolved['properties']['To']['description'], 'Recipient email address.')

    def test_build_schema_example(self):
        resolved = resolve_swagger_schema(SAMPLE_SWAGGER, {'$ref': '#/definitions/ClientSendHtmlMessage'})
        example = build_schema_example(resolved)
        self.assertEqual(example, {
            'To': 'user@example.com',
            'Subject': 'string',
            'Body': 'string',
        })

    def test_build_operation_summary_includes_schema_details_when_requested(self):
        path, method, operation = find_swagger_operation(SAMPLE_SWAGGER, 'SendEmailV2')
        connection = {'properties': {'connectionRuntimeUrl': 'https://example.test/apim/office365/connection-id'}}
        summary = build_operation_summary(
            path, method, operation, connection, swagger=SAMPLE_SWAGGER, include_schema_details=True)
        self.assertEqual(summary['operationType'], 'action')
        self.assertIsNone(summary['triggerType'])
        self.assertEqual(summary['bodySchema']['$ref'], '#/definitions/ClientSendHtmlMessage')
        self.assertEqual(summary['resolvedBodySchema']['properties']['Subject']['type'], 'string')
        self.assertEqual(summary['requestBodyExample']['To'], 'user@example.com')

    def test_build_operation_summary_includes_trigger_metadata(self):
        path, method, operation = find_swagger_operation(SAMPLE_SWAGGER, 'OnFlaggedEmailV4')
        connection = {'properties': {'connectionRuntimeUrl': 'https://example.test/apim/office365/connection-id'}}
        summary = build_operation_summary(path, method, operation, connection)
        self.assertEqual(summary['operationType'], 'trigger')
        self.assertEqual(summary['triggerType'], 'batch')
        self.assertEqual(summary['triggerHint'], 'To see it work now, flag an email in your inbox.')
        self.assertEqual(summary['notificationOperationId'], 'CreateGraphOnFlaggedEmailPokeSubscription')

    def test_operation_matches_type(self):
        _, _, action = find_swagger_operation(SAMPLE_SWAGGER, 'SendEmailV2')
        _, _, trigger = find_swagger_operation(SAMPLE_SWAGGER, 'OnFlaggedEmailV4')
        self.assertTrue(operation_matches_type(action))
        self.assertTrue(operation_matches_type(trigger))
        self.assertTrue(operation_matches_type(action, 'action'))
        self.assertFalse(operation_matches_type(action, 'trigger'))
        self.assertTrue(operation_matches_type(trigger, 'trigger'))
        self.assertFalse(operation_matches_type(trigger, 'action'))
        with self.assertRaises(InvalidArgumentValueError):
            operation_matches_type(action, 'other')

    def test_build_operation_summary_omits_schema_details_by_default(self):
        path, method, operation = find_swagger_operation(SAMPLE_SWAGGER, 'SendEmailV2')
        connection = {'properties': {'connectionRuntimeUrl': 'https://example.test/apim/office365/connection-id'}}
        summary = build_operation_summary(path, method, operation, connection, swagger=SAMPLE_SWAGGER)
        self.assertNotIn('resolvedBodySchema', summary)
        self.assertNotIn('requestBodyExample', summary)

    def test_build_runtime_url_strips_connection_id(self):
        url = build_runtime_url(
            'https://example.test/apim/office365/connection-id',
            '/{connectionId}/v2/Mail')
        self.assertEqual(url, 'https://example.test/apim/office365/connection-id/v2/Mail')

    def test_build_runtime_url_replaces_path_parameters(self):
        url = build_runtime_url(
            'https://example.test/apim/office365/connection-id',
            '/{connectionId}/Draft/Send/{messageId}',
            {'messageId': 'message/id'})
        self.assertEqual(url, 'https://example.test/apim/office365/connection-id/Draft/Send/message%2Fid')

    def test_build_runtime_url_requires_path_parameters(self):
        with self.assertRaises(RequiredArgumentMissingError):
            build_runtime_url('https://example.test/apim/office365/connection-id', '/{connectionId}/Draft/{messageId}')

    def test_build_runtime_parameters_routes_by_swagger_location(self):
        _, _, operation = find_swagger_operation(SAMPLE_SWAGGER, 'HttpRequest')
        query, headers, path = build_runtime_parameters(
            operation,
            parameter=['Uri=https://graph.microsoft.com/v1.0/me', 'api-version=1'],
            query_parameter=['top=5'],
            header=['CustomHeader=value'])
        self.assertEqual(headers['Uri'], 'https://graph.microsoft.com/v1.0/me')
        self.assertEqual(headers['CustomHeader'], 'value')
        self.assertEqual(query['api-version'], '1')
        self.assertEqual(query['top'], '5')
        self.assertEqual(path, {})

    def test_build_runtime_parameters_requires_header(self):
        _, _, operation = find_swagger_operation(SAMPLE_SWAGGER, 'HttpRequest')
        with self.assertRaises(RequiredArgumentMissingError):
            build_runtime_parameters(operation)

    def test_validate_required_body(self):
        _, _, operation = find_swagger_operation(SAMPLE_SWAGGER, 'SendEmailV2')
        with self.assertRaises(RequiredArgumentMissingError):
            validate_required_body(operation, None)
        validate_required_body(operation, {'To': 'user@example.com'})

    def test_format_runtime_http_error_for_acl_failure(self):
        response = FakeResponse(403, {'Message': 'Forbidden'})
        message = format_runtime_http_error(
            HTTPError('Forbidden', response),
            resource_group_name='rg',
            gateway_name='gateway',
            connection_name='office365-test')
        self.assertIn('Runtime authorization failed', message)
        self.assertIn('connection access-policy create', message)
        self.assertIn('az connector-namespace', message)
        self.assertIn('--namespace-name gateway', message)
        self.assertIn('--connection-name office365-test', message)

    def test_format_runtime_http_error_for_wrong_audience(self):
        response = FakeResponse(400, {'message': 'Audience validation failed'})
        message = format_runtime_http_error(
            HTTPError('Bad Request', response),
            resource_group_name='rg',
            gateway_name='gateway',
            connection_name='office365-test')
        self.assertIn('runtime token exchange failed', message)
        self.assertIn('https://service.flow.microsoft.com/', message)


if __name__ == '__main__':
    unittest.main()