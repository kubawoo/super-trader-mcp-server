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
