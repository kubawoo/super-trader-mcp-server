from datetime import datetime

from super_trader_mcp_server.mcpserver import mcp


@mcp.tool
async def get_current_date() -> str:
    """Returns the current date"""
    return datetime.now().strftime("%Y-%m-%d")


@mcp.tool
async def get_current_time() -> str:
    """Returns the current time"""
    return datetime.now().strftime("%H:%M")
