"""Busy Bar MCP — package-level initialization.

Importing this package registers all MCP tools by importing every
module so that its ``@server.tool`` decorators fire.  No tool definitions
live at the package level; they are all in namespace-specific submodules.
"""

# Import the singleton server instance first (no circular deps)
from ._server import server, MCPServer

# Pull in every namespace module so that its @server.tool decorators
# execute during package initialisation.  The actual tool functions are
# not re-exported here; imports should use the submodule directly if needed.
import busybar_mcp.account  # noqa: F401
import busybar_mcp.busy     # noqa: F401
import busybar_mcp.ble      # noqa: F401
import busybar_mcp.settings # noqa: F401
import busybar_mcp.smarthome# noqa: F401
import busybar_mcp.storage  # noqa: F401
import busybar_mcp.system   # noqa: F401
import busybar_mcp.time     # noqa: F401
import busybar_mcp.updater  # noqa: F401
import busybar_mcp.wifi     # noqa: F401


def main() -> None:
    """Console entry point: load ``.env`` and run the MCP server over stdio."""
    from dotenv import load_dotenv

    load_dotenv()

    server.run(transport="stdio")
