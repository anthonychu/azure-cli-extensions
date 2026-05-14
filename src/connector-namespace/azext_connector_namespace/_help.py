from knack.help_files import helps  # pylint: disable=unused-import


helps['connector-namespace'] = """
type: group
short-summary: Manage Connector Namespace resources.
long-summary: |
  Connector Namespaces host connector definitions, authenticated connector connections, trigger configs, MCP server configs, and connection access policies.
  Typical workflow: create or show a namespace, list available connectors, create a connection from an available connector, authorize the connection, inspect actions or triggers, invoke actions, and create trigger configs from trigger operations.
examples:
  - name: Discover and use a connector from a namespace.
    text: |
      az connector-namespace available-connector list -g MyResourceGroup --namespace-name MyNamespace -o table
      az connector-namespace connection create -g MyResourceGroup --namespace-name MyNamespace -n office365-test --available-connector office365
      az connector-namespace connection authorize -g MyResourceGroup --namespace-name MyNamespace -n office365-test
      az connector-namespace connection operation list -g MyResourceGroup --namespace-name MyNamespace -n office365-test --operation-type action -o table
      az connector-namespace connection operation list -g MyResourceGroup --namespace-name MyNamespace -n office365-test --operation-type trigger -o table
"""


helps['connector-namespace create'] = """
type: command
short-summary: Create a Connector Namespace.
long-summary: Create the parent resource that contains available connectors, connections, trigger configs, MCP server configs, and access policies.
examples:
  - name: Create a Connector Namespace with a system-assigned identity.
    text: az connector-namespace create -g MyResourceGroup -n MyNamespace -l westcentralus
"""

helps['connector-namespace list'] = """
type: command
short-summary: List Connector Namespaces.
long-summary: Use this first when you need the namespace name to pass to child commands with --namespace-name.
examples:
  - name: List Connector Namespaces in a resource group.
    text: az connector-namespace list -g MyResourceGroup -o table
"""

helps['connector-namespace show'] = """
type: command
short-summary: Show details for a Connector Namespace.
long-summary: Show namespace location, identity, provisioning state, tags, and service-provided properties.
examples:
  - name: Show a Connector Namespace.
    text: az connector-namespace show -g MyResourceGroup -n MyNamespace
"""

helps['connector-namespace update'] = """
type: command
short-summary: Update a Connector Namespace.
long-summary: Update mutable namespace properties such as tags and managed identity type.
examples:
  - name: Update Connector Namespace tags.
    text: az connector-namespace update -g MyResourceGroup -n MyNamespace --tags env=test owner=team
"""

helps['connector-namespace delete'] = """
type: command
short-summary: Delete a Connector Namespace.
long-summary: Delete the namespace and its child resources.
examples:
  - name: Delete a Connector Namespace.
    text: az connector-namespace delete -g MyResourceGroup -n MyNamespace
"""

helps['connector-namespace available-connector'] = """
type: group
short-summary: List and inspect available connectors for a Connector Namespace.
long-summary: |
  Available connectors are managed API definitions, such as Microsoft 365 (connector name office365) or OneDrive for Business (connector name onedriveforbusiness), that can be used to create authenticated connection instances.
  Start here when you do not know which connector names can be used with connection create or trigger-config create.
"""

helps['connector-namespace available-connector list'] = """
type: command
short-summary: List available connectors for a Connector Namespace.
long-summary: Use the Name column as --available-connector when creating a connection or trigger config.
examples:
  - name: List available connectors.
    text: az connector-namespace available-connector list -g MyResourceGroup --namespace-name MyNamespace -o table
"""

helps['connector-namespace available-connector show'] = """
type: command
short-summary: Show an available connector definition.
long-summary: Use --export to retrieve the connector Swagger/OpenAPI definition, including operation metadata such as x-ms-trigger and x-ms-trigger-hint.
examples:
  - name: Show the Microsoft 365 available connector.
    text: az connector-namespace available-connector show -g MyResourceGroup --namespace-name MyNamespace -n office365
  - name: Export the connector Swagger/OpenAPI definition.
    text: az connector-namespace available-connector show -g MyResourceGroup --namespace-name MyNamespace -n office365 --export
"""

helps['connector-namespace connection'] = """
type: group
short-summary: Manage Connector Namespace connections.
long-summary: |
  Connections are authenticated instances of available connectors. Create a connection from an available connector, authorize it if OAuth consent is needed, then inspect actions and triggers with connection operation commands.
"""

helps['connector-namespace connection create'] = """
type: command
short-summary: Create a Connector Namespace connection.
long-summary: Create a connection from an available connector name discovered with available-connector list. OAuth connectors usually require authorize after creation.
examples:
  - name: Create a Microsoft 365 connection from the office365 available connector.
    text: az connector-namespace connection create -g MyResourceGroup --namespace-name MyNamespace -n office365-test --available-connector office365
  - name: Create a connection from a JSON body.
    text: az connector-namespace connection create -g MyResourceGroup --namespace-name MyNamespace -n office365-test --body @connection.json
"""

helps['connector-namespace connection list'] = """
type: command
short-summary: List Connector Namespace connections.
long-summary: Use the connection Name with connection show, authorize, operation list/show, invoke, and access-policy commands.
examples:
  - name: List connections for a Connector Namespace.
    text: az connector-namespace connection list -g MyResourceGroup --namespace-name MyNamespace -o table
"""

helps['connector-namespace connection show'] = """
type: command
short-summary: Show details for a Connector Namespace connection.
long-summary: Show connection status, connector name, runtime URL metadata, and authentication-related properties returned by the service.
examples:
  - name: Show a Microsoft 365 connection.
    text: az connector-namespace connection show -g MyResourceGroup --namespace-name MyNamespace -n office365-test
"""

helps['connector-namespace connection update'] = """
type: command
short-summary: Update a Connector Namespace connection.
long-summary: Update connection properties from a JSON body, or update the available connector reference when supported by the service.
examples:
  - name: Update a connection from a JSON body.
    text: az connector-namespace connection update -g MyResourceGroup --namespace-name MyNamespace -n office365-test --body @connection.json
"""

helps['connector-namespace connection delete'] = """
type: command
short-summary: Delete a Connector Namespace connection.
long-summary: Delete an authenticated connection instance. Trigger configs and access policies that depend on the connection may also need cleanup.
examples:
  - name: Delete a connection.
    text: az connector-namespace connection delete -g MyResourceGroup --namespace-name MyNamespace -n office365-test
"""

helps['connector-namespace connection list-consent-links'] = """
type: command
short-summary: List OAuth consent links for a Connector Namespace connection.
long-summary: Retrieve consent links when you want to handle browser opening yourself or inspect the login URL returned by the service.
examples:
  - name: Retrieve consent links for a connection.
    text: az connector-namespace connection list-consent-links -g MyResourceGroup --namespace-name MyNamespace -n office365-test
"""

helps['connector-namespace connection authorize'] = """
type: command
short-summary: Open the OAuth consent page for a Connector Namespace connection.
long-summary: Run this after creating a connection when the connector requires user authorization. After authorization, use operation list/show to discover actions and triggers.
examples:
  - name: Open the consent page for a connection.
    text: az connector-namespace connection authorize -g MyResourceGroup --namespace-name MyNamespace -n office365-test
  - name: Print the consent page without opening a browser.
    text: az connector-namespace connection authorize -g MyResourceGroup --namespace-name MyNamespace -n office365-test --no-browser
"""

helps['connector-namespace connection invoke'] = """
type: command
short-summary: Invoke a Connector Namespace connection runtime action.
long-summary: |
  Invokes an authenticated connection runtime operation. Use connection operation list --operation-type action and connection operation show to find Swagger operation IDs, required parameters, and request body examples before invoking mutating actions.
examples:
  - name: Send a Microsoft 365 email using the SendEmailV2 action.
    text: az connector-namespace connection invoke -g MyResourceGroup --namespace-name MyNamespace -n office365-test --operation-id SendEmailV2 --body @mail.json
  - name: Invoke a runtime path directly.
    text: az connector-namespace connection invoke -g MyResourceGroup --namespace-name MyNamespace -n office365-test --path /v2/Mail --method post --body @mail.json
  - name: Grant access if runtime invocation fails with an authorization error.
    text: az connector-namespace connection access-policy create -g MyResourceGroup --namespace-name MyNamespace --connection-name office365-test -n signed-in-user --object-id 00000000-0000-0000-0000-000000000000 --tenant-id 00000000-0000-0000-0000-000000000000
"""

helps['connector-namespace connection operation'] = """
type: group
short-summary: List and inspect actions and triggers for a Connector Namespace connection.
long-summary: |
  Operations come from the connector Swagger for the connection. Use --operation-type action to find operations for connection invoke, or --operation-type trigger to find operations for trigger-config create.
"""

helps['connector-namespace connection operation list'] = """
type: command
short-summary: List actions and triggers for a Connector Namespace connection.
long-summary: |
  Use --operation-type action to list invokable runtime actions. Use --operation-type trigger to list trigger operations that can back trigger configs. Trigger rows include triggerType and triggerHint when the connector provides them.
examples:
  - name: List all Microsoft 365 connection operations.
    text: az connector-namespace connection operation list -g MyResourceGroup --namespace-name MyNamespace -n office365-test -o table
  - name: List only invokable actions.
    text: az connector-namespace connection operation list -g MyResourceGroup --namespace-name MyNamespace -n office365-test --operation-type action -o table
  - name: List only trigger operations.
    text: az connector-namespace connection operation list -g MyResourceGroup --namespace-name MyNamespace -n office365-test --operation-type trigger -o table
"""

helps['connector-namespace connection operation show'] = """
type: command
short-summary: Show an action or trigger operation for a Connector Namespace connection.
long-summary: Includes operation type, trigger metadata, method, runtime path, parameters, raw body schema, resolved body schema, and a generated request body example when a body schema is available.
examples:
  - name: Show the Microsoft 365 send email action.
    text: az connector-namespace connection operation show -g MyResourceGroup --namespace-name MyNamespace -n office365-test --operation-id SendEmailV2
  - name: Show a generated request body example for an action.
    text: az connector-namespace connection operation show -g MyResourceGroup --namespace-name MyNamespace -n office365-test --operation-id SendEmailV2 --query requestBodyExample
  - name: Show trigger metadata and test hint.
    text: az connector-namespace connection operation show -g MyResourceGroup --namespace-name MyNamespace -n office365-test --operation-id OnFlaggedEmailV4 --query "{operationType:operationType,triggerType:triggerType,triggerHint:triggerHint}"
"""

helps['connector-namespace connection access-policy'] = """
type: group
short-summary: Manage access policies for Connector Namespace connections.
long-summary: Access policies grant Azure AD principals permission to call a connection runtime URL. Add one when a user, managed identity, or app needs to invoke connection actions.
"""

helps['connector-namespace connection access-policy create'] = """
type: command
short-summary: Create or update a connection access policy.
long-summary: Grant an Azure AD principal access to a connection runtime URL. This is commonly needed before invoking actions from an app or managed identity.
examples:
  - name: Grant an Azure AD identity access to a connection runtime URL.
    text: az connector-namespace connection access-policy create -g MyResourceGroup --namespace-name MyNamespace --connection-name office365-test -n functionapp-msi --object-id 00000000-0000-0000-0000-000000000000 --tenant-id 00000000-0000-0000-0000-000000000000
"""

helps['connector-namespace connection access-policy list'] = """
type: command
short-summary: List access policies for a Connector Namespace connection.
long-summary: List principals that have been granted access to a connection runtime URL.
examples:
  - name: List access policies for a connection.
    text: az connector-namespace connection access-policy list -g MyResourceGroup --namespace-name MyNamespace --connection-name office365-test -o table
"""

helps['connector-namespace connection access-policy show'] = """
type: command
short-summary: Show details for a connection access policy.
long-summary: Inspect the principal and provisioning state for one connection access policy.
examples:
  - name: Show a connection access policy.
    text: az connector-namespace connection access-policy show -g MyResourceGroup --namespace-name MyNamespace --connection-name office365-test -n functionapp-msi
"""

helps['connector-namespace connection access-policy update'] = """
type: command
short-summary: Update a connection access policy.
long-summary: Update a connection access policy from explicit principal values or a JSON body.
examples:
  - name: Update a connection access policy from a JSON body.
    text: az connector-namespace connection access-policy update -g MyResourceGroup --namespace-name MyNamespace --connection-name office365-test -n functionapp-msi --body @access-policy.json
"""

helps['connector-namespace connection access-policy delete'] = """
type: command
short-summary: Delete a connection access policy.
long-summary: Remove a principal's access to a connection runtime URL.
examples:
  - name: Delete a connection access policy.
    text: az connector-namespace connection access-policy delete -g MyResourceGroup --namespace-name MyNamespace --connection-name office365-test -n functionapp-msi
"""

helps['connector-namespace mcp-server-config'] = """
type: group
short-summary: Manage Connector Namespace MCP server configs.
long-summary: MCP server configs are child resources of a namespace. Use these commands when exposing connector-backed capabilities through an MCP endpoint.
"""

helps['connector-namespace mcp-server-config create'] = """
type: command
short-summary: Create an MCP server config from a JSON body.
long-summary: Create an MCP server config child resource. Provide the service-specific MCP config JSON with --body.
examples:
  - name: Create an MCP server config.
    text: az connector-namespace mcp-server-config create -g MyResourceGroup --namespace-name MyNamespace -n MyMcpConfig --body @mcp-config.json
"""

helps['connector-namespace mcp-server-config list'] = """
type: command
short-summary: List MCP server configs for a Connector Namespace.
long-summary: List MCP server config child resources in a namespace.
examples:
  - name: List MCP server configs.
    text: az connector-namespace mcp-server-config list -g MyResourceGroup --namespace-name MyNamespace -o table
"""

helps['connector-namespace mcp-server-config show'] = """
type: command
short-summary: Show details for an MCP server config.
long-summary: Inspect one MCP server config and its endpoint/provisioning state.
examples:
  - name: Show an MCP server config.
    text: az connector-namespace mcp-server-config show -g MyResourceGroup --namespace-name MyNamespace -n MyMcpConfig
"""

helps['connector-namespace mcp-server-config update'] = """
type: command
short-summary: Update an MCP server config from a JSON body.
long-summary: Replace or update an MCP server config using the service-specific MCP config JSON.
examples:
  - name: Update an MCP server config.
    text: az connector-namespace mcp-server-config update -g MyResourceGroup --namespace-name MyNamespace -n MyMcpConfig --body @mcp-config.json
"""

helps['connector-namespace mcp-server-config delete'] = """
type: command
short-summary: Delete an MCP server config.
long-summary: Delete an MCP server config child resource.
examples:
  - name: Delete an MCP server config.
    text: az connector-namespace mcp-server-config delete -g MyResourceGroup --namespace-name MyNamespace -n MyMcpConfig
"""

helps['connector-namespace trigger-config'] = """
type: group
short-summary: Manage Connector Namespace trigger configs.
long-summary: |
  Trigger configs connect a connector trigger operation to a callback URL. Discover trigger operations with connection operation list --operation-type trigger, inspect parameters and trigger hints with operation show, then create a trigger config with the selected operation name.
"""

helps['connector-namespace trigger-config run'] = """
type: group
short-summary: List run history for Connector Namespace trigger configs.
long-summary: Trigger config runs are the execution history for a trigger config. Use this after creating and enabling a trigger config to inspect recent trigger deliveries.
"""

helps['connector-namespace trigger-config run list'] = """
type: command
short-summary: List run history for a trigger config.
long-summary: List recent runs from the trigger config runs collection. Use --top to limit the number of returned runs.
examples:
  - name: List recent runs for a trigger config.
    text: az connector-namespace trigger-config run list -g MyResourceGroup --namespace-name MyNamespace --trigger-config-name on-flagged-email -o table
  - name: List the latest 50 runs for a trigger config.
    text: az connector-namespace trigger-config run list -g MyResourceGroup --namespace-name MyNamespace --trigger-config-name on-flagged-email --top 50
"""

helps['connector-namespace trigger-config create'] = """
type: command
short-summary: Create a trigger config.
long-summary: |
  Create a trigger config for a trigger operation discovered with connection operation list --operation-type trigger. The operation name should be the trigger operationId, and parameters should match the operation show output.
examples:
  - name: Discover Microsoft 365 triggers before creating a trigger config.
    text: az connector-namespace connection operation list -g MyResourceGroup --namespace-name MyNamespace -n office365-test --operation-type trigger -o table
  - name: Inspect the trigger parameters and hint.
    text: az connector-namespace connection operation show -g MyResourceGroup --namespace-name MyNamespace -n office365-test --operation-id OnFlaggedEmailV4
  - name: Create a trigger config with typed parameters.
    text: az connector-namespace trigger-config create -g MyResourceGroup --namespace-name MyNamespace -n on-flagged-email --available-connector office365 --connection-name office365-test --operation-name OnFlaggedEmailV4 --callback-url https://example.com/runtime/webhooks/connector
  - name: Create a trigger config from a JSON body.
    text: az connector-namespace trigger-config create -g MyResourceGroup --namespace-name MyNamespace -n on-flagged-email --body @trigger-config.json
"""

helps['connector-namespace trigger-config list'] = """
type: command
short-summary: List trigger configs for a Connector Namespace.
long-summary: List trigger config child resources and use the Name column with show, update, or delete.
examples:
  - name: List trigger configs.
    text: az connector-namespace trigger-config list -g MyResourceGroup --namespace-name MyNamespace -o table
"""

helps['connector-namespace trigger-config show'] = """
type: command
short-summary: Show details for a trigger config.
long-summary: Inspect the connector, connection, operation name, callback settings, parameters, and provisioning state for one trigger config.
examples:
  - name: Show a trigger config.
    text: az connector-namespace trigger-config show -g MyResourceGroup --namespace-name MyNamespace -n on-flagged-email
"""

helps['connector-namespace trigger-config update'] = """
type: command
short-summary: Update a trigger config.
long-summary: Update a trigger config from typed arguments or a JSON body. Use operation show if you need to confirm expected trigger parameters.
examples:
  - name: Update a trigger config from a JSON body.
    text: az connector-namespace trigger-config update -g MyResourceGroup --namespace-name MyNamespace -n on-flagged-email --body @trigger-config.json
"""

helps['connector-namespace trigger-config delete'] = """
type: command
short-summary: Delete a trigger config.
long-summary: Delete a trigger config child resource.
examples:
  - name: Delete a trigger config.
    text: az connector-namespace trigger-config delete -g MyResourceGroup --namespace-name MyNamespace -n on-flagged-email
"""