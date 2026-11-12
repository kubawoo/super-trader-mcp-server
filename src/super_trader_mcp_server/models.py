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
