from dotenv import load_dotenv

load_dotenv()

# -- server singleton imported once from busybar_mcp._server --
from busybar_mcp._server import server  # noqa: E402

# -- register all tool modules (side-effect: @server.tool decorators fire) --
import busybar_mcp.account   # noqa: F401, E402
import busybar_mcp.busy      # noqa: F401, E402
import busybar_mcp.ble       # noqa: F401, E402
import busybar_mcp.input     # noqa: F401, E402
import busybar_mcp.settings  # noqa: F401, E402
import busybar_mcp.smarthome # noqa: F401, E402
import busybar_mcp.storage   # noqa: F401, E402
import busybar_mcp.system    # noqa: F401, E402
import busybar_mcp.time      # noqa: F401, E402
import busybar_mcp.updater   # noqa: F401, E402
import busybar_mcp.wifi      # noqa: F401, E402

if __name__ == "__main__":
    server.run()
