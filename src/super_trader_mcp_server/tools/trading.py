from typing import List

import yfinance as yf

from super_trader_mcp_server.mcpserver import mcp
from super_trader_mcp_server.models import TopHoldingModel


@mcp.tool
async def get_current_stock_price(ticker: str) -> float:
    """Returns the current stock price"""
    stk = yf.Ticker(ticker)
    return stk.info["regularMarketPrice"]


@mcp.tool
async def get_top_holdings(ticker: str) -> List[TopHoldingModel]:
    """Returns the top holdings for a ticker"""
    etf = yf.Ticker(ticker)
    holdings = etf.funds_data.top_holdings
    return [
        TopHoldingModel(ticker=row.Index, name=row[1], pct=row[2])
        for row in holdings.itertuples()
    ]
