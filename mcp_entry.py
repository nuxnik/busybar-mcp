from dotenv import load_dotenv
from busybar_mcp.server import register_tools, server

load_dotenv(override=False)
register_tools()
