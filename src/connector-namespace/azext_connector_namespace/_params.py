from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    get_enum_type,
    get_location_type,
    resource_group_name_type,
    tags_type,
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group


IDENTITY_TYPES = ['None', 'SystemAssigned']
OPERATION_TYPES = ['action', 'trigger']


def load_arguments(self, _):
    namespace_name_type = CLIArgumentType(options_list=['--namespace-name'], metavar='NAME', required=True,
                                          help='Connector Namespace name.')
    name_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME', required=True,
                                help='Name of the resource.')
    body_type = CLIArgumentType(options_list=['--body', '-b'], help='JSON request body. Use @{file} to load from a file.')

    for scope in [
            'connector-namespace',
            'connector-namespace available-connector',
            'connector-namespace connection',
            'connector-namespace connection operation',
            'connector-namespace connection access-policy',
            'connector-namespace mcp-server-config',
            'connector-namespace trigger-config',
            'connector-namespace trigger-config run']:
        with self.argument_context(scope) as c:
            c.argument('resource_group_name', arg_type=resource_group_name_type)

    for scope in [
            'connector-namespace create',
            'connector-namespace show',
            'connector-namespace update',
            'connector-namespace delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type)

    with self.argument_context('connector-namespace create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('identity_type', options_list=['--identity-type'], arg_type=get_enum_type(IDENTITY_TYPES), default='SystemAssigned',
                   help='Managed identity type for the Connector Namespace.')

    with self.argument_context('connector-namespace update') as c:
        c.argument('tags', tags_type)
        c.argument('identity_type', options_list=['--identity-type'], arg_type=get_enum_type(IDENTITY_TYPES),
                   help='Managed identity type for the Connector Namespace.')

    for scope in [
            'connector-namespace available-connector',
            'connector-namespace connection',
            'connector-namespace connection operation',
            'connector-namespace connection access-policy',
            'connector-namespace mcp-server-config',
            'connector-namespace trigger-config',
            'connector-namespace trigger-config run']:
        with self.argument_context(scope) as c:
            c.argument('gateway_name', namespace_name_type)

    with self.argument_context('connector-namespace available-connector show') as c:
        c.argument('name', options_list=['--name', '-n'], metavar='NAME', required=True,
                   help='Name of the available connector.')
        c.argument('export', options_list=['--export'], action='store_true', help='Return the exported Swagger/OpenAPI definition.')

    for scope in [
            'connector-namespace connection create',
            'connector-namespace connection show',
            'connector-namespace connection update',
            'connector-namespace connection delete',
            'connector-namespace connection list-consent-links',
            'connector-namespace connection authorize',
            'connector-namespace connection invoke',
            'connector-namespace connection operation list',
            'connector-namespace connection operation show']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type)

    with self.argument_context('connector-namespace connection invoke') as c:
        c.argument('operation_id', options_list=['--operation-id'], help='Swagger operationId to invoke.')
        c.argument('path', options_list=['--path'], help='Runtime path to invoke, such as /v2/Mail. Use as an escape hatch when --operation-id is not available.')
        c.argument('method', options_list=['--method'], help='HTTP method. Defaults to the Swagger operation method, or GET when --path is used.')
        c.argument('body', body_type)
        c.argument('parameter', options_list=['--parameter'], nargs='*', help='Operation parameter in NAME=VALUE format. Routed by Swagger location when --operation-id is used; otherwise sent as a query parameter.')
        c.argument('query_parameter', options_list=['--query-parameter'], nargs='*', help='Query parameter in NAME=VALUE format.')
        c.argument('header', options_list=['--header'], nargs='*', help='HTTP header in NAME=VALUE format.')

    with self.argument_context('connector-namespace connection operation list') as c:
        c.argument('operation_type', options_list=['--operation-type'], arg_type=get_enum_type(OPERATION_TYPES),
                   help='Filter operations by type. Actions can be invoked directly. Triggers can be used to create trigger configs.')

    with self.argument_context('connector-namespace connection operation show') as c:
        c.argument('operation_id', options_list=['--operation-id'], required=True, help='Swagger operationId to inspect.')

    for scope in ['connector-namespace connection create', 'connector-namespace connection update']:
        with self.argument_context(scope) as c:
            c.argument('available_connector', options_list=['--available-connector'], help='Name of the available connector to instantiate.')
            c.argument('body', body_type)

    with self.argument_context('connector-namespace connection list-consent-links') as c:
        c.argument('redirect_url', options_list=['--redirect-url'], default='https://portal.azure.com',
                   help='OAuth redirect URL used when requesting consent links.')

    with self.argument_context('connector-namespace connection authorize') as c:
        c.argument('redirect_url', options_list=['--redirect-url'], default='https://portal.azure.com',
                   help='OAuth redirect URL used when requesting consent links.')
        c.argument('no_browser', options_list=['--no-browser'], action='store_true', help='Print the authorization URL without opening a browser.')

    for scope in [
            'connector-namespace connection access-policy create',
            'connector-namespace connection access-policy show',
            'connector-namespace connection access-policy update',
            'connector-namespace connection access-policy delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type)

    with self.argument_context('connector-namespace connection access-policy') as c:
        c.argument('connection_name', options_list=['--connection-name'], required=True, help='Connection name.')

    for scope in [
            'connector-namespace connection access-policy create',
            'connector-namespace connection access-policy update']:
        with self.argument_context(scope) as c:
            c.argument('body', body_type)
            c.argument('object_id', options_list=['--object-id'], help='Azure AD object ID to grant access.')
            c.argument('tenant_id', options_list=['--tenant-id'], help='Azure AD tenant ID for the principal.')
            c.argument('principal_type', options_list=['--principal-type'], default='ActiveDirectory', help='Principal type.')

    for scope in [
            'connector-namespace mcp-server-config create',
            'connector-namespace mcp-server-config show',
            'connector-namespace mcp-server-config update',
            'connector-namespace mcp-server-config delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type)

    for scope in [
            'connector-namespace mcp-server-config create',
            'connector-namespace mcp-server-config update']:
        with self.argument_context(scope) as c:
            c.argument('body', body_type)

    for scope in [
            'connector-namespace trigger-config create',
            'connector-namespace trigger-config show',
            'connector-namespace trigger-config update',
            'connector-namespace trigger-config delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type)

    with self.argument_context('connector-namespace trigger-config run') as c:
        c.argument('trigger_config_name', options_list=['--trigger-config-name'], metavar='NAME', required=True,
                   help='Trigger config name.')

    with self.argument_context('connector-namespace trigger-config run list') as c:
        c.argument('top', options_list=['--top'], type=int, help='Maximum number of trigger runs to return.')
        c.argument('all_runs', options_list=['--all'], action='store_true',
                   help='Retrieve all pages of trigger runs. Use carefully for large run histories.')

    with self.argument_context('connector-namespace trigger-config run show') as c:
        c.argument('run_id', options_list=['--run-id'], metavar='ID', required=True,
                   help='Trigger run ID from trigger-config run list.')

    for scope in [
            'connector-namespace trigger-config create',
            'connector-namespace trigger-config update']:
        with self.argument_context(scope) as c:
            c.argument('body', body_type)
            c.argument('available_connector', options_list=['--available-connector'], help='Name of the available connector for the trigger.')
            c.argument('connection_name', options_list=['--connection-name'], help='Connection name used by the trigger.')
            c.argument('operation_name', options_list=['--operation-name'], help='Connector trigger operation name.')
            c.argument('callback_url', options_list=['--callback-url'], help='Callback URL invoked by the Connector Namespace.')
            c.argument('http_method', options_list=['--http-method'], help='HTTP method used for the callback. Defaults to Post on create.')
            c.argument('parameter', options_list=['--parameter'], nargs='*', help='Trigger parameter in NAME=VALUE format. Repeat or separate with spaces.')
            c.argument('description', options_list=['--description'], help='Trigger config description.')
            c.argument('trigger_type', options_list=['--type'], help='Trigger config type.')
