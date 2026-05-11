from azure.cli.core import AzCommandsLoader

from azext_connector_gateway._help import helps  # pylint: disable=unused-import


class ConnectorGatewayCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        connector_gateway_custom = CliCommandType(
            operations_tmpl='azext_connector_gateway.custom#{}')
        super(ConnectorGatewayCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=connector_gateway_custom)

    def load_command_table(self, args):
        from azext_connector_gateway.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_connector_gateway._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ConnectorGatewayCommandsLoader