from azure.cli.core import AzCommandsLoader

from azext_connector_namespace._help import helps  # pylint: disable=unused-import


class ConnectorNamespaceCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        connector_namespace_custom = CliCommandType(
            operations_tmpl='azext_connector_namespace.custom#{}')
        super(ConnectorNamespaceCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=connector_namespace_custom)

    def load_command_table(self, args):
        from azext_connector_namespace.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_connector_namespace._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ConnectorNamespaceCommandsLoader