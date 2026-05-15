from super_trader_mcp_server.mcpserver import mcp


@mcp.prompt
def ask_about_stock_price(company: str) -> str:
    """Generates a user message asking for a current price of a stock."""
    return f"What is the current price of '{company}'?"


@mcp.prompt
def ask_about_top_holdings(fund: str) -> str:
    """Generates a user message asking for top holdings of an ETF."""
    return f"What are the top holdings of '{fund}'?"


@mcp.prompt
def ask_about_etf_equity_stats(ticker: str) -> str:
    """Generates a user message asking for equity valuation stats of an ETF."""
    return f"What are the equity valuation stats (P/E, P/B, etc.) for '{ticker}'?"


@mcp.prompt
def ask_about_company_info(ticker: str) -> str:
    """Generates a user message asking for company information."""
    return f"What is the company info for '{ticker}'?"
