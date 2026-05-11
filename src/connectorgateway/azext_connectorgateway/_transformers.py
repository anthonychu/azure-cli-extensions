from collections import OrderedDict


def transform_gateway_table(result):
    return _transform_many(result, _gateway_row)


def transform_available_connector_table(result):
    return _transform_many(result, _available_connector_row)


def transform_connection_table(result):
    return _transform_many(result, _connection_row)


def transform_access_policy_table(result):
    return _transform_many(result, _access_policy_row)


def transform_mcp_server_config_table(result):
    return _transform_many(result, _mcp_server_config_row)


def transform_trigger_config_table(result):
    return _transform_many(result, _trigger_config_row)


def _transform_many(result, row_transformer):
    if isinstance(result, list):
        return [row_transformer(item) for item in result]
    return row_transformer(result)


def _gateway_row(item):
    properties = item.get('properties') or {}
    identity = item.get('identity') or {}
    return OrderedDict([
        ('Name', item.get('name')),
        ('Location', item.get('location')),
        ('Identity', identity.get('type')),
        ('State', properties.get('provisioningState')),
        ('GatewayId', properties.get('connectorGatewayId')),
    ])


def _available_connector_row(item):
    if item.get('swagger'):
        paths = item.get('paths') or {}
        definitions = item.get('definitions') or {}
        info = item.get('info') or {}
        return OrderedDict([
            ('Title', info.get('title')),
            ('Version', info.get('version')),
            ('Swagger', item.get('swagger')),
            ('Host', item.get('host')),
            ('BasePath', item.get('basePath')),
            ('Paths', len(paths)),
            ('Definitions', len(definitions)),
        ])
    properties = item.get('properties') or {}
    general_info = properties.get('generalInformation') or {}
    capabilities = properties.get('capabilities') or []
    return OrderedDict([
        ('Name', item.get('name')),
        ('DisplayName', general_info.get('displayName')),
        ('Release', general_info.get('releaseTag')),
        ('Tier', general_info.get('tier')),
        ('Capabilities', ','.join(capabilities)),
        ('Export', properties.get('isExportSupported')),
    ])


def _connection_row(item):
    properties = item.get('properties') or {}
    return OrderedDict([
        ('Name', item.get('name')),
        ('AvailableConnector', properties.get('connectorName')),
        ('DisplayName', properties.get('displayName')),
        ('Status', properties.get('overallStatus') or _first_status(properties)),
        ('State', properties.get('provisioningState')),
    ])


def _access_policy_row(item):
    properties = item.get('properties') or {}
    principal = properties.get('principal') or {}
    identity = principal.get('identity') or {}
    return OrderedDict([
        ('Name', item.get('name')),
        ('PrincipalType', principal.get('type')),
        ('ObjectId', identity.get('objectId')),
        ('TenantId', identity.get('tenantId')),
        ('State', properties.get('provisioningState')),
    ])


def _mcp_server_config_row(item):
    properties = item.get('properties') or {}
    return OrderedDict([
        ('Name', item.get('name')),
        ('State', properties.get('state')),
        ('ProvisioningState', properties.get('provisioningState')),
        ('Endpoint', properties.get('mcpEndpointUrl')),
    ])


def _trigger_config_row(item):
    properties = item.get('properties') or {}
    connection_details = properties.get('connectionDetails') or {}
    return OrderedDict([
        ('Name', item.get('name')),
        ('AvailableConnector', connection_details.get('connectorName')),
        ('Connection', connection_details.get('connectionName')),
        ('Operation', properties.get('operationName')),
        ('State', properties.get('state')),
        ('ProvisioningState', properties.get('provisioningState')),
    ])


def _first_status(properties):
    statuses = properties.get('statuses') or []
    if statuses:
        return statuses[0].get('status')
    return None