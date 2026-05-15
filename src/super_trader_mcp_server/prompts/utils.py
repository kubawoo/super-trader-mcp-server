from super_trader_mcp_server.mcpserver import mcp


@mcp.prompt
def ask_current_date(fmt: str = "%Y-%m-%d") -> str:
    """Generates a user message asking for the current date in a specific format."""
    return f"What is the current date in {fmt} format?"


@mcp.prompt
def ask_current_time(fmt: str = "%H:%M") -> str:
    """Generates a user message asking for the current time in a specific format."""
    return f"What is the current time in {fmt} format?"
