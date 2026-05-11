from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    get_enum_type,
    get_location_type,
    resource_group_name_type,
    tags_type,
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group


IDENTITY_TYPES = ['None', 'SystemAssigned']


def load_arguments(self, _):
    gateway_name_type = CLIArgumentType(options_list=['--gateway-name'], metavar='NAME', required=True,
                                        help='Connector Gateway name.')
    name_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME', required=True,
                                help='Name of the resource.')
    body_type = CLIArgumentType(options_list=['--body', '-b'], help='JSON request body. Use @{file} to load from a file.')

    for scope in [
            'connector-gateway',
            'connector-gateway available-connector',
            'connector-gateway connection',
            'connector-gateway connection access-policy',
            'connector-gateway mcp-server-config',
            'connector-gateway trigger-config']:
        with self.argument_context(scope) as c:
            c.argument('resource_group_name', arg_type=resource_group_name_type)

    for scope in [
            'connector-gateway create',
            'connector-gateway show',
            'connector-gateway update',
            'connector-gateway delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type)

    with self.argument_context('connector-gateway create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('identity_type', options_list=['--identity-type'], arg_type=get_enum_type(IDENTITY_TYPES), default='SystemAssigned',
                   help='Managed identity type for the Connector Gateway.')

    with self.argument_context('connector-gateway update') as c:
        c.argument('tags', tags_type)
        c.argument('identity_type', options_list=['--identity-type'], arg_type=get_enum_type(IDENTITY_TYPES),
                   help='Managed identity type for the Connector Gateway.')

    for scope in [
            'connector-gateway available-connector',
            'connector-gateway connection',
            'connector-gateway connection access-policy',
            'connector-gateway mcp-server-config',
            'connector-gateway trigger-config']:
        with self.argument_context(scope) as c:
            c.argument('gateway_name', gateway_name_type)

    with self.argument_context('connector-gateway available-connector show') as c:
        c.argument('name', options_list=['--name', '-n'], metavar='NAME', required=True,
                   help='Name of the available connector.')
        c.argument('export', options_list=['--export'], action='store_true', help='Return the exported Swagger/OpenAPI definition.')

    for scope in [
            'connector-gateway connection create',
            'connector-gateway connection show',
            'connector-gateway connection update',
            'connector-gateway connection delete',
            'connector-gateway connection list-consent-links',
            'connector-gateway connection authorize']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type)

    for scope in ['connector-gateway connection create', 'connector-gateway connection update']:
        with self.argument_context(scope) as c:
            c.argument('available_connector', options_list=['--available-connector'], help='Name of the available connector to instantiate.')
            c.argument('body', body_type)

    with self.argument_context('connector-gateway connection list-consent-links') as c:
        c.argument('redirect_url', options_list=['--redirect-url'], default='https://portal.azure.com',
                   help='OAuth redirect URL used when requesting consent links.')

    with self.argument_context('connector-gateway connection authorize') as c:
        c.argument('redirect_url', options_list=['--redirect-url'], default='https://portal.azure.com',
                   help='OAuth redirect URL used when requesting consent links.')
        c.argument('no_browser', options_list=['--no-browser'], action='store_true', help='Print the authorization URL without opening a browser.')

    for scope in [
            'connector-gateway connection access-policy create',
            'connector-gateway connection access-policy show',
            'connector-gateway connection access-policy update',
            'connector-gateway connection access-policy delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type)

    with self.argument_context('connector-gateway connection access-policy') as c:
        c.argument('connection_name', options_list=['--connection-name'], required=True, help='Connection name.')

    for scope in [
            'connector-gateway connection access-policy create',
            'connector-gateway connection access-policy update']:
        with self.argument_context(scope) as c:
            c.argument('body', body_type)
            c.argument('object_id', options_list=['--object-id'], help='Azure AD object ID to grant access.')
            c.argument('tenant_id', options_list=['--tenant-id'], help='Azure AD tenant ID for the principal.')
            c.argument('principal_type', options_list=['--principal-type'], default='ActiveDirectory', help='Principal type.')

    for scope in [
            'connector-gateway mcp-server-config create',
            'connector-gateway mcp-server-config show',
            'connector-gateway mcp-server-config update',
            'connector-gateway mcp-server-config delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type)

    for scope in [
            'connector-gateway mcp-server-config create',
            'connector-gateway mcp-server-config update']:
        with self.argument_context(scope) as c:
            c.argument('body', body_type)

    for scope in [
            'connector-gateway trigger-config create',
            'connector-gateway trigger-config show',
            'connector-gateway trigger-config update',
            'connector-gateway trigger-config delete']:
        with self.argument_context(scope) as c:
            c.argument('name', name_type)

    for scope in [
            'connector-gateway trigger-config create',
            'connector-gateway trigger-config update']:
        with self.argument_context(scope) as c:
            c.argument('body', body_type)
            c.argument('available_connector', options_list=['--available-connector'], help='Name of the available connector for the trigger.')
            c.argument('connection_name', options_list=['--connection-name'], help='Connection name used by the trigger.')
            c.argument('operation_name', options_list=['--operation-name'], help='Connector trigger operation name.')
            c.argument('callback_url', options_list=['--callback-url'], help='Callback URL invoked by the Connector Gateway.')
            c.argument('http_method', options_list=['--http-method'], help='HTTP method used for the callback. Defaults to Post on create.')
            c.argument('parameter', options_list=['--parameter'], nargs='*', help='Trigger parameter in NAME=VALUE format. Repeat or separate with spaces.')
            c.argument('description', options_list=['--description'], help='Trigger config description.')
            c.argument('trigger_type', options_list=['--type'], help='Trigger config type.')
