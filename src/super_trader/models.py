from pydantic import BaseModel


class DividendHistoryItemModel(BaseModel):
    date: str
    amount: float


class DividendDetailsModel(BaseModel):
    ticker: str
    dividend_rate: float | None = None
    dividend_yield: float | None = None
    trailing_annual_dividend_rate: float | None = None
    trailing_annual_dividend_yield: float | None = None
    ex_dividend_date: str | None = None
    dividend_date: str | None = None
    payout_ratio: float | None = None
    five_year_avg_dividend_yield: float | None = None
    history: list[DividendHistoryItemModel]


class NewsItemModel(BaseModel):
    title: str
    publisher: str
    link: str
    publish_time: int
    type: str
    thumbnail_url: str | None = None


class TopHoldingModel(BaseModel):
    ticker: str
    name: str
    pct: float


class ETFEquityStatsModel(BaseModel):
    ticker: str
    price_earnings: float | None = None
    price_book: float | None = None
    price_sales: float | None = None
    price_cashflow: float | None = None
    median_market_cap: float | None = None
    three_year_earnings_growth: float | None = None
    category_average_price_earnings: float | None = None
    category_average_price_book: float | None = None
    category_average_price_sales: float | None = None
    category_average_price_cashflow: float | None = None
    category_average_median_market_cap: float | None = None
    category_average_three_year_earnings_growth: float | None = None


class StockPriceModel(BaseModel):
    ticker: str
    regular_market_price: float | None = None
    regular_market_change: float | None = None
    regular_market_change_percent: float | None = None
    regular_market_time: int | None = None
    pre_market_price: float | None = None
    pre_market_change: float | None = None
    pre_market_change_percent: float | None = None
    pre_market_time: int | None = None
    post_market_price: float | None = None
    post_market_change: float | None = None
    post_market_change_percent: float | None = None
    post_market_time: int | None = None
    currency: str = "USD"
    market_state: str | None = None


class StockInfoModel(BaseModel):
    ticker: str
    sector: str
    industry: str
    market_cap: int
    employees: int
    display_name: str
    currency: str
    website: str
    country: str
    long_business_summary: str
    trailing_pe: float | None = None
    forward_pe: float | None = None
    total_revenue: int | None = None
    dividend_rate: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None
    beta: float | None = None
    target_mean_price: float | None = None


class IncomeStatementPeriodModel(BaseModel):
    period_end: str
    total_revenue: float | None = None
    operating_revenue: float | None = None
    cost_of_revenue: float | None = None
    gross_profit: float | None = None
    operating_expense: float | None = None
    research_and_development: float | None = None
    selling_general_administration: float | None = None
    operating_income: float | None = None
    ebit: float | None = None
    ebitda: float | None = None
    net_interest_income: float | None = None
    interest_expense: float | None = None
    interest_income: float | None = None
    pretax_income: float | None = None
    tax_provision: float | None = None
    net_income: float | None = None
    net_income_common_stockholders: float | None = None
    diluted_eps: float | None = None
    basic_eps: float | None = None
    diluted_average_shares: float | None = None
    basic_average_shares: float | None = None
    total_expenses: float | None = None
    normalized_income: float | None = None
    normalized_ebitda: float | None = None


class BalanceSheetPeriodModel(BaseModel):
    period_end: str
    total_assets: float | None = None
    total_current_assets: float | None = None
    cash_and_cash_equivalents: float | None = None
    cash_equivalents: float | None = None
    short_term_investments: float | None = None
    accounts_receivable: float | None = None
    inventory: float | None = None
    total_non_current_assets: float | None = None
    net_ppe: float | None = None
    goodwill_and_intangible_assets: float | None = None
    total_liabilities: float | None = None
    total_current_liabilities: float | None = None
    accounts_payable: float | None = None
    current_debt: float | None = None
    total_non_current_liabilities: float | None = None
    long_term_debt: float | None = None
    total_equity: float | None = None
    common_stock_equity: float | None = None
    retained_earnings: float | None = None
    treasury_shares_number: float | None = None
    ordinary_shares_number: float | None = None
    total_debt: float | None = None
    net_debt: float | None = None
    working_capital: float | None = None
    invested_capital: float | None = None
    tangible_book_value: float | None = None


class CashFlowPeriodModel(BaseModel):
    period_end: str
    operating_cash_flow: float | None = None
    net_income_from_continuing_operations: float | None = None
    depreciation_and_amortization: float | None = None
    stock_based_compensation: float | None = None
    change_in_working_capital: float | None = None
    change_in_receivables: float | None = None
    change_in_inventory: float | None = None
    change_in_payables: float | None = None
    investing_cash_flow: float | None = None
    capital_expenditure: float | None = None
    purchase_of_ppe: float | None = None
    sale_of_investment: float | None = None
    purchase_of_investment: float | None = None
    financing_cash_flow: float | None = None
    cash_dividends_paid: float | None = None
    common_stock_dividend_paid: float | None = None
    repurchase_of_capital_stock: float | None = None
    net_common_stock_issuance: float | None = None
    net_issuance_payments_of_debt: float | None = None
    net_long_term_debt_issuance: float | None = None
    long_term_debt_payments: float | None = None
    long_term_debt_issuance: float | None = None
    net_short_term_debt_issuance: float | None = None
    free_cash_flow: float | None = None
    end_cash_position: float | None = None
    beginning_cash_position: float | None = None
    changes_in_cash: float | None = None
    interest_paid: float | None = None
    income_tax_paid: float | None = None


class FinancialStatementModel(BaseModel):
    ticker: str
    statement_type: str  # 'income_statement', 'balance_sheet', 'cash_flow'
    frequency: str  # 'annual', 'quarterly', 'ttm'
    periods: list[IncomeStatementPeriodModel | BalanceSheetPeriodModel | CashFlowPeriodModel]


class IncomeStatementResponseModel(BaseModel):
    ticker: str
    statement_type: str = "income_statement"
    frequency: str  # 'annual', 'quarterly', 'ttm'
    periods: list[IncomeStatementPeriodModel]


class BalanceSheetResponseModel(BaseModel):
    ticker: str
    statement_type: str = "balance_sheet"
    frequency: str  # 'annual', 'quarterly'
    periods: list[BalanceSheetPeriodModel]


class CashFlowResponseModel(BaseModel):
    ticker: str
    statement_type: str = "cash_flow"
    frequency: str  # 'annual', 'quarterly', 'ttm'
    periods: list[CashFlowPeriodModel]


class OptionContractModel(BaseModel):
    contract_symbol: str
    strike: float
    last_price: float | None = None
    bid: float | None = None
    ask: float | None = None
    change: float | None = None
    percent_change: float | None = None
    volume: int | None = None
    open_interest: int | None = None
    implied_volatility: float | None = None
    in_the_money: bool | None = None
    contract_size: str | None = None
    currency: str | None = None
    last_trade_date: str | None = None


class OptionChainModel(BaseModel):
    ticker: str
    expiration_date: str
    underlying_price: float
    calls: list[OptionContractModel]
    puts: list[OptionContractModel]


class OptionExpirationsModel(BaseModel):
    ticker: str
    expirations: list[str]
    count: int


class ATMOptionsModel(BaseModel):
    ticker: str
    expiration_date: str
    underlying_price: float
    atm_strike: float
    call: OptionContractModel | None = None
    put: OptionContractModel | None = None
    nearby_calls: list[OptionContractModel]
    nearby_puts: list[OptionContractModel]


# Earnings Models
class EarningsDateModel(BaseModel):
    earnings_date: str  # ISO format datetime
    eps_estimate: float | None = None
    reported_eps: float | None = None
    surprise_percent: float | None = None


class EarningsDatesResponseModel(BaseModel):
    ticker: str
    earnings_dates: list[EarningsDateModel]
    count: int


class EarningsHistoryItemModel(BaseModel):
    quarter: str  # YYYY-MM-DD
    eps_actual: float | None = None
    eps_estimate: float | None = None
    eps_difference: float | None = None
    surprise_percent: float | None = None
    methodology: str | None = None


class EarningsHistoryResponseModel(BaseModel):
    ticker: str
    history: list[EarningsHistoryItemModel]
    count: int


class EarningsEstimatePeriodModel(BaseModel):
    period: str  # e.g., '0q', '+1q', '0y', '+1y'
    avg_estimate: float | None = None
    low_estimate: float | None = None
    high_estimate: float | None = None
    year_ago_eps: float | None = None
    growth: float | None = None
    currency: str | None = None
    methodology: str | None = None


class EarningsEstimatesResponseModel(BaseModel):
    ticker: str
    estimates: list[EarningsEstimatePeriodModel]
    count: int


# Analyst Models
class PriceTargetsModel(BaseModel):
    current: float | None = None
    high: float | None = None
    low: float | None = None
    mean: float | None = None
    median: float | None = None


class PriceTargetsResponseModel(BaseModel):
    ticker: str
    price_targets: PriceTargetsModel


class RecommendationPeriodModel(BaseModel):
    period: str  # e.g., '0m', '-1m', '-2m', '-3m'
    strong_buy: int
    buy: int
    hold: int
    sell: int
    strong_sell: int
    total: int


class RecommendationsResponseModel(BaseModel):
    ticker: str
    recommendations: list[RecommendationPeriodModel]
    count: int


class UpgradeDowngradeModel(BaseModel):
    date: str  # ISO format datetime
    firm: str
    to_grade: str | None = None
    from_grade: str | None = None
    action: str | None = None  # 'up', 'down', 'init', 'reiterated', etc.
    price_target: float | None = None
    prior_price_target: float | None = None


class UpgradesDowngradesResponseModel(BaseModel):
    ticker: str
    upgrades_downgrades: list[UpgradeDowngradeModel]
    count: int


# ==================== INDEX MODELS ====================


class IndexConstituentModel(BaseModel):
    """Represents a single constituent in an index."""
    rank: int | None = None
    ticker: str
    company: str
    weight: float | None = None  # Percentage weight in the index
    sector: str | None = None
    industry: str | None = None


class IndexInfoModel(BaseModel):
    """Metadata about an index."""
    symbol: str  # e.g., 'NDX', 'SPX', 'DJI'
    name: str  # e.g., 'NASDAQ 100', 'S&P 500', 'Dow Jones Industrial Average'
    description: str | None = None
    currency: str = "USD"
    last_updated: str | None = None  # ISO format date
    constituent_count: int = 0


class IndexConstituentsResponseModel(BaseModel):
    """Response model for index constituents."""
    index: IndexInfoModel
    constituents: list[IndexConstituentModel]
    total_count: int
    data_source: str = "CSV"
