"""MCP tools for index data."""

from super_trader.mcpserver import mcp
from super_trader.models import (
    IndexConstituentsResponseModel,
    IndexInfoModel,
)
from super_trader.utils.index_data import (
    load_index_constituents,
    get_available_indexes,
    register_index,
)


@mcp.tool
async def get_index_constituents(symbol: str) -> IndexConstituentsResponseModel:
    """Get the constituent stocks for a market index.
    
    Args:
        symbol: Index symbol (e.g., 'NDX' for NASDAQ 100, 'SPX' for S&P 500).
    
    Returns:
        IndexConstituentsResponseModel with:
        - index: Index metadata (symbol, name, description, currency, last_updated, constituent_count)
        - constituents: List of IndexConstituentModel with rank, ticker, company, weight, sector, industry
        - total_count: Number of constituents
        - data_source: Source of the data (CSV filename)
    
    Available indexes: NDX (NASDAQ 100)
    More indexes can be added by placing CSV files in the data/ directory.
    """
    return load_index_constituents(symbol)


@mcp.tool
async def list_available_indexes() -> list[IndexInfoModel]:
    """List all available market indexes with constituent data.
    
    Returns:
        List of IndexInfoModel objects with symbol, name, description, currency, 
        last_updated, and constituent_count for each available index.
    
    Indexes are discovered from the INDEX_REGISTRY and CSV files in the data/ directory.
    """
    return get_available_indexes()


@mcp.tool
async def register_index(
    symbol: str,
    name: str,
    description: str | None = None,
    currency: str = "USD",
    last_updated: str | None = None,
) -> IndexInfoModel:
    """Register a new index in the index registry (for future CSV files).
    
    Args:
        symbol: Index symbol (e.g., 'SPX', 'DJI', 'RUT')
        name: Full index name (e.g., 'S&P 500')
        description: Optional description of the index
        currency: Currency code (default: 'USD')
        last_updated: ISO format date when data was last updated (e.g., '2024-11-26')
    
    Returns:
        The registered IndexInfoModel.
    
    Note: This only registers metadata. The actual constituent data must be provided
    as a CSV file in the data/ directory (e.g., data/spx.csv).
    """
    return register_index(symbol, name, description, currency, last_updated)