from busybar_python_sdk import StorageApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _serialize, _wrap_tool_error


@server.tool(name="list_storage_files")
def list_storage_files(path: str = "/"):
    """List files and directories stored on the Busy Bar device at a given path.

    This tool calls `StorageApi.list_storage_files(path)` to enumerate the directory
    contents on the device's internal storage for the specified path.

    Args:
        path: The directory path to list (e.g., "/", "/photos"). Defaults to "/".

    Returns a StorageList object containing:
        - A list of StorageListElement objects, each with:
            - type (str): File type — "file" or "dir"
            - name (str): Name of the file or directory

    Use case:
        Browse device storage to find files before uploading, downloading, or managing
        media assets for display on the Busy Bar unit.
    """
    try:
        api = _make_api(StorageApi)
        result = api.list_storage_files(path=path)
        return CallToolResult(content=[{"type": "text", "text": str(_serialize(result))}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to list storage files at {path!r}: {e}")


@server.tool(name="get_storage_status")
def get_storage_status():
    """Retrieve storage capacity information from the Busy Bar device.

    This tool queries GET /api/storage/status via `StorageApi.get_storage_status()`
    to learn current flash storage usage and available space.

    Returns a StorageStatus object containing:
        - used_bytes (int): Bytes currently used on the device storage
        - free_bytes (int): Bytes available for writing
        - total_bytes (int): Total capacity of the storage

    Use case:
        Check available storage before uploading files or media to confirm there is
        sufficient space, and monitor storage consumption over time.
    """
    try:
        api = _make_api(StorageApi)
        result = api.get_storage_status()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get storage status: {e}")
