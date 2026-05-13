from pydantic import BaseModel


class TopHoldingModel(BaseModel):
    ticker: str
    name: str
    pct: float