from typing import List

import yfinance as yf

from super_trader_mcp_server.mcpserver import mcp
from pandas import isna

from super_trader_mcp_server.models import ETFEquityStatsModel, TopHoldingModel, StockInfoModel


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
async def get_etf_equity_stats(ticker: str) -> ETFEquityStatsModel:
    """Returns equity valuation metrics (P/E, P/B, etc.) for an ETF"""
    etf = yf.Ticker(ticker)
    stats = etf.funds_data.equity_holdings
    etf_col = ticker.upper()
    if etf_col not in stats.columns:
        etf_col = stats.columns[0]

    def v(col: str, key: str) -> float | None:
        val = stats.loc[key, col]
        return None if isna(val) else float(val)

    return ETFEquityStatsModel(
        ticker=ticker,
        price_earnings=v(etf_col, "Price/Earnings"),
        price_book=v(etf_col, "Price/Book"),
        price_sales=v(etf_col, "Price/Sales"),
        price_cashflow=v(etf_col, "Price/Cashflow"),
        median_market_cap=v(etf_col, "Median Market Cap"),
        three_year_earnings_growth=v(etf_col, "3 Year Earnings Growth"),
        category_average_price_earnings=v("Category Average", "Price/Earnings"),
        category_average_price_book=v("Category Average", "Price/Book"),
        category_average_price_sales=v("Category Average", "Price/Sales"),
        category_average_price_cashflow=v("Category Average", "Price/Cashflow"),
        category_average_median_market_cap=v("Category Average", "Median Market Cap"),
        category_average_three_year_earnings_growth=v("Category Average", "3 Year Earnings Growth"),
    )


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
        display_name=info.get("displayName", "N/A"),
        currency=info.get("currency", "N/A"),
        website=info.get("website", "N/A"),
        country=info.get("country", "N/A"),
        long_business_summary=info.get("longBusinessSummary", "N/A"),
        trailing_pe=info.get("trailingPE"),
        forward_pe=info.get("forwardPE"),
        total_revenue=info.get("totalRevenue"),
        dividend_rate=info.get("dividendRate"),
        fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
        fifty_two_week_low=info.get("fiftyTwoWeekLow"),
        beta=info.get("beta"),
        target_mean_price=info.get("targetMeanPrice"),
    )
