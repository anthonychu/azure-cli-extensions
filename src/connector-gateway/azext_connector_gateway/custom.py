import webbrowser

from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError

from azext_connector_gateway._client import ConnectorGatewayClient
from azext_connector_gateway._validators import ensure_object, parse_key_value_pairs


def list_gateways(cmd, resource_group_name=None):
    client = ConnectorGatewayClient(cmd)
    result = client.request('GET', client.gateway_collection_path(resource_group_name))
    return (result or {}).get('value', [])


def show_gateway(cmd, resource_group_name, name):
    client = ConnectorGatewayClient(cmd)
    return client.request('GET', client.gateway_path(resource_group_name, name))


def create_gateway(cmd, resource_group_name, name, location, tags=None, identity_type='SystemAssigned'):
    client = ConnectorGatewayClient(cmd)
    body = build_gateway_body(location=location, tags=tags, identity_type=identity_type)
    return client.request('PUT', client.gateway_path(resource_group_name, name), body=body)


def update_gateway(cmd, resource_group_name, name, tags=None, identity_type=None):
    client = ConnectorGatewayClient(cmd)
    existing = client.request('GET', client.gateway_path(resource_group_name, name))
    body = build_gateway_update_body(existing, tags=tags, identity_type=identity_type)
    return client.request('PUT', client.gateway_path(resource_group_name, name), body=body)


def delete_gateway(cmd, resource_group_name, name):
    client = ConnectorGatewayClient(cmd)
    return client.request('DELETE', client.gateway_path(resource_group_name, name))


def list_available_connectors(cmd, resource_group_name, gateway_name):
    client = ConnectorGatewayClient(cmd)
    result = client.request('GET', client.child_collection_path(resource_group_name, gateway_name, 'managedApis'))
    return (result or {}).get('value', [])


def show_available_connector(cmd, resource_group_name, gateway_name, name, export=False):
    client = ConnectorGatewayClient(cmd)
    return client.request(
        'GET', client.child_path(resource_group_name, gateway_name, 'managedApis', name),
        query={'export': True} if export else None)


def list_connections(cmd, resource_group_name, gateway_name):
    return _list_gateway_child(cmd, resource_group_name, gateway_name, 'connections')


def show_connection(cmd, resource_group_name, gateway_name, name):
    return _show_gateway_child(cmd, resource_group_name, gateway_name, 'connections', name)


def create_connection(cmd, resource_group_name, gateway_name, name, available_connector=None, body=None):
    request_body = ensure_object(body) if body else build_connection_body(available_connector)
    client = ConnectorGatewayClient(cmd)
    return client.request('PUT', client.child_path(resource_group_name, gateway_name, 'connections', name), body=request_body)


def update_connection(cmd, resource_group_name, gateway_name, name, available_connector=None, body=None):
    client = ConnectorGatewayClient(cmd)
    request_body = ensure_object(body) if body else None
    if request_body is None:
        if not available_connector:
            return show_connection(cmd, resource_group_name, gateway_name, name)
        existing = show_connection(cmd, resource_group_name, gateway_name, name)
        request_body = {'properties': existing.get('properties') or {}}
        request_body['properties']['connectorName'] = available_connector
    return client.request('PUT', client.child_path(resource_group_name, gateway_name, 'connections', name), body=request_body)


def delete_connection(cmd, resource_group_name, gateway_name, name):
    return _delete_gateway_child(cmd, resource_group_name, gateway_name, 'connections', name)


def list_connection_consent_links(cmd, resource_group_name, gateway_name, name, redirect_url='https://portal.azure.com'):
    client = ConnectorGatewayClient(cmd)
    body = build_consent_body(redirect_url)
    path = '{}/listConsentLinks'.format(client.child_path(resource_group_name, gateway_name, 'connections', name))
    return client.request('POST', path, body=body)


def authorize_connection(cmd, resource_group_name, gateway_name, name, redirect_url='https://portal.azure.com', no_browser=False):
    result = list_connection_consent_links(cmd, resource_group_name, gateway_name, name, redirect_url)
    link_entry = extract_first_consent_link(result)
    link = link_entry.get('link')
    opened = False
    if link and not no_browser:
        opened = webbrowser.open(link)
    return {
        'opened': opened,
        'status': link_entry.get('status'),
        'displayName': link_entry.get('displayName'),
        'firstPartyLoginUri': link_entry.get('firstPartyLoginUri'),
        'link': link,
    }


def list_access_policies(cmd, resource_group_name, gateway_name, connection_name):
    client = ConnectorGatewayClient(cmd)
    result = client.request('GET', client.access_policy_collection_path(resource_group_name, gateway_name, connection_name))
    return (result or {}).get('value', [])


def show_access_policy(cmd, resource_group_name, gateway_name, connection_name, name):
    client = ConnectorGatewayClient(cmd)
    return client.request('GET', client.access_policy_path(resource_group_name, gateway_name, connection_name, name))


def create_access_policy(cmd, resource_group_name, gateway_name, connection_name, name, object_id=None, tenant_id=None,
                         principal_type='ActiveDirectory', body=None):
    request_body = ensure_object(body) if body else build_access_policy_body(object_id, tenant_id, principal_type)
    client = ConnectorGatewayClient(cmd)
    return client.request(
        'PUT', client.access_policy_path(resource_group_name, gateway_name, connection_name, name), body=request_body)


def update_access_policy(cmd, resource_group_name, gateway_name, connection_name, name, object_id=None, tenant_id=None,
                         principal_type='ActiveDirectory', body=None):
    return create_access_policy(
        cmd, resource_group_name, gateway_name, connection_name, name, object_id, tenant_id, principal_type, body)


def delete_access_policy(cmd, resource_group_name, gateway_name, connection_name, name):
    client = ConnectorGatewayClient(cmd)
    return client.request('DELETE', client.access_policy_path(resource_group_name, gateway_name, connection_name, name))


def list_mcp_server_configs(cmd, resource_group_name, gateway_name):
    return _list_gateway_child(cmd, resource_group_name, gateway_name, 'mcpserverconfigs')


def show_mcp_server_config(cmd, resource_group_name, gateway_name, name):
    return _show_gateway_child(cmd, resource_group_name, gateway_name, 'mcpserverconfigs', name)


def create_mcp_server_config(cmd, resource_group_name, gateway_name, name, body):
    if not body:
        raise RequiredArgumentMissingError('--body is required.')
    request_body = ensure_object(body)
    client = ConnectorGatewayClient(cmd)
    return client.request('PUT', client.child_path(resource_group_name, gateway_name, 'mcpserverconfigs', name), body=request_body)


def update_mcp_server_config(cmd, resource_group_name, gateway_name, name, body):
    return create_mcp_server_config(cmd, resource_group_name, gateway_name, name, body)


def delete_mcp_server_config(cmd, resource_group_name, gateway_name, name):
    return _delete_gateway_child(cmd, resource_group_name, gateway_name, 'mcpserverconfigs', name)


def list_trigger_configs(cmd, resource_group_name, gateway_name):
    return _list_gateway_child(cmd, resource_group_name, gateway_name, 'triggerconfigs')


def show_trigger_config(cmd, resource_group_name, gateway_name, name):
    return _show_gateway_child(cmd, resource_group_name, gateway_name, 'triggerconfigs', name)


def create_trigger_config(cmd, resource_group_name, gateway_name, name, available_connector=None, connection_name=None,
                          operation_name=None, callback_url=None, http_method='Post', parameter=None, description=None,
                          trigger_type=None, body=None):
    request_body = ensure_object(body) if body else build_trigger_config_body(
        available_connector=available_connector,
        connection_name=connection_name,
        operation_name=operation_name,
        callback_url=callback_url,
        http_method=http_method or 'Post',
        parameter=parameter,
        description=description,
        trigger_type=trigger_type)
    client = ConnectorGatewayClient(cmd)
    return client.request('PUT', client.child_path(resource_group_name, gateway_name, 'triggerconfigs', name), body=request_body)


def update_trigger_config(cmd, resource_group_name, gateway_name, name, available_connector=None, connection_name=None,
                          operation_name=None, callback_url=None, http_method='Post', parameter=None, description=None,
                          trigger_type=None, body=None):
    if body:
        return create_trigger_config(cmd, resource_group_name, gateway_name, name, body=body)
    existing = show_trigger_config(cmd, resource_group_name, gateway_name, name)
    properties = existing.get('properties') or {}
    request_body = {'properties': properties}
    if operation_name:
        properties['operationName'] = operation_name
    if available_connector or connection_name:
        connection_details = properties.setdefault('connectionDetails', {})
        if available_connector:
            connection_details['connectorName'] = available_connector
        if connection_name:
            connection_details['connectionName'] = connection_name
    if callback_url or http_method:
        notification_details = properties.setdefault('notificationDetails', {})
        if callback_url:
            notification_details['callbackUrl'] = callback_url
        if http_method:
            notification_details['httpMethod'] = http_method
    if parameter is not None:
        properties['parameters'] = parse_key_value_pairs(parameter)
    if description is not None:
        properties['description'] = description
    if trigger_type is not None:
        properties['type'] = trigger_type
    client = ConnectorGatewayClient(cmd)
    return client.request('PUT', client.child_path(resource_group_name, gateway_name, 'triggerconfigs', name), body=request_body)


def delete_trigger_config(cmd, resource_group_name, gateway_name, name):
    return _delete_gateway_child(cmd, resource_group_name, gateway_name, 'triggerconfigs', name)


def build_gateway_body(location, tags=None, identity_type='SystemAssigned'):
    body = {'location': location, 'properties': {}}
    if tags is not None:
        body['tags'] = tags
    if identity_type:
        body['identity'] = {'type': identity_type}
    return body


def build_gateway_update_body(existing, tags=None, identity_type=None):
    body = {
        'location': existing.get('location'),
        'properties': {},
    }
    existing_tags = existing.get('tags')
    if tags is not None:
        body['tags'] = tags
    elif existing_tags is not None:
        body['tags'] = existing_tags

    identity = _gateway_identity_for_put(existing.get('identity'), identity_type=identity_type)
    if identity:
        body['identity'] = identity
    return body


def _gateway_identity_for_put(existing_identity, identity_type=None):
    if identity_type is not None:
        return {'type': identity_type}
    if not existing_identity:
        return None

    identity = {}
    if existing_identity.get('type'):
        identity['type'] = existing_identity.get('type')
    user_assigned_identities = existing_identity.get('userAssignedIdentities')
    if user_assigned_identities:
        identity['userAssignedIdentities'] = {resource_id: {} for resource_id in user_assigned_identities}
    return identity or None


def build_connection_body(available_connector):
    if not available_connector:
        raise RequiredArgumentMissingError('Either --available-connector or --body is required.')
    return {'properties': {'connectorName': available_connector}}


def build_consent_body(redirect_url):
    return {'parameters': [{'redirectUrl': redirect_url, 'parameterName': 'token'}]}


def extract_first_consent_link(result):
    values = (result or {}).get('value') or []
    if not values:
        raise InvalidArgumentValueError('The service did not return any consent links.')
    link_entry = values[0]
    if not link_entry.get('link'):
        raise InvalidArgumentValueError('The service returned a consent link entry without a link.')
    return link_entry


def build_access_policy_body(object_id, tenant_id, principal_type='ActiveDirectory'):
    if not object_id or not tenant_id:
        raise RequiredArgumentMissingError('Either --body or both --object-id and --tenant-id are required.')
    return {
        'properties': {
            'principal': {
                'type': principal_type,
                'identity': {
                    'objectId': object_id,
                    'tenantId': tenant_id,
                }
            }
        }
    }


def build_trigger_config_body(available_connector, connection_name, operation_name, callback_url, http_method='Post',
                              parameter=None, description=None, trigger_type=None):
    missing = []
    for value, name in [
            (available_connector, '--available-connector'),
            (connection_name, '--connection-name'),
            (operation_name, '--operation-name'),
            (callback_url, '--callback-url')]:
        if not value:
            missing.append(name)
    if missing:
        raise RequiredArgumentMissingError('Either --body or {} are required.'.format(', '.join(missing)))
    properties = {
        'operationName': operation_name,
        'connectionDetails': {
            'connectorName': available_connector,
            'connectionName': connection_name,
        },
        'notificationDetails': {
            'callbackUrl': callback_url,
            'httpMethod': http_method or 'Post',
        }
    }
    parameters = parse_key_value_pairs(parameter)
    if parameters:
        properties['parameters'] = parameters
    if description is not None:
        properties['description'] = description
    if trigger_type is not None:
        properties['type'] = trigger_type
    return {'properties': properties}


def _list_gateway_child(cmd, resource_group_name, gateway_name, collection):
    client = ConnectorGatewayClient(cmd)
    result = client.request('GET', client.child_collection_path(resource_group_name, gateway_name, collection))
    return (result or {}).get('value', [])


def _show_gateway_child(cmd, resource_group_name, gateway_name, collection, name):
    client = ConnectorGatewayClient(cmd)
    return client.request('GET', client.child_path(resource_group_name, gateway_name, collection, name))


def _delete_gateway_child(cmd, resource_group_name, gateway_name, collection, name):
    client = ConnectorGatewayClient(cmd)
    return client.request('DELETE', client.child_path(resource_group_name, gateway_name, collection, name))