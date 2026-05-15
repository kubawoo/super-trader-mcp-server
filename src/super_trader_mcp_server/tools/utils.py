from datetime import datetime

from super_trader_mcp_server.mcpserver import mcp


@mcp.tool
async def get_current_date(fmt: str = "%Y-%m-%d") -> str:
    """Returns the current date"""
    return datetime.now().strftime(fmt)


@mcp.tool
async def get_current_time(fmt: str = "%H:%M") -> str:
    """Returns the current time"""
    return datetime.now().strftime(fmt)
