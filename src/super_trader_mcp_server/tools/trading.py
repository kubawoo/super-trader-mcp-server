from typing import List

import yfinance as yf

from super_trader_mcp_server.mcpserver import mcp


@mcp.tool
async def get_current_stock_price(ticker: str) -> float:
    """Returns the current stock price"""
    stk = yf.Ticker(ticker)
    return stk.info["regularMarketPrice"]


@mcp.tool
async def get_top_holdings(ticker: str) -> List[str]:
    """Returns the top holdings for a ticker"""
    etf = yf.Ticker(ticker)
    data = etf.funds_data
    # TODO: return full data frame
    names = data.top_holdings[["Name"]].values.tolist()
    return [x for xs in names for x in xs]
