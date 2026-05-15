from pydantic import BaseModel


class TopHoldingModel(BaseModel):
    ticker: str
    name: str
    pct: float


class StockInfoModel(BaseModel):
    ticker: str
    sector: str
    industry: str
    market_cap: int
    employees: int
