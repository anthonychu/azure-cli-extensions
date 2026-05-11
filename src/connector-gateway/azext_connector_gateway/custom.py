import webbrowser
from urllib.parse import quote, unquote

from azure.cli.core.azclierror import (CLIError, ClientRequestError, HTTPError, InvalidArgumentValueError,
                                       RequiredArgumentMissingError)

from azext_connector_gateway._client import ConnectorGatewayClient, RUNTIME_RESOURCE
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


def list_connection_operations(cmd, resource_group_name, gateway_name, name):
    connection, swagger = _get_connection_and_swagger(cmd, resource_group_name, gateway_name, name)
    return [
        build_operation_summary(path, method, operation, connection)
        for path, method, operation in iter_swagger_operations(swagger)
    ]


def show_connection_operation(cmd, resource_group_name, gateway_name, name, operation_id):
    connection, swagger = _get_connection_and_swagger(cmd, resource_group_name, gateway_name, name)
    path, method, operation = find_swagger_operation(swagger, operation_id)
    return build_operation_summary(path, method, operation, connection, swagger=swagger, include_schema_details=True)


def invoke_connection(cmd, resource_group_name, gateway_name, name, operation_id=None, path=None, method=None, body=None,
                      parameter=None, query_parameter=None, header=None):
    if operation_id and path:
        raise InvalidArgumentValueError('Use either --operation-id or --path, but not both.')
    if not operation_id and not path:
        raise RequiredArgumentMissingError('Either --operation-id or --path is required.')

    client = ConnectorGatewayClient(cmd)
    connection = client.request('GET', client.child_path(resource_group_name, gateway_name, 'connections', name))
    connection_properties = connection.get('properties') or {}
    runtime_url = connection_properties.get('connectionRuntimeUrl')
    if not runtime_url:
        raise InvalidArgumentValueError(
            "Connection '{}' does not expose properties.connectionRuntimeUrl.".format(name))

    operation = None
    operation_path = path
    operation_method = method
    if operation_id:
        connector_name = _connection_connector_name(connection)
        swagger = client.request(
            'GET', client.child_path(resource_group_name, gateway_name, 'managedApis', connector_name),
            query={'export': True})
        operation_path, operation_method, operation = find_swagger_operation(swagger, operation_id)
        operation_method = method or operation_method
    else:
        operation_method = method or 'GET'

    body_payload = ensure_object(body) if body else None
    validate_required_body(operation, body_payload)
    query_parameters, headers, path_parameters = build_runtime_parameters(
        operation, parameter=parameter, query_parameter=query_parameter, header=header)
    runtime_request_url = build_runtime_url(runtime_url, operation_path, path_parameters)

    try:
        return client.runtime_request(
            operation_method, runtime_request_url, body=body_payload, headers=headers, query=query_parameters)
    except HTTPError as ex:
        raise ClientRequestError(format_runtime_http_error(
            ex, resource_group_name=resource_group_name, gateway_name=gateway_name, connection_name=name))
    except CLIError as ex:
        raise ClientRequestError(format_runtime_cli_error(ex))


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


def iter_swagger_operations(swagger):
    for path, path_item in sorted((swagger or {}).get('paths', {}).items()):
        for method, operation in sorted((path_item or {}).items()):
            if method.lower() not in ['delete', 'get', 'head', 'options', 'patch', 'post', 'put']:
                continue
            if isinstance(operation, dict):
                yield path, method.lower(), operation


def find_swagger_operation(swagger, operation_id):
    for path, method, operation in iter_swagger_operations(swagger):
        if operation.get('operationId') == operation_id:
            return path, method, operation
    raise InvalidArgumentValueError("Operation '{}' was not found in the connector Swagger.".format(operation_id))


def build_operation_summary(path, method, operation, connection, swagger=None, include_schema_details=False):
    runtime_url = ((connection or {}).get('properties') or {}).get('connectionRuntimeUrl')
    body_parameter = next((parameter for parameter in operation.get('parameters') or []
                           if parameter.get('in') == 'body'), None)
    body_schema = (body_parameter or {}).get('schema')
    summary = {
        'operationId': operation.get('operationId'),
        'summary': operation.get('summary'),
        'description': operation.get('description'),
        'method': method.upper(),
        'path': path,
        'runtimePath': _runtime_path_from_operation_path(path),
        'runtimeUrl': build_runtime_url(runtime_url, path) if runtime_url and _path_has_only_connection_id(path) else None,
        'bodySchema': body_schema,
        'parameters': [_summarize_parameter(parameter) for parameter in operation.get('parameters') or []],
    }
    if include_schema_details:
        resolved_body_schema = resolve_swagger_schema(swagger, body_schema) if body_schema else None
        summary['resolvedBodySchema'] = resolved_body_schema
        summary['requestBodyExample'] = build_schema_example(resolved_body_schema) if resolved_body_schema else None
    return summary


def resolve_swagger_schema(swagger, schema, seen_refs=None):
    if isinstance(schema, list):
        return [resolve_swagger_schema(swagger, item, seen_refs) for item in schema]
    if not isinstance(schema, dict):
        return schema

    ref = schema.get('$ref')
    if ref:
        seen_refs = seen_refs or set()
        if ref in seen_refs:
            return dict(schema)
        target = _resolve_local_ref(swagger, ref)
        if target is None:
            return dict(schema)
        resolved = resolve_swagger_schema(swagger, target, seen_refs | {ref})
        sibling_values = {
            key: resolve_swagger_schema(swagger, value, seen_refs | {ref})
            for key, value in schema.items()
            if key != '$ref'
        }
        if sibling_values and isinstance(resolved, dict):
            resolved = dict(resolved)
            resolved.update(sibling_values)
        return resolved

    return {key: resolve_swagger_schema(swagger, value, seen_refs) for key, value in schema.items()}


def build_schema_example(schema):
    return _schema_example(schema)


def build_runtime_url(connection_runtime_url, operation_path, path_parameters=None):
    if not operation_path:
        raise RequiredArgumentMissingError('--path is required when --operation-id is not used.')

    runtime_path = operation_path
    if runtime_path.startswith('/{connectionId}'):
        runtime_path = runtime_path[len('/{connectionId}'):]
    elif runtime_path.startswith('{connectionId}'):
        runtime_path = runtime_path[len('{connectionId}'):]
    if not runtime_path:
        runtime_path = '/'
    if not runtime_path.startswith('/'):
        runtime_path = '/' + runtime_path

    for name, value in (path_parameters or {}).items():
        runtime_path = runtime_path.replace('{{{}}}'.format(name), quote(str(value), safe=''))

    if '{' in runtime_path or '}' in runtime_path:
        raise RequiredArgumentMissingError(
            'Missing path parameter values. Use --parameter NAME=VALUE for required path parameters.')
    return '{}{}'.format(connection_runtime_url.rstrip('/'), runtime_path)


def build_runtime_parameters(operation=None, parameter=None, query_parameter=None, header=None):
    query_parameters = _parse_key_value_map(query_parameter)
    headers = _parse_key_value_map(header)
    path_parameters = {}
    generic_parameters = _parse_key_value_map(parameter)
    operation_parameters = _operation_parameters_by_name(operation)

    for name, value in generic_parameters.items():
        parameter_metadata = operation_parameters.get(name) if operation_parameters else None
        location = (parameter_metadata or {}).get('in')
        if location == 'path':
            path_parameters[name] = value
        elif location == 'header':
            headers[name] = value
        elif location == 'body':
            raise InvalidArgumentValueError(
                "Parameter '{}' is a body parameter. Use --body to provide the request body.".format(name))
        else:
            query_parameters[name] = value

    if operation:
        for parameter_metadata in operation.get('parameters') or []:
            if parameter_metadata.get('name') == 'connectionId':
                continue
            if not parameter_metadata.get('required'):
                continue
            name = parameter_metadata.get('name')
            location = parameter_metadata.get('in')
            if location == 'path' and name not in path_parameters:
                raise RequiredArgumentMissingError(
                    "Required path parameter '{}' is missing. Use --parameter {}=VALUE.".format(name, name))
            if location == 'query' and name not in query_parameters:
                raise RequiredArgumentMissingError(
                    "Required query parameter '{}' is missing. Use --parameter {}=VALUE.".format(name, name))
            if location == 'header' and name not in headers:
                raise RequiredArgumentMissingError(
                    "Required header parameter '{}' is missing. Use --header {}=VALUE.".format(name, name))

    return query_parameters, headers, path_parameters


def validate_required_body(operation, body):
    if not operation:
        return
    for parameter_metadata in operation.get('parameters') or []:
        if parameter_metadata.get('in') == 'body' and parameter_metadata.get('required') and body is None:
            raise RequiredArgumentMissingError(
                "Operation '{}' requires a request body. Use --body @file or --body '{{...}}'.".format(
                    operation.get('operationId')))


def format_runtime_http_error(error, resource_group_name, gateway_name, connection_name):
    response = getattr(error, 'response', None)
    status_code = getattr(response, 'status_code', None)
    service_message = _response_message(response) or str(error)
    lower_message = service_message.lower()

    if status_code in [401, 403]:
        return """Runtime authorization failed for connection '{}'.

The signed-in Azure identity can acquire a runtime token, but the Connector Gateway runtime rejected the call. Grant a connection access policy, then retry:

az connector-gateway connection access-policy create -g {} --gateway-name {} --connection-name {} -n <policy-name> --object-id <object-id> --tenant-id <tenant-id>

For your signed-in user, you can usually get these values with:
az ad signed-in-user show --query id -o tsv
az account show --query tenantId -o tsv

If the connection itself is not authenticated, run:
az connector-gateway connection authorize -g {} --gateway-name {} -n {}

Service response: {}""".format(
            connection_name, resource_group_name, gateway_name, connection_name,
            resource_group_name, gateway_name, connection_name, service_message)

    if 'audience' in lower_message or 'token exchange' in lower_message or 'tokenexchange' in lower_message:
        return """Connector Gateway runtime token exchange failed.

The extension expected the runtime token audience to be '{}'. If this keeps happening, verify the cloud environment and update the connector-gateway extension.

Service response: {}""".format(RUNTIME_RESOURCE, service_message)

    return "Connector Gateway runtime invocation failed with status {}. Service response: {}".format(
        status_code or 'unknown', service_message)


def format_runtime_cli_error(error):
    return """Connector Gateway runtime invocation could not acquire or attach an Azure token.

Run `az login`, verify the correct tenant and subscription with `az account show`, then retry. If needed, select the subscription with `az account set --subscription <subscription>`.

Details: {}""".format(error)


def _get_connection_and_swagger(cmd, resource_group_name, gateway_name, connection_name):
    client = ConnectorGatewayClient(cmd)
    connection = client.request('GET', client.child_path(resource_group_name, gateway_name, 'connections', connection_name))
    connector_name = _connection_connector_name(connection)
    swagger = client.request(
        'GET', client.child_path(resource_group_name, gateway_name, 'managedApis', connector_name),
        query={'export': True})
    return connection, swagger


def _connection_connector_name(connection):
    connector_name = ((connection or {}).get('properties') or {}).get('connectorName')
    if not connector_name:
        raise InvalidArgumentValueError('The connection does not include properties.connectorName.')
    return connector_name


def _resolve_local_ref(swagger, ref):
    if not ref.startswith('#/'):
        return None
    current = swagger
    for token in ref[2:].split('/'):
        token = unquote(token).replace('~1', '/').replace('~0', '~')
        if isinstance(current, dict):
            current = current.get(token)
        elif isinstance(current, list) and token.isdigit():
            current = current[int(token)]
        else:
            return None
        if current is None:
            return None
    return current


def _schema_example(schema, property_name=None, depth=0):
    if not isinstance(schema, dict) or depth > 8:
        return None
    if 'example' in schema:
        return schema.get('example')
    if 'default' in schema:
        return schema.get('default')
    enum_values = schema.get('enum')
    if enum_values:
        return enum_values[0]

    if schema.get('allOf'):
        return _merge_schema_examples([_schema_example(item, property_name, depth + 1)
                                       for item in schema.get('allOf')])
    for composition_key in ['oneOf', 'anyOf']:
        if schema.get(composition_key):
            return _schema_example(schema[composition_key][0], property_name, depth + 1)

    schema_type = _schema_type(schema)
    if schema_type == 'object' or schema.get('properties'):
        return _object_schema_example(schema, depth)
    if schema_type == 'array':
        return [_schema_example(schema.get('items') or {}, property_name, depth + 1)]
    if schema_type == 'integer':
        return 0
    if schema_type == 'number':
        return 0.0
    if schema_type == 'boolean':
        return False
    if schema_type == 'string' or schema_type is None:
        return _string_schema_example(schema, property_name)
    return None


def _object_schema_example(schema, depth):
    properties = schema.get('properties') or {}
    if not properties:
        additional_properties = schema.get('additionalProperties')
        if isinstance(additional_properties, dict):
            return {'propertyName': _schema_example(additional_properties, 'propertyName', depth + 1)}
        return {}

    required_names = schema.get('required') or []
    property_names = [name for name in required_names if name in properties]
    if not property_names:
        property_names = list(properties.keys())[:5]
    return {name: _schema_example(properties[name], name, depth + 1) for name in property_names}


def _schema_type(schema):
    schema_type = schema.get('type')
    if isinstance(schema_type, list):
        for item in schema_type:
            if item != 'null':
                return item
        return schema_type[0] if schema_type else None
    return schema_type


def _string_schema_example(schema, property_name=None):
    schema_format = (schema.get('format') or '').lower()
    lower_name = (property_name or '').lower()
    if schema_format == 'email' or lower_name in ['to', 'cc', 'bcc'] or 'email' in lower_name:
        return 'user@example.com'
    if schema_format in ['uri', 'url'] or 'url' in lower_name or 'uri' in lower_name:
        return 'https://example.com'
    if schema_format == 'uuid' or lower_name.endswith('id'):
        return '00000000-0000-0000-0000-000000000000'
    if schema_format == 'date-time':
        return '2026-05-11T00:00:00Z'
    if schema_format == 'date':
        return '2026-05-11'
    return 'string'


def _merge_schema_examples(examples):
    merged = {}
    for example in examples:
        if isinstance(example, dict):
            merged.update(example)
        elif example is not None:
            return example
    return merged


def _runtime_path_from_operation_path(path):
    if path.startswith('/{connectionId}'):
        result = path[len('/{connectionId}'):]
    elif path.startswith('{connectionId}'):
        result = path[len('{connectionId}'):]
    else:
        result = path
    return result or '/'


def _path_has_only_connection_id(path):
    runtime_path = _runtime_path_from_operation_path(path)
    return '{' not in runtime_path and '}' not in runtime_path


def _summarize_parameter(parameter):
    return {
        'name': parameter.get('name'),
        'in': parameter.get('in'),
        'required': parameter.get('required', False),
        'type': parameter.get('type'),
        'summary': parameter.get('x-ms-summary'),
        'description': parameter.get('description'),
        'schema': parameter.get('schema'),
    }


def _operation_parameters_by_name(operation):
    if not operation:
        return {}
    return {parameter.get('name'): parameter for parameter in operation.get('parameters') or [] if parameter.get('name')}


def _parse_key_value_map(values):
    result = {}
    for pair in parse_key_value_pairs(values):
        result[pair['name']] = pair['value']
    return result


def _response_message(response):
    if response is None:
        return None
    try:
        payload = response.json()
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        for key in ['message', 'Message']:
            if payload.get(key):
                return _truncate(payload.get(key))
        error = payload.get('error')
        if isinstance(error, dict):
            return _truncate(error.get('message') or error.get('Message') or error.get('code'))
        if isinstance(error, str):
            return _truncate(error)
    return _truncate(getattr(response, 'text', None))


def _truncate(value, limit=1200):
    if value is None:
        return None
    value = str(value)
    if len(value) <= limit:
        return value
    return value[:limit] + '...'


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