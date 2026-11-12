from datetime import datetime
from typing import List

import yfinance as yf

from super_trader.mcpserver import mcp
from pandas import isna

from super_trader.models import (
    ETFEquityStatsModel,
    TopHoldingModel,
    StockInfoModel,
    NewsItemModel,
    DividendDetailsModel,
    DividendHistoryItemModel,
)


@mcp.tool
async def get_current_stock_price(ticker: str) -> float:
    """Get the current regular market price for a stock or ETF from Yahoo Finance.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'SPY', 'TSLA').
    
    Returns:
        Current regular market price as a float. Returns the 'regularMarketPrice'
        field from Yahoo Finance, which reflects the last traded price during
        regular market hours or the previous close if markets are closed.
    """
    stk = yf.Ticker(ticker)
    return stk.info["regularMarketPrice"]


@mcp.tool
async def get_top_holdings(ticker: str) -> List[TopHoldingModel]:
    """Get the top portfolio holdings for an ETF or mutual fund from Yahoo Finance.
    
    Args:
        ticker: ETF or fund ticker symbol (e.g., 'SPY', 'VTI', 'ARKK').
    
    Returns:
        List of TopHoldingModel objects containing:
        - ticker: Holding's ticker symbol
        - name: Holding's full name
        - pct: Percentage weight in the portfolio (0-100)
    
    Note: Only works for ETFs and funds that report holdings data.
    Individual stocks will return an empty list.
    """
    etf = yf.Ticker(ticker)
    holdings = etf.funds_data.top_holdings
    return [
        TopHoldingModel(ticker=row.Index, name=row[1], pct=row[2])
        for row in holdings.itertuples()
    ]


@mcp.tool
async def get_etf_equity_stats(ticker: str) -> ETFEquityStatsModel:
    """Get equity valuation and fundamental statistics for an ETF's underlying holdings.
    
    Args:
        ticker: ETF ticker symbol (e.g., 'SPY', 'QQQ', 'IWM').
    
    Returns:
        ETFEquityStatsModel with valuation metrics for both the ETF and its
        category average, including:
        - Price/Earnings (P/E) ratio
        - Price/Book (P/B) ratio
        - Price/Sales (P/S) ratio
        - Price/Cashflow ratio
        - Median market capitalization of holdings
        - 3-year earnings growth rate
    
    Provides side-by-side comparison of the ETF's metrics vs. its Morningstar
    category average for relative valuation analysis.
    """
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
        category_average_three_year_earnings_growth=v(
            "Category Average", "3 Year Earnings Growth"
        ),
    )


@mcp.tool
async def get_company_info(ticker: str) -> StockInfoModel:
    """Get comprehensive company profile and key financial metrics from Yahoo Finance.
    
    Args:
        ticker: Stock or ETF ticker symbol (e.g., 'AAPL', 'MSFT', 'SPY').
    
    Returns:
        StockInfoModel with:
        - Company identification: display_name, sector, industry, country, website
        - Market data: market_cap, currency, beta, 52-week high/low
        - Valuation: trailing_pe, forward_pe, target_mean_price
        - Financials: total_revenue, employees
        - Dividends: dividend_rate, dividend_yield
        - Business description: long_business_summary
    
    All data sourced from Yahoo Finance's quoteSummary API.
    """
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


@mcp.tool
async def get_company_news(ticker: str) -> List[NewsItemModel]:
    """Get the latest news articles for a company from Yahoo Finance.
    
    Args:
        ticker: Stock or ETF ticker symbol (e.g., 'AAPL', 'TSLA', 'SPY').
    
    Returns:
        List of NewsItemModel objects with:
        - title: Article headline
        - publisher: News source name
        - link: Canonical URL to full article
        - publish_time: Unix timestamp of publication
        - type: Content type (e.g., 'STORY', 'VIDEO')
        - thumbnail_url: Article thumbnail image URL if available
    
    Returns up to ~20 most recent news items. Coverage varies by ticker.
    """
    stk = yf.Ticker(ticker)
    news = stk.news
    result = []
    for item in news:
        content = item.get("content", {})
        pub_date_str = content.get("pubDate", "")
        publish_time = 0
        if pub_date_str:
            try:
                dt = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                publish_time = int(dt.timestamp())
            except ValueError:
                pass
        result.append(
            NewsItemModel(
                title=content.get("title", ""),
                publisher=content.get("provider", {}).get("displayName", ""),
                link=content.get("canonicalUrl", {}).get("url", ""),
                publish_time=publish_time,
                type=content.get("contentType", ""),
                thumbnail_url=content.get("thumbnail", {}).get("resolutions", [{}])[0].get("url") if content.get("thumbnail") else None,
            )
        )
    return result


@mcp.tool
async def get_dividend_details(ticker: str) -> DividendDetailsModel:
    """Get comprehensive dividend information for a stock or ETF.
    
    Args:
        ticker: Stock or ETF ticker symbol (e.g., 'AAPL', 'JNJ', 'SCHD').
    
    Returns:
        DividendDetailsModel with:
        - Current metrics: dividend_rate, dividend_yield
        - Trailing annual: trailing_annual_dividend_rate, trailing_annual_dividend_yield
        - Key dates: ex_dividend_date, dividend_date (formatted YYYY-MM-DD)
        - Quality metrics: payout_ratio, five_year_avg_dividend_yield
        - Full history: List of DividendHistoryItemModel (date, amount) for all
          historical dividend payments from Yahoo Finance
    
    Useful for dividend growth analysis, yield comparison, and payment tracking.
    """
    stk = yf.Ticker(ticker)
    info = stk.info
    dividends = stk.dividends
    
    def fmt_ts(ts: int | float | None) -> str | None:
        if ts is None:
            return None
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    
    history = []
    for date, amount in dividends.items():
        dt = date.to_pydatetime()
        history.append(DividendHistoryItemModel(date=dt.strftime("%Y-%m-%d"), amount=float(amount)))
    
    return DividendDetailsModel(
        ticker=ticker,
        dividend_rate=info.get("dividendRate"),
        dividend_yield=info.get("dividendYield"),
        trailing_annual_dividend_rate=info.get("trailingAnnualDividendRate"),
        trailing_annual_dividend_yield=info.get("trailingAnnualDividendYield"),
        ex_dividend_date=fmt_ts(info.get("exDividendDate")),
        dividend_date=fmt_ts(info.get("dividendDate")),
        payout_ratio=info.get("payoutRatio"),
        five_year_avg_dividend_yield=info.get("fiveYearAvgDividendYield"),
        history=history,
    )
