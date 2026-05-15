from typing import List

import yfinance as yf

from super_trader_mcp_server.mcpserver import mcp
from super_trader_mcp_server.models import TopHoldingModel, StockInfoModel


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


@mcp.tool
async def get_company_info(ticker: str) -> StockInfoModel:
    """Returns basic company information like sector, industry, and market cap"""
    stk = yf.Ticker(ticker)
    info = stk.info
    return StockInfoModel(
        ticker=ticker,
        sector=info.get("sector", "N/A"),
        industry=info.get("industry", "N/A"),
        market_cap=info.get("marketCap", 0),
        employees=info.get("fullTimeEmployees", 0),
    )
