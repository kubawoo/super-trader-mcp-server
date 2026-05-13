from super_trader_mcp_server.mcpserver import mcp


@mcp.prompt
def ask_about_stock_price(company: str) -> str:
    """Generates a user message asking for a current price of a stock."""
    return f"What is the current price of '{company}'?"


@mcp.prompt
def ask_about_top_holdings(fund: str) -> str:
    """Generates a user message asking for top holdings of an ETFk."""
    return f"What are the top holdings of '{fund}'?"