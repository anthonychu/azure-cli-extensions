from knack.help_files import helps  # pylint: disable=unused-import


helps['connectorgateway'] = """
type: group
short-summary: Manage Connector Gateway resources.
"""
 

helps['connectorgateway create'] = """
type: command
short-summary: Create a Connector Gateway.
examples:
  - name: Create a Connector Gateway with a system-assigned identity.
    text: az connectorgateway create -g MyResourceGroup -n MyGateway -l westcentralus
"""

helps['connectorgateway available-connector'] = """
type: group
short-summary: List and inspect available connectors for a Connector Gateway.
long-summary: Available connectors are the managed API definitions that can be used to create connection instances.
"""

helps['connectorgateway available-connector list'] = """
type: command
short-summary: List available connectors for a Connector Gateway.
examples:
  - name: List available connectors.
    text: az connectorgateway available-connector list -g MyResourceGroup --gateway-name MyGateway -o table
"""

helps['connectorgateway available-connector show'] = """
type: command
short-summary: Show an available connector.
examples:
  - name: Show the Office 365 available connector.
    text: az connectorgateway available-connector show -g MyResourceGroup --gateway-name MyGateway -n office365
  - name: Export the connector Swagger/OpenAPI definition.
    text: az connectorgateway available-connector show -g MyResourceGroup --gateway-name MyGateway -n office365 --export
"""

helps['connectorgateway connection'] = """
type: group
short-summary: Manage Connector Gateway connections.
long-summary: Connections are authenticated instances of available connectors.
"""

helps['connectorgateway connection create'] = """
type: command
short-summary: Create a Connector Gateway connection.
examples:
  - name: Create an Office 365 connection.
    text: az connectorgateway connection create -g MyResourceGroup --gateway-name MyGateway -n office365-test --available-connector office365
"""

helps['connectorgateway connection list-consent-links'] = """
type: command
short-summary: List OAuth consent links for a Connector Gateway connection.
examples:
  - name: Retrieve consent links for a connection.
    text: az connectorgateway connection list-consent-links -g MyResourceGroup --gateway-name MyGateway -n office365-test
"""

helps['connectorgateway connection authorize'] = """
type: command
short-summary: Open the OAuth consent page for a Connector Gateway connection.
examples:
  - name: Open the consent page for a connection.
    text: az connectorgateway connection authorize -g MyResourceGroup --gateway-name MyGateway -n office365-test
  - name: Print the consent page without opening a browser.
    text: az connectorgateway connection authorize -g MyResourceGroup --gateway-name MyGateway -n office365-test --no-browser
"""

helps['connectorgateway connection access-policy'] = """
type: group
short-summary: Manage access policies for Connector Gateway connections.
"""

helps['connectorgateway connection access-policy create'] = """
type: command
short-summary: Create or update a connection access policy.
examples:
  - name: Grant an Azure AD identity access to a connection runtime URL.
    text: az connectorgateway connection access-policy create -g MyResourceGroup --gateway-name MyGateway --connection-name office365-test -n functionapp-msi --object-id 00000000-0000-0000-0000-000000000000 --tenant-id 00000000-0000-0000-0000-000000000000
"""

helps['connectorgateway mcp-server-config'] = """
type: group
short-summary: Manage Connector Gateway MCP server configs.
"""

helps['connectorgateway mcp-server-config create'] = """
type: command
short-summary: Create an MCP server config from a JSON body.
examples:
  - name: Create an MCP server config.
    text: az connectorgateway mcp-server-config create -g MyResourceGroup --gateway-name MyGateway -n MyMcpConfig --body @mcp-config.json
"""

helps['connectorgateway trigger-config'] = """
type: group
short-summary: Manage Connector Gateway trigger configs.
"""

helps['connectorgateway trigger-config create'] = """
type: command
short-summary: Create a trigger config.
examples:
  - name: Create a trigger config with typed parameters.
    text: az connectorgateway trigger-config create -g MyResourceGroup --gateway-name MyGateway -n on-new-file --available-connector onedriveforbusiness --connection-name onedrive-test --operation-name OnNewFileV2 --callback-url https://example.com/runtime/webhooks/connector --parameter folderId=Documents includeSubfolders=false
  - name: Create a trigger config from a JSON body.
    text: az connectorgateway trigger-config create -g MyResourceGroup --gateway-name MyGateway -n on-new-file --body @trigger-config.json
"""