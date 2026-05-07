import yfinance as yf

from super_trader_mcp_server.mcpserver import mcp


@mcp.tool
async def get_current_stock_price(ticker: str) -> float:
    """Returns the current stock price"""
    stk = yf.Ticker(ticker)
    return stk.info["regularMarketPrice"]