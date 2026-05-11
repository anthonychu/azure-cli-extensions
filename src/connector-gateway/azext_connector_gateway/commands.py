from azext_connector_gateway._transformers import (
    transform_access_policy_table,
    transform_available_connector_table,
    transform_connection_table,
    transform_gateway_table,
    transform_mcp_server_config_table,
    transform_trigger_config_table,
)


def load_command_table(self, _):
    with self.command_group('connector-gateway') as g:
        g.custom_command('create', 'create_gateway', table_transformer=transform_gateway_table)
        g.custom_command('list', 'list_gateways', table_transformer=transform_gateway_table)
        g.custom_show_command('show', 'show_gateway', table_transformer=transform_gateway_table)
        g.custom_command('update', 'update_gateway', table_transformer=transform_gateway_table)
        g.custom_command('delete', 'delete_gateway', confirmation=True)

    with self.command_group('connector-gateway available-connector') as g:
        g.custom_command('list', 'list_available_connectors', table_transformer=transform_available_connector_table)
        g.custom_show_command('show', 'show_available_connector', table_transformer=transform_available_connector_table)

    with self.command_group('connector-gateway connection') as g:
        g.custom_command('create', 'create_connection', table_transformer=transform_connection_table)
        g.custom_command('list', 'list_connections', table_transformer=transform_connection_table)
        g.custom_show_command('show', 'show_connection', table_transformer=transform_connection_table)
        g.custom_command('update', 'update_connection', table_transformer=transform_connection_table)
        g.custom_command('delete', 'delete_connection', confirmation=True)
        g.custom_command('list-consent-links', 'list_connection_consent_links')
        g.custom_command('authorize', 'authorize_connection')

    with self.command_group('connector-gateway connection access-policy') as g:
        g.custom_command('create', 'create_access_policy', table_transformer=transform_access_policy_table)
        g.custom_command('list', 'list_access_policies', table_transformer=transform_access_policy_table)
        g.custom_show_command('show', 'show_access_policy', table_transformer=transform_access_policy_table)
        g.custom_command('update', 'update_access_policy', table_transformer=transform_access_policy_table)
        g.custom_command('delete', 'delete_access_policy', confirmation=True)

    with self.command_group('connector-gateway mcp-server-config') as g:
        g.custom_command('create', 'create_mcp_server_config', table_transformer=transform_mcp_server_config_table)
        g.custom_command('list', 'list_mcp_server_configs', table_transformer=transform_mcp_server_config_table)
        g.custom_show_command('show', 'show_mcp_server_config', table_transformer=transform_mcp_server_config_table)
        g.custom_command('update', 'update_mcp_server_config', table_transformer=transform_mcp_server_config_table)
        g.custom_command('delete', 'delete_mcp_server_config', confirmation=True)

    with self.command_group('connector-gateway trigger-config') as g:
        g.custom_command('create', 'create_trigger_config', table_transformer=transform_trigger_config_table)
        g.custom_command('list', 'list_trigger_configs', table_transformer=transform_trigger_config_table)
        g.custom_show_command('show', 'show_trigger_config', table_transformer=transform_trigger_config_table)
        g.custom_command('update', 'update_trigger_config', table_transformer=transform_trigger_config_table)
        g.custom_command('delete', 'delete_trigger_config', confirmation=True)