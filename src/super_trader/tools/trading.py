from datetime import datetime
from typing import List

import yfinance as yf

from super_trader.mcpserver import mcp
from pandas import isna

from super_trader.models import (
    BetaModel,
    ETFEquityStatsModel,
    TopHoldingModel,
    StockInfoModel,
    StockPriceModel,
    NewsItemModel,
    DividendDetailsModel,
    DividendHistoryItemModel,
    IncomeStatementPeriodModel,
    BalanceSheetPeriodModel,
    CashFlowPeriodModel,
    FinancialStatementModel,
    IncomeStatementResponseModel,
    BalanceSheetResponseModel,
    CashFlowResponseModel,
    OptionContractModel,
    OptionChainModel,
    OptionExpirationsModel,
    ATMOptionsModel,
    EarningsDateModel,
    EarningsDatesResponseModel,
    EarningsHistoryItemModel,
    EarningsHistoryResponseModel,
    EarningsEstimatePeriodModel,
    EarningsEstimatesResponseModel,
    PriceTargetsModel,
    PriceTargetsResponseModel,
    RecommendationPeriodModel,
    RecommendationsResponseModel,
    UpgradeDowngradeModel,
    UpgradesDowngradesResponseModel,
    HistoricalQuoteModel,
    HistoricalQuotesResponseModel,
    CorrelationModel,
)


@mcp.tool
async def get_current_stock_price(ticker: str) -> StockPriceModel:
    """Get the current stock price including regular market, pre-market, and post-market prices.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'SPY', 'TSLA').
    
    Returns:
        StockPriceModel with prices from all trading sessions:
        - regular_market_price: Price during regular trading hours (9:30 AM - 4:00 PM ET)
        - pre_market_price: Pre-market price (4:00 AM - 9:30 AM ET) if available
        - post_market_price: After-hours price (4:00 PM - 8:00 PM ET) if available
        Each includes price, change, change_percent, and timestamp.
    """
    stk = yf.Ticker(ticker)
    info = stk.info
    
    # Regular market data
    regular_price = info.get("regularMarketPrice")
    regular_change = info.get("regularMarketChange")
    regular_change_pct = info.get("regularMarketChangePercent")
    regular_time = info.get("regularMarketTime")
    
    # Pre-market data (yfinance doesn't always expose this separately)
    pre_price = info.get("preMarketPrice")
    pre_change = info.get("preMarketChange")
    pre_change_pct = info.get("preMarketChangePercent")
    pre_time = info.get("preMarketTime")
    
    # Post-market data
    post_price = info.get("postMarketPrice")
    post_change = info.get("postMarketChange")
    post_change_pct = info.get("postMarketChangePercent")
    post_time = info.get("postMarketTime")
    
    return StockPriceModel(
        ticker=ticker,
        regular_market_price=regular_price,
        regular_market_change=regular_change,
        regular_market_change_percent=regular_change_pct,
        regular_market_time=regular_time,
        pre_market_price=pre_price,
        pre_market_change=pre_change,
        pre_market_change_percent=pre_change_pct,
        pre_market_time=pre_time,
        post_market_price=post_price,
        post_market_change=post_change,
        post_market_change_percent=post_change_pct,
        post_market_time=post_time,
        currency=info.get("currency", "USD"),
        market_state=info.get("marketState"),
    )


@mcp.tool
async def get_historical_quotes(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
) -> HistoricalQuotesResponseModel:
    """Get historical OHLCV price data for a ticker.

    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'SPY', 'TSLA').
        period: Time period to fetch. Valid values: '1d', '5d', '1mo', '3mo',
            '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.
        interval: Data interval. Valid values: '1m', '2m', '5m', '15m', '30m',
            '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'.
            Note: Intraday intervals (< 1d) only work for periods up to '1mo'.
            '1m' interval only available for '1d' or '5d' periods.

    Returns:
        HistoricalQuotesResponseModel with list of HistoricalQuoteModel objects
        containing: date, open, high, low, close, volume, dividends, stock_splits.
    """
    stk = yf.Ticker(ticker)
    hist = stk.history(period=period, interval=interval, auto_adjust=False)

    quotes = []
    for idx, row in hist.iterrows():
        # idx is a Timestamp
        if hasattr(idx, 'strftime'):
            date_str = idx.strftime('%Y-%m-%d') if interval in ('1d', '5d', '1wk', '1mo', '3mo') else idx.isoformat()
        else:
            date_str = str(idx)

        quotes.append(HistoricalQuoteModel(
            date=date_str,
            open=None if isna(row.get('Open')) else float(row.get('Open')),
            high=None if isna(row.get('High')) else float(row.get('High')),
            low=None if isna(row.get('Low')) else float(row.get('Low')),
            close=None if isna(row.get('Close')) else float(row.get('Close')),
            volume=None if isna(row.get('Volume')) else int(row.get('Volume')),
            dividends=None if isna(row.get('Dividends')) else float(row.get('Dividends')),
            stock_splits=None if isna(row.get('Stock Splits')) else float(row.get('Stock Splits')),
        ))

    return HistoricalQuotesResponseModel(
        ticker=ticker,
        period=period,
        interval=interval,
        quotes=quotes,
        count=len(quotes),
    )


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


@mcp.tool
async def get_income_statement(
    ticker: str, quarterly: bool = False, ttm: bool = False
) -> IncomeStatementResponseModel:
    """Get the income statement (profit & loss) for a company.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'MSFT').
        quarterly: If True, returns quarterly data (last 4-6 quarters).
        ttm: If True, returns trailing twelve months data (single period).
    
    Returns:
        FinancialStatementModel with IncomeStatementPeriodModel objects containing:
        - Revenue: total_revenue, operating_revenue
        - Costs: cost_of_revenue, gross_profit
        - Operating: operating_expense, R&D, SG&A, operating_income
        - Profitability: EBIT, EBITDA, pretax_income, net_income
        - Per-share: diluted_eps, basic_eps, share counts
        - Key metrics: normalized_income, normalized_ebitda
    
    Note: quarterly and ttm are mutually exclusive; ttm takes precedence.
    """
    stk = yf.Ticker(ticker)
    
    if ttm:
        df = stk.ttm_income_stmt
        frequency = "ttm"
    elif quarterly:
        df = stk.quarterly_income_stmt
        frequency = "quarterly"
    else:
        df = stk.income_stmt
        frequency = "annual"
    
    if df is None or df.empty:
        return IncomeStatementResponseModel(
            ticker=ticker,
            frequency=frequency,
            periods=[]
        )
    
    def get_val(row_name: str, col) -> float | None:
        try:
            val = df.loc[row_name, col]
            return None if isna(val) else float(val)
        except (KeyError, TypeError):
            return None
    
    periods = []
    for col in df.columns:
        period_end = str(col)[:10]  # Extract YYYY-MM-DD
        periods.append(IncomeStatementPeriodModel(
            period_end=period_end,
            total_revenue=get_val("Total Revenue", col),
            operating_revenue=get_val("Operating Revenue", col),
            cost_of_revenue=get_val("Cost Of Revenue", col),
            gross_profit=get_val("Gross Profit", col),
            operating_expense=get_val("Operating Expense", col),
            research_and_development=get_val("Research And Development", col),
            selling_general_administration=get_val("Selling General And Administration", col),
            operating_income=get_val("Operating Income", col),
            ebit=get_val("EBIT", col),
            ebitda=get_val("EBITDA", col),
            net_interest_income=get_val("Net Interest Income", col),
            interest_expense=get_val("Interest Expense", col),
            interest_income=get_val("Interest Income", col),
            pretax_income=get_val("Pretax Income", col),
            tax_provision=get_val("Tax Provision", col),
            net_income=get_val("Net Income", col),
            net_income_common_stockholders=get_val("Net Income Common Stockholders", col),
            diluted_eps=get_val("Diluted EPS", col),
            basic_eps=get_val("Basic EPS", col),
            diluted_average_shares=get_val("Diluted Average Shares", col),
            basic_average_shares=get_val("Basic Average Shares", col),
            total_expenses=get_val("Total Expenses", col),
            normalized_income=get_val("Normalized Income", col),
            normalized_ebitda=get_val("Normalized EBITDA", col),
        ))
    
    return IncomeStatementResponseModel(
        ticker=ticker,
        frequency=frequency,
        periods=periods
    )


@mcp.tool
async def get_balance_sheet(
    ticker: str, quarterly: bool = False
) -> BalanceSheetResponseModel:
    """Get the balance sheet for a company.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'MSFT').
        quarterly: If True, returns quarterly data (last 4-6 quarters).
    
    Returns:
        FinancialStatementModel with BalanceSheetPeriodModel objects containing:
        - Assets: total_assets, current_assets, cash, receivables, inventory, PPE, goodwill
        - Liabilities: total_liabilities, current_liabilities, accounts_payable, debt
        - Equity: total_equity, common_stock_equity, retained_earnings, shares
        - Derived: total_debt, net_debt, working_capital, invested_capital
    
    Note: TTM (trailing twelve months) is not available for balance sheets.
    """
    stk = yf.Ticker(ticker)
    
    if quarterly:
        df = stk.quarterly_balance_sheet
        frequency = "quarterly"
    else:
        df = stk.balance_sheet
        frequency = "annual"
    
    if df is None or df.empty:
        return BalanceSheetResponseModel(
            ticker=ticker,
            frequency=frequency,
            periods=[]
        )
    
    def get_val(row_name: str, col) -> float | None:
        try:
            val = df.loc[row_name, col]
            return None if isna(val) else float(val)
        except (KeyError, TypeError):
            return None
    
    periods = []
    for col in df.columns:
        period_end = str(col)[:10]
        periods.append(BalanceSheetPeriodModel(
            period_end=period_end,
            total_assets=get_val("Total Assets", col),
            total_current_assets=get_val("Current Assets", col),
            cash_and_cash_equivalents=get_val("Cash Cash Equivalents And Short Term Investments", col),
            cash_equivalents=get_val("Cash Equivalents", col),
            short_term_investments=get_val("Other Short Term Investments", col),
            accounts_receivable=get_val("Accounts Receivable", col),
            inventory=get_val("Inventory", col),
            total_non_current_assets=get_val("Total Non Current Assets", col),
            net_ppe=get_val("Net PPE", col),
            goodwill_and_intangible_assets=get_val("Goodwill And Other Intangible Assets", col),
            total_liabilities=get_val("Total Liabilities Net Minority Interest", col),
            total_current_liabilities=get_val("Current Liabilities", col),
            accounts_payable=get_val("Accounts Payable", col),
            current_debt=get_val("Current Debt", col),
            total_non_current_liabilities=get_val("Total Non Current Liabilities Net Minority Interest", col),
            long_term_debt=get_val("Long Term Debt", col),
            total_equity=get_val("Total Equity Gross Minority Interest", col),
            common_stock_equity=get_val("Common Stock Equity", col),
            retained_earnings=get_val("Retained Earnings", col),
            treasury_shares_number=get_val("Treasury Shares Number", col),
            ordinary_shares_number=get_val("Ordinary Shares Number", col),
            total_debt=get_val("Total Debt", col),
            net_debt=get_val("Net Debt", col),
            working_capital=get_val("Working Capital", col),
            invested_capital=get_val("Invested Capital", col),
            tangible_book_value=get_val("Tangible Book Value", col),
        ))
    
    return BalanceSheetResponseModel(
        ticker=ticker,
        frequency=frequency,
        periods=periods
    )


@mcp.tool
async def get_cash_flow(
    ticker: str, quarterly: bool = False, ttm: bool = False
) -> CashFlowResponseModel:
    """Get the cash flow statement for a company.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'MSFT').
        quarterly: If True, returns quarterly data (last 4-6 quarters).
        ttm: If True, returns trailing twelve months data (single period).
    
    Returns:
        FinancialStatementModel with CashFlowPeriodModel objects containing:
        - Operating: operating_cash_flow, net_income, D&A, stock_comp, working capital changes
        - Investing: capex, PPE purchases, investment sales/purchases
        - Financing: dividends_paid, share_repurchases, debt_issuance/repayment
        - Key metrics: free_cash_flow, cash position changes
    
    Note: quarterly and ttm are mutually exclusive; ttm takes precedence.
    """
    stk = yf.Ticker(ticker)
    
    if ttm:
        df = stk.ttm_cashflow
        frequency = "ttm"
    elif quarterly:
        df = stk.quarterly_cashflow
        frequency = "quarterly"
    else:
        df = stk.cashflow
        frequency = "annual"
    
    if df is None or df.empty:
        return CashFlowResponseModel(
            ticker=ticker,
            frequency=frequency,
            periods=[]
        )
    
    def get_val(row_name: str, col) -> float | None:
        try:
            val = df.loc[row_name, col]
            return None if isna(val) else float(val)
        except (KeyError, TypeError):
            return None
    
    periods = []
    for col in df.columns:
        period_end = str(col)[:10]
        periods.append(CashFlowPeriodModel(
            period_end=period_end,
            operating_cash_flow=get_val("Operating Cash Flow", col),
            net_income_from_continuing_operations=get_val("Net Income From Continuing Operations", col),
            depreciation_and_amortization=get_val("Depreciation And Amortization", col),
            stock_based_compensation=get_val("Stock Based Compensation", col),
            change_in_working_capital=get_val("Change In Working Capital", col),
            change_in_receivables=get_val("Changes In Account Receivables", col),
            change_in_inventory=get_val("Change In Inventory", col),
            change_in_payables=get_val("Change In Account Payable", col),
            investing_cash_flow=get_val("Investing Cash Flow", col),
            capital_expenditure=get_val("Capital Expenditure", col),
            purchase_of_ppe=get_val("Purchase Of PPE", col),
            sale_of_investment=get_val("Sale Of Investment", col),
            purchase_of_investment=get_val("Purchase Of Investment", col),
            financing_cash_flow=get_val("Financing Cash Flow", col),
            cash_dividends_paid=get_val("Cash Dividends Paid", col),
            common_stock_dividend_paid=get_val("Common Stock Dividend Paid", col),
            repurchase_of_capital_stock=get_val("Repurchase Of Capital Stock", col),
            net_common_stock_issuance=get_val("Net Common Stock Issuance", col),
            net_issuance_payments_of_debt=get_val("Net Issuance Payments Of Debt", col),
            net_long_term_debt_issuance=get_val("Net Long Term Debt Issuance", col),
            long_term_debt_payments=get_val("Long Term Debt Payments", col),
            long_term_debt_issuance=get_val("Long Term Debt Issuance", col),
            net_short_term_debt_issuance=get_val("Net Short Term Debt Issuance", col),
            free_cash_flow=get_val("Free Cash Flow", col),
            end_cash_position=get_val("End Cash Position", col),
            beginning_cash_position=get_val("Beginning Cash Position", col),
            changes_in_cash=get_val("Changes In Cash", col),
            interest_paid=get_val("Interest Paid Supplemental Data", col),
            income_tax_paid=get_val("Income Tax Paid Supplemental Data", col),
        ))
    
    return CashFlowResponseModel(
        ticker=ticker,
        frequency=frequency,
        periods=periods
    )


@mcp.tool
async def get_option_expirations(ticker: str) -> OptionExpirationsModel:
    """Get all available option expiration dates for a ticker.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'SPY', 'TSLA').
    
    Returns:
        OptionExpirationsModel with list of expiration dates in YYYY-MM-DD format.
        Use these dates with get_option_chain to get the full option chain.
    """
    stk = yf.Ticker(ticker)
    expirations = list(stk.options)
    return OptionExpirationsModel(
        ticker=ticker,
        expirations=expirations,
        count=len(expirations)
    )


def _df_to_contracts(df) -> list[OptionContractModel]:
    """Convert option chain DataFrame to list of OptionContractModel."""
    contracts = []
    for _, row in df.iterrows():
        contracts.append(OptionContractModel(
            contract_symbol=row.get('contractSymbol', ''),
            strike=float(row.get('strike', 0)),
            last_price=float(row['lastPrice']) if not isna(row.get('lastPrice')) else None,
            bid=float(row['bid']) if not isna(row.get('bid')) else None,
            ask=float(row['ask']) if not isna(row.get('ask')) else None,
            change=float(row['change']) if not isna(row.get('change')) else None,
            percent_change=float(row['percentChange']) if not isna(row.get('percentChange')) else None,
            volume=int(row['volume']) if not isna(row.get('volume')) else None,
            open_interest=int(row['openInterest']) if not isna(row.get('openInterest')) else None,
            implied_volatility=float(row['impliedVolatility']) if not isna(row.get('impliedVolatility')) else None,
            in_the_money=bool(row.get('inTheMoney')) if not isna(row.get('inTheMoney')) else None,
            contract_size=row.get('contractSize'),
            currency=row.get('currency'),
            last_trade_date=str(row['lastTradeDate']) if not isna(row.get('lastTradeDate')) else None,
        ))
    return contracts


@mcp.tool
async def get_option_chain(ticker: str, expiration_date: str) -> OptionChainModel:
    """Get the full option chain (calls and puts) for a specific expiration date.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'SPY', 'TSLA').
        expiration_date: Expiration date in YYYY-MM-DD format (from get_option_expirations).
    
    Returns:
        OptionChainModel with:
        - underlying_price: Current stock price
        - calls: List of call OptionContractModel objects
        - puts: List of put OptionContractModel objects
        Each contract includes: strike, bid/ask, last price, volume, open interest,
        implied volatility, in-the-money flag, and contract metadata.
    """
    stk = yf.Ticker(ticker)
    
    if expiration_date not in stk.options:
        available = ', '.join(stk.options[:10])
        raise ValueError(f"Expiration {expiration_date} not found. Available: {available}...")
    
    oc = stk.option_chain(expiration_date)
    underlying_price = oc.underlying.get('regularMarketPrice', 0.0)
    
    calls = _df_to_contracts(oc.calls)
    puts = _df_to_contracts(oc.puts)
    
    return OptionChainModel(
        ticker=ticker,
        expiration_date=expiration_date,
        underlying_price=underlying_price,
        calls=calls,
        puts=puts
    )


@mcp.tool
async def get_atm_options(
    ticker: str, 
    expiration_date: str | None = None,
    nearby_strikes: int = 3
) -> ATMOptionsModel:
    """Get at-the-money (ATM) options for a ticker.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'SPY', 'TSLA').
        expiration_date: Specific expiration (YYYY-MM-DD). If None, uses nearest expiration.
        nearby_strikes: Number of strikes above/below ATM to include (default: 3).
    
    Returns:
        ATMOptionsModel with:
        - underlying_price: Current stock price
        - atm_strike: Strike closest to current price
        - call/put: ATM call and put contracts
        - nearby_calls/puts: Contracts for strikes around ATM
    """
    stk = yf.Ticker(ticker)
    
    if expiration_date is None:
        if not stk.options:
            raise ValueError(f"No options available for {ticker}")
        expiration_date = stk.options[0]
    elif expiration_date not in stk.options:
        available = ', '.join(stk.options[:10])
        raise ValueError(f"Expiration {expiration_date} not found. Available: {available}...")
    
    oc = stk.option_chain(expiration_date)
    underlying_price = oc.underlying.get('regularMarketPrice', 0.0)
    
    # Find ATM strike
    calls_df = oc.calls
    strikes = calls_df['strike'].tolist()
    atm_strike = min(strikes, key=lambda x: abs(x - underlying_price))
    
    # Get ATM contracts
    atm_call_row = calls_df[calls_df['strike'] == atm_strike]
    atm_put_row = oc.puts[oc.puts['strike'] == atm_strike]
    
    atm_call = _df_to_contracts(atm_call_row)[0] if not atm_call_row.empty else None
    atm_put = _df_to_contracts(atm_put_row)[0] if not atm_put_row.empty else None
    
    # Get nearby strikes
    atm_idx = strikes.index(atm_strike)
    nearby_strike_list = strikes[max(0, atm_idx - nearby_strikes):atm_idx + nearby_strikes + 1]
    
    nearby_calls = _df_to_contracts(calls_df[calls_df['strike'].isin(nearby_strike_list)])
    nearby_puts = _df_to_contracts(oc.puts[oc.puts['strike'].isin(nearby_strike_list)])
    
    return ATMOptionsModel(
        ticker=ticker,
        expiration_date=expiration_date,
        underlying_price=underlying_price,
        atm_strike=atm_strike,
        call=atm_call,
        put=atm_put,
        nearby_calls=nearby_calls,
        nearby_puts=nearby_puts
    )


@mcp.tool
async def get_options_by_strike_range(
    ticker: str,
    expiration_date: str,
    min_strike: float | None = None,
    max_strike: float | None = None
) -> OptionChainModel:
    """Get option chain filtered by strike price range.
    
    Args:
        ticker: Stock/ETF ticker symbol.
        expiration_date: Expiration date in YYYY-MM-DD format.
        min_strike: Minimum strike price (inclusive).
        max_strike: Maximum strike price (inclusive).
    
    Returns:
        OptionChainModel with only calls/puts within the strike range.
    """
    stk = yf.Ticker(ticker)
    
    if expiration_date not in stk.options:
        available = ', '.join(stk.options[:10])
        raise ValueError(f"Expiration {expiration_date} not found. Available: {available}...")
    
    oc = stk.option_chain(expiration_date)
    underlying_price = oc.underlying.get('regularMarketPrice', 0.0)
    
    calls_df = oc.calls
    puts_df = oc.puts
    
    if min_strike is not None:
        calls_df = calls_df[calls_df['strike'] >= min_strike]
        puts_df = puts_df[puts_df['strike'] >= min_strike]
    if max_strike is not None:
        calls_df = calls_df[calls_df['strike'] <= max_strike]
        puts_df = puts_df[puts_df['strike'] <= max_strike]
    
    calls = _df_to_contracts(calls_df)
    puts = _df_to_contracts(puts_df)
    
    return OptionChainModel(
        ticker=ticker,
        expiration_date=expiration_date,
        underlying_price=underlying_price,
        calls=calls,
        puts=puts
    )


# ==================== EARNINGS TOOLS ====================


@mcp.tool
async def get_earnings_dates(ticker: str) -> EarningsDatesResponseModel:
    """Get upcoming and historical earnings dates with EPS estimates and surprises.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'MSFT', 'TSLA').
    
    Returns:
        EarningsDatesResponseModel with list of EarningsDateModel containing:
        - earnings_date: ISO format datetime of earnings announcement
        - eps_estimate: Analyst consensus EPS estimate
        - reported_eps: Actual reported EPS (None for future dates)
        - surprise_percent: Percentage surprise vs estimate (None for future dates)
    
    Includes both future estimated dates and historical reported earnings.
    """
    stk = yf.Ticker(ticker)
    df = stk.earnings_dates
    
    if df is None or df.empty:
        return EarningsDatesResponseModel(ticker=ticker, earnings_dates=[], count=0)
    
    earnings_dates = []
    for idx, row in df.iterrows():
        # idx is a Timestamp, row has: EPS Estimate, Reported EPS, Surprise(%)
        eps_est = row.get('EPS Estimate')
        eps_rep = row.get('Reported EPS')
        surprise = row.get('Surprise(%)')
        
        earnings_dates.append(EarningsDateModel(
            earnings_date=idx.isoformat(),
            eps_estimate=None if isna(eps_est) else float(eps_est),
            reported_eps=None if isna(eps_rep) else float(eps_rep),
            surprise_percent=None if isna(surprise) else float(surprise),
        ))
    
    return EarningsDatesResponseModel(
        ticker=ticker,
        earnings_dates=earnings_dates,
        count=len(earnings_dates)
    )


@mcp.tool
async def get_earnings_history(ticker: str) -> EarningsHistoryResponseModel:
    """Get historical quarterly earnings results with actuals vs estimates.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'MSFT', 'TSLA').
    
    Returns:
        EarningsHistoryResponseModel with list of EarningsHistoryItemModel containing:
        - quarter: Quarter end date (YYYY-MM-DD)
        - eps_actual: Actual reported EPS
        - eps_estimate: Analyst consensus estimate
        - eps_difference: Actual minus estimate
        - surprise_percent: Surprise as decimal (e.g., 0.05 = 5% beat)
        - methodology: Accounting standard (typically 'gaap')
    
    Returns last ~4-8 quarters of historical earnings data.
    """
    stk = yf.Ticker(ticker)
    df = stk.earnings_history
    
    if df is None or df.empty:
        return EarningsHistoryResponseModel(ticker=ticker, history=[], count=0)
    
    history = []
    for idx, row in df.iterrows():
        # idx is quarter end date, columns: epsActual, epsEstimate, epsDifference, surprisePercent, methodology
        history.append(EarningsHistoryItemModel(
            quarter=str(idx)[:10],
            eps_actual=None if isna(row.get('epsActual')) else float(row.get('epsActual')),
            eps_estimate=None if isna(row.get('epsEstimate')) else float(row.get('epsEstimate')),
            eps_difference=None if isna(row.get('epsDifference')) else float(row.get('epsDifference')),
            surprise_percent=None if isna(row.get('surprisePercent')) else float(row.get('surprisePercent')),
            methodology=row.get('methodology'),
        ))
    
    return EarningsHistoryResponseModel(
        ticker=ticker,
        history=history,
        count=len(history)
    )


@mcp.tool
async def get_earnings_estimates(ticker: str) -> EarningsEstimatesResponseModel:
    """Get analyst EPS estimates for current/next quarter and current/next year.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'MSFT', 'TSLA').
    
    Returns:
        EarningsEstimatesResponseModel with list of EarningsEstimatePeriodModel containing:
        - period: Period identifier ('0q'=current quarter, '+1q'=next quarter, '0y'=current year, '+1y'=next year)
        - avg_estimate: Mean analyst EPS estimate
        - low_estimate: Lowest analyst EPS estimate
        - high_estimate: Highest analyst EPS estimate
        - year_ago_eps: EPS from same period year ago
        - growth: Estimated year-over-year growth rate
        - currency: Currency (typically 'USD')
        - methodology: Accounting standard (typically 'gaap')
    
    Useful for setting earnings expectations and tracking estimate revisions.
    """
    stk = yf.Ticker(ticker)
    df = stk.earnings_estimate
    
    if df is None or df.empty:
        return EarningsEstimatesResponseModel(ticker=ticker, estimates=[], count=0)
    
    estimates = []
    for idx, row in df.iterrows():
        # idx is period ('0q', '+1q', '0y', '+1y'), columns: avg, low, high, yearAgoEps, growth, currency, methodology
        estimates.append(EarningsEstimatePeriodModel(
            period=idx,
            avg_estimate=None if isna(row.get('avg')) else float(row.get('avg')),
            low_estimate=None if isna(row.get('low')) else float(row.get('low')),
            high_estimate=None if isna(row.get('high')) else float(row.get('high')),
            year_ago_eps=None if isna(row.get('yearAgoEps')) else float(row.get('yearAgoEps')),
            growth=None if isna(row.get('growth')) else float(row.get('growth')),
            currency=row.get('currency'),
            methodology=row.get('methodology'),
        ))
    
    return EarningsEstimatesResponseModel(
        ticker=ticker,
        estimates=estimates,
        count=len(estimates)
    )


# ==================== ANALYST TOOLS ====================


@mcp.tool
async def get_analyst_price_targets(ticker: str) -> PriceTargetsResponseModel:
    """Get analyst price targets (mean, median, high, low, current).
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'MSFT', 'TSLA').
    
    Returns:
        PriceTargetsResponseModel with PriceTargetsModel containing:
        - current: Current stock price
        - high: Highest analyst price target
        - low: Lowest analyst price target
        - mean: Average analyst price target
        - median: Median analyst price target
    
    Useful for gauging analyst sentiment and upside/downside potential.
    """
    stk = yf.Ticker(ticker)
    targets = stk.analyst_price_targets
    
    if not targets:
        return PriceTargetsResponseModel(
            ticker=ticker,
            price_targets=PriceTargetsModel()
        )
    
    return PriceTargetsResponseModel(
        ticker=ticker,
        price_targets=PriceTargetsModel(
            current=targets.get('current'),
            high=targets.get('high'),
            low=targets.get('low'),
            mean=targets.get('mean'),
            median=targets.get('median'),
        )
    )


@mcp.tool
async def get_recommendations(ticker: str) -> RecommendationsResponseModel:
    """Get analyst recommendation trends (strong buy, buy, hold, sell, strong sell) over time.
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'MSFT', 'TSLA').
    
    Returns:
        RecommendationsResponseModel with list of RecommendationPeriodModel containing:
        - period: Time period ('0m'=current month, '-1m'=1 month ago, etc.)
        - strong_buy: Count of strong buy ratings
        - buy: Count of buy ratings
        - hold: Count of hold ratings
        - sell: Count of sell ratings
        - strong_sell: Count of strong sell ratings
        - total: Total analysts covering
    
    Shows how analyst sentiment has evolved over recent months.
    """
    stk = yf.Ticker(ticker)
    df = stk.recommendations
    
    if df is None or df.empty:
        return RecommendationsResponseModel(ticker=ticker, recommendations=[], count=0)
    
    recommendations = []
    for idx, row in df.iterrows():
        # idx is period ('0m', '-1m', '-2m', '-3m'), columns: strongBuy, buy, hold, sell, strongSell
        strong_buy = int(row.get('strongBuy', 0))
        buy = int(row.get('buy', 0))
        hold = int(row.get('hold', 0))
        sell = int(row.get('sell', 0))
        strong_sell = int(row.get('strongSell', 0))
        
        recommendations.append(RecommendationPeriodModel(
            period=str(idx),
            strong_buy=strong_buy,
            buy=buy,
            hold=hold,
            sell=sell,
            strong_sell=strong_sell,
            total=strong_buy + buy + hold + sell + strong_sell,
        ))
    
    return RecommendationsResponseModel(
        ticker=ticker,
        recommendations=recommendations,
        count=len(recommendations)
    )


@mcp.tool
async def get_upgrades_downgrades(
    ticker: str,
    limit: int = 50
) -> UpgradesDowngradesResponseModel:
    """Get recent analyst rating changes (upgrades, downgrades, initiations, reiterations).
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'MSFT', 'TSLA').
        limit: Maximum number of recent changes to return (default: 50).
    
    Returns:
        UpgradesDowngradesResponseModel with list of UpgradeDowngradeModel containing:
        - date: Date of rating change (ISO format)
        - firm: Analyst firm name
        - to_grade: New rating (e.g., 'Buy', 'Hold', 'Sell', 'Overweight')
        - from_grade: Previous rating
        - action: Type of change ('up', 'down', 'init', 'reiterated', 'maintained')
        - price_target: New price target (if provided)
        - prior_price_target: Previous price target
    
    Returns most recent changes first. Useful for tracking sentiment shifts.
    """
    stk = yf.Ticker(ticker)
    df = stk.upgrades_downgrades
    
    if df is None or df.empty:
        return UpgradesDowngradesResponseModel(ticker=ticker, upgrades_downgrades=[], count=0)
    
    # Sort by date descending (most recent first) and limit
    df = df.sort_index(ascending=False).head(limit)
    
    changes = []
    for idx, row in df.iterrows():
        # idx is datetime, columns: Firm, To Grade, From Grade, Action, Price Target, Prior Price Target
        changes.append(UpgradeDowngradeModel(
            date=idx.isoformat(),
            firm=row.get('Firm', ''),
            to_grade=row.get('To Grade'),
            from_grade=row.get('From Grade'),
            action=row.get('Action'),
            price_target=None if isna(row.get('Price Target')) else float(row.get('Price Target')),
            prior_price_target=None if isna(row.get('Prior Price Target')) else float(row.get('Prior Price Target')),
        ))
    
    return UpgradesDowngradesResponseModel(
        ticker=ticker,
        upgrades_downgrades=changes,
        count=len(changes)
    )


# ==================== CORRELATION TOOLS ====================


@mcp.tool
async def get_correlation(
    ticker1: str,
    ticker2: str,
    period: str = "1y",
    interval: str = "1d",
) -> CorrelationModel:
    """Calculate Pearson correlation coefficient between two tickers' returns.
    
    Fetches historical price data for both tickers from Yahoo Finance, aligns
    them by date, computes daily returns, and calculates the correlation.
    
    Args:
        ticker1: First ticker symbol (e.g., 'AAPL', 'SPY').
        ticker2: Second ticker symbol (e.g., 'MSFT', 'QQQ').
        period: Time period to fetch. Valid values: '1d', '5d', '1mo', '3mo',
            '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.
        interval: Data interval. Valid values: '1m', '2m', '5m', '15m', '30m',
            '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'.
            Note: Intraday intervals (< 1d) only work for periods up to '1mo'.
            '1m' interval only available for '1d' or '5d' periods.
    
    Returns:
        CorrelationModel with:
        - correlation: Pearson correlation coefficient (-1 to 1)
        - data_points: Number of aligned data points used
        - ticker1/ticker2 returns statistics (mean, std)
        - error: Error message if correlation couldn't be calculated
    
    Note:
        - Correlation of 1 = perfect positive correlation
        - Correlation of -1 = perfect negative correlation
        - Correlation of 0 = no linear relationship
        - Requires at least 2 data points to calculate
    """
    import pandas as pd
    import numpy as np
    
    # Handle same ticker case - correlation is 1.0
    if ticker1.upper() == ticker2.upper():
        # Still fetch data to get statistics
        stk = yf.Ticker(ticker1)
        hist = stk.history(period=period, interval=interval, auto_adjust=True)
        if hist.empty:
            return CorrelationModel(
                ticker1=ticker1,
                ticker2=ticker2,
                period=period,
                interval=interval,
                correlation=None,
                data_points=0,
                error="No data returned for ticker"
            )
        close = hist['Close'].dropna()
        if len(close) < 2:
            return CorrelationModel(
                ticker1=ticker1,
                ticker2=ticker2,
                period=period,
                interval=interval,
                correlation=None,
                data_points=len(close),
                error="Insufficient data points"
            )
        returns = close.pct_change().dropna()
        if len(returns) < 2:
            return CorrelationModel(
                ticker1=ticker1,
                ticker2=ticker2,
                period=period,
                interval=interval,
                correlation=None,
                data_points=len(returns),
                error="Insufficient return data points"
            )
        r_mean = float(returns.mean())
        r_std = float(returns.std())
        return CorrelationModel(
            ticker1=ticker1,
            ticker2=ticker2,
            period=period,
            interval=interval,
            correlation=1.0,
            data_points=len(returns),
            ticker1_returns_mean=r_mean,
            ticker1_returns_std=r_std,
            ticker2_returns_mean=r_mean,
            ticker2_returns_std=r_std,
            error=None
        )
    
    # Fetch historical data for both tickers
    stk1 = yf.Ticker(ticker1)
    stk2 = yf.Ticker(ticker2)
    
    hist1 = stk1.history(period=period, interval=interval, auto_adjust=True)
    hist2 = stk2.history(period=period, interval=interval, auto_adjust=True)
    
    # Check if we got data
    if hist1.empty or hist2.empty:
        return CorrelationModel(
            ticker1=ticker1,
            ticker2=ticker2,
            period=period,
            interval=interval,
            correlation=None,
            data_points=0,
            error="No data returned for one or both tickers"
        )
    
    # Extract close prices and align by date
    close1 = hist1['Close'].rename(ticker1)
    close2 = hist2['Close'].rename(ticker2)
    
    # Join on index (date) - inner join to only keep overlapping dates
    aligned = pd.concat([close1, close2], axis=1, join='inner')
    
    # Drop any rows with NaN
    aligned = aligned.dropna()
    
    if len(aligned) < 2:
        return CorrelationModel(
            ticker1=ticker1,
            ticker2=ticker2,
            period=period,
            interval=interval,
            correlation=None,
            data_points=len(aligned),
            error="Insufficient overlapping data points (need at least 2)"
        )
    
    # Calculate daily returns (percentage change)
    returns1 = aligned[ticker1].pct_change().dropna()
    returns2 = aligned[ticker2].pct_change().dropna()
    
    # Re-align returns after pct_change (first row will be NaN)
    returns_df = pd.concat([returns1, returns2], axis=1, join='inner').dropna()
    
    if len(returns_df) < 2:
        return CorrelationModel(
            ticker1=ticker1,
            ticker2=ticker2,
            period=period,
            interval=interval,
            correlation=None,
            data_points=len(returns_df),
            error="Insufficient return data points after calculation"
        )
    
    # Calculate Pearson correlation
    correlation = returns_df[ticker1].corr(returns_df[ticker2])
    
    # Calculate statistics
    r1_mean = float(returns_df[ticker1].mean())
    r1_std = float(returns_df[ticker1].std())
    r2_mean = float(returns_df[ticker2].mean())
    r2_std = float(returns_df[ticker2].std())
    
    return CorrelationModel(
        ticker1=ticker1,
        ticker2=ticker2,
        period=period,
        interval=interval,
        correlation=float(correlation) if not pd.isna(correlation) else None,
        data_points=len(returns_df),
        ticker1_returns_mean=r1_mean,
        ticker1_returns_std=r1_std,
        ticker2_returns_mean=r2_mean,
        ticker2_returns_std=r2_std,
        error=None
    )


# ==================== BETA TOOLS ====================


@mcp.tool
async def get_beta(
    ticker: str,
    benchmark: str = "SPY",
    period: str = "1y",
    interval: str = "1d",
) -> BetaModel:
    """Calculate beta (and alpha) of a ticker relative to a benchmark.
    
    Beta measures the volatility of a stock relative to a benchmark (default: SPY).
    - Beta > 1: Stock is more volatile than benchmark
    - Beta < 1: Stock is less volatile than benchmark
    - Beta < 0: Stock moves inversely to benchmark
    
    Also calculates Jensen's alpha (excess return vs CAPM prediction) and R-squared
    (goodness of fit of the regression).
    
    Args:
        ticker: Stock/ETF ticker symbol (e.g., 'AAPL', 'TSLA', 'QQQ').
        benchmark: Benchmark ticker symbol (default: 'SPY' for S&P 500).
        period: Time period to fetch. Valid values: '1d', '5d', '1mo', '3mo',
            '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.
        interval: Data interval. Valid values: '1m', '2m', '5m', '15m', '30m',
            '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'.
            Note: Intraday intervals (< 1d) only work for periods up to '1mo'.
            '1m' interval only available for '1d' or '5d' periods.
    
    Returns:
        BetaModel with:
        - beta: Slope of regression (ticker returns vs benchmark returns)
        - alpha: Jensen's alpha (annualized excess return)
        - r_squared: Coefficient of determination (0-1)
        - data_points: Number of aligned return observations
        - Returns statistics for both ticker and benchmark
        - error: Error message if calculation failed
    """
    import pandas as pd
    import numpy as np
    
    # Handle same ticker case - beta is 1.0, alpha is 0
    if ticker.upper() == benchmark.upper():
        stk = yf.Ticker(ticker)
        hist = stk.history(period=period, interval=interval, auto_adjust=True)
        if hist.empty:
            return BetaModel(
                ticker=ticker,
                benchmark=benchmark,
                period=period,
                interval=interval,
                beta=None,
                alpha=None,
                r_squared=None,
                data_points=0,
                error="No data returned for ticker"
            )
        close = hist['Close'].dropna()
        if len(close) < 2:
            return BetaModel(
                ticker=ticker,
                benchmark=benchmark,
                period=period,
                interval=interval,
                beta=None,
                alpha=None,
                r_squared=None,
                data_points=len(close),
                error="Insufficient data points"
            )
        returns = close.pct_change().dropna()
        if len(returns) < 2:
            return BetaModel(
                ticker=ticker,
                benchmark=benchmark,
                period=period,
                interval=interval,
                beta=None,
                alpha=None,
                r_squared=None,
                data_points=len(returns),
                error="Insufficient return data points"
            )
        r_mean = float(returns.mean())
        r_std = float(returns.std())
        # Annualize alpha (assuming 252 trading days for daily data)
        periods_per_year = 252 if interval == "1d" else 12 if interval in ("1mo", "1wk") else 1
        alpha_annualized = 0.0  # alpha is 0 when ticker == benchmark
        return BetaModel(
            ticker=ticker,
            benchmark=benchmark,
            period=period,
            interval=interval,
            beta=1.0,
            alpha=alpha_annualized,
            r_squared=1.0,
            data_points=len(returns),
            ticker_returns_mean=r_mean,
            ticker_returns_std=r_std,
            benchmark_returns_mean=r_mean,
            benchmark_returns_std=r_std,
            error=None
        )
    
    # Fetch historical data for both tickers
    stk1 = yf.Ticker(ticker)
    stk2 = yf.Ticker(benchmark)
    
    hist1 = stk1.history(period=period, interval=interval, auto_adjust=True)
    hist2 = stk2.history(period=period, interval=interval, auto_adjust=True)
    
    # Check if we got data
    if hist1.empty or hist2.empty:
        return BetaModel(
            ticker=ticker,
            benchmark=benchmark,
            period=period,
            interval=interval,
            beta=None,
            alpha=None,
            r_squared=None,
            data_points=0,
            error="No data returned for one or both tickers"
        )
    
    # Extract close prices and align by date
    close1 = hist1['Close'].rename(ticker)
    close2 = hist2['Close'].rename(benchmark)
    
    # Join on index (date) - inner join to only keep overlapping dates
    aligned = pd.concat([close1, close2], axis=1, join='inner')
    
    # Drop any rows with NaN
    aligned = aligned.dropna()
    
    if len(aligned) < 2:
        return BetaModel(
            ticker=ticker,
            benchmark=benchmark,
            period=period,
            interval=interval,
            beta=None,
            alpha=None,
            r_squared=None,
            data_points=len(aligned),
            error="Insufficient overlapping data points (need at least 2)"
        )
    
    # Calculate returns (percentage change)
    returns1 = aligned[ticker].pct_change().dropna()
    returns2 = aligned[benchmark].pct_change().dropna()
    
    # Re-align returns after pct_change (first row will be NaN)
    returns_df = pd.concat([returns1, returns2], axis=1, join='inner').dropna()
    
    if len(returns_df) < 2:
        return BetaModel(
            ticker=ticker,
            benchmark=benchmark,
            period=period,
            interval=interval,
            beta=None,
            alpha=None,
            r_squared=None,
            data_points=len(returns_df),
            error="Insufficient return data points after calculation"
        )
    
    # Linear regression: ticker_returns = alpha + beta * benchmark_returns
    X = returns_df[benchmark].values
    y = returns_df[ticker].values
    
    # Using numpy for OLS regression
    X_mean = np.mean(X)
    y_mean = np.mean(y)
    
    # Calculate beta (covariance / variance of benchmark)
    covariance = np.sum((X - X_mean) * (y - y_mean))
    variance = np.sum((X - X_mean) ** 2)
    
    if variance == 0:
        return BetaModel(
            ticker=ticker,
            benchmark=benchmark,
            period=period,
            interval=interval,
            beta=None,
            alpha=None,
            r_squared=None,
            data_points=len(returns_df),
            error="Benchmark has zero variance"
        )
    
    beta = covariance / variance
    alpha = y_mean - beta * X_mean
    
    # Calculate R-squared
    y_pred = alpha + beta * X
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)
    
    if ss_tot == 0:
        r_squared = 1.0
    else:
        r_squared = 1 - (ss_res / ss_tot)
    
    # Annualize alpha (assuming 252 trading days for daily data)
    periods_per_year = 252 if interval == "1d" else 52 if interval == "1wk" else 12 if interval == "1mo" else 1
    alpha_annualized = alpha * periods_per_year
    
    # Calculate statistics
    ticker_returns_mean = float(returns_df[ticker].mean())
    ticker_returns_std = float(returns_df[ticker].std())
    benchmark_returns_mean = float(returns_df[benchmark].mean())
    benchmark_returns_std = float(returns_df[benchmark].std())
    
    return BetaModel(
        ticker=ticker,
        benchmark=benchmark,
        period=period,
        interval=interval,
        beta=float(beta),
        alpha=float(alpha_annualized),
        r_squared=float(r_squared),
        data_points=len(returns_df),
        ticker_returns_mean=ticker_returns_mean,
        ticker_returns_std=ticker_returns_std,
        benchmark_returns_mean=benchmark_returns_mean,
        benchmark_returns_std=benchmark_returns_std,
        error=None
    )
