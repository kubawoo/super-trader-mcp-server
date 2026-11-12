from datetime import datetime

from super_trader.mcpserver import mcp


@mcp.tool
async def get_current_date(fmt: str = "%Y-%m-%d") -> str:
    """Get the current local date with optional custom formatting.
    
    Args:
        fmt: strftime format string (default: '%Y-%m-%d' for ISO format).
             Common formats: '%Y-%m-%d', '%m/%d/%Y', '%d-%b-%Y', '%A, %B %d, %Y'.
    
    Returns:
        Current date as a formatted string using the system's local timezone.
    """
    return datetime.now().strftime(fmt)


@mcp.tool
async def get_current_time(fmt: str = "%H:%M") -> str:
    """Get the current local time with optional custom formatting.
    
    Args:
        fmt: strftime format string (default: '%H:%M' for 24-hour format).
             Common formats: '%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M:%S %p'.
    
    Returns:
        Current time as a formatted string using the system's local timezone.
    """
    return datetime.now().strftime(fmt)
