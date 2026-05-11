from knack.help_files import helps  # pylint: disable=unused-import


helps['connector-gateway'] = """
type: group
short-summary: Manage Connector Gateway resources.
"""
 

helps['connector-gateway create'] = """
type: command
short-summary: Create a Connector Gateway.
examples:
  - name: Create a Connector Gateway with a system-assigned identity.
    text: az connector-gateway create -g MyResourceGroup -n MyGateway -l westcentralus
"""

helps['connector-gateway available-connector'] = """
type: group
short-summary: List and inspect available connectors for a Connector Gateway.
long-summary: Available connectors are the managed API definitions that can be used to create connection instances.
"""

helps['connector-gateway available-connector list'] = """
type: command
short-summary: List available connectors for a Connector Gateway.
examples:
  - name: List available connectors.
    text: az connector-gateway available-connector list -g MyResourceGroup --gateway-name MyGateway -o table
"""

helps['connector-gateway available-connector show'] = """
type: command
short-summary: Show an available connector.
examples:
  - name: Show the Office 365 available connector.
    text: az connector-gateway available-connector show -g MyResourceGroup --gateway-name MyGateway -n office365
  - name: Export the connector Swagger/OpenAPI definition.
    text: az connector-gateway available-connector show -g MyResourceGroup --gateway-name MyGateway -n office365 --export
"""

helps['connector-gateway connection'] = """
type: group
short-summary: Manage Connector Gateway connections.
long-summary: Connections are authenticated instances of available connectors.
"""

helps['connector-gateway connection create'] = """
type: command
short-summary: Create a Connector Gateway connection.
examples:
  - name: Create an Office 365 connection.
    text: az connector-gateway connection create -g MyResourceGroup --gateway-name MyGateway -n office365-test --available-connector office365
"""

helps['connector-gateway connection list-consent-links'] = """
type: command
short-summary: List OAuth consent links for a Connector Gateway connection.
examples:
  - name: Retrieve consent links for a connection.
    text: az connector-gateway connection list-consent-links -g MyResourceGroup --gateway-name MyGateway -n office365-test
"""

helps['connector-gateway connection authorize'] = """
type: command
short-summary: Open the OAuth consent page for a Connector Gateway connection.
examples:
  - name: Open the consent page for a connection.
    text: az connector-gateway connection authorize -g MyResourceGroup --gateway-name MyGateway -n office365-test
  - name: Print the consent page without opening a browser.
    text: az connector-gateway connection authorize -g MyResourceGroup --gateway-name MyGateway -n office365-test --no-browser
"""

helps['connector-gateway connection access-policy'] = """
type: group
short-summary: Manage access policies for Connector Gateway connections.
"""

helps['connector-gateway connection access-policy create'] = """
type: command
short-summary: Create or update a connection access policy.
examples:
  - name: Grant an Azure AD identity access to a connection runtime URL.
    text: az connector-gateway connection access-policy create -g MyResourceGroup --gateway-name MyGateway --connection-name office365-test -n functionapp-msi --object-id 00000000-0000-0000-0000-000000000000 --tenant-id 00000000-0000-0000-0000-000000000000
"""

helps['connector-gateway mcp-server-config'] = """
type: group
short-summary: Manage Connector Gateway MCP server configs.
"""

helps['connector-gateway mcp-server-config create'] = """
type: command
short-summary: Create an MCP server config from a JSON body.
examples:
  - name: Create an MCP server config.
    text: az connector-gateway mcp-server-config create -g MyResourceGroup --gateway-name MyGateway -n MyMcpConfig --body @mcp-config.json
"""

helps['connector-gateway trigger-config'] = """
type: group
short-summary: Manage Connector Gateway trigger configs.
"""

helps['connector-gateway trigger-config create'] = """
type: command
short-summary: Create a trigger config.
examples:
  - name: Create a trigger config with typed parameters.
    text: az connector-gateway trigger-config create -g MyResourceGroup --gateway-name MyGateway -n on-new-file --available-connector onedriveforbusiness --connection-name onedrive-test --operation-name OnNewFileV2 --callback-url https://example.com/runtime/webhooks/connector --parameter folderId=Documents includeSubfolders=false
  - name: Create a trigger config from a JSON body.
    text: az connector-gateway trigger-config create -g MyResourceGroup --gateway-name MyGateway -n on-new-file --body @trigger-config.json
"""