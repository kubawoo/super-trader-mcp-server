"""MCP resources for index data."""

from super_trader.mcpserver import mcp
from super_trader.utils.index_data import load_index_constituents, get_index_csv_path


@mcp.resource(
    "index://{symbol}/constituents{?format}",
    mime_type="application/json",
    description="Get index constituents as JSON. Format can be 'json' (default) or 'csv'.",
)
async def get_index_constituents_resource(symbol: str = "", format: str = "json") -> str:
    """Get index constituents as a resource.
    
    Args:
        symbol: Index symbol (e.g., 'NDX', 'SPX')
        format: Output format - 'json' (default) or 'csv'
    
    Returns:
        JSON string of IndexConstituentsResponseModel or CSV string of constituents
    """
    result = load_index_constituents(symbol)
    
    if format.lower() == "csv":
        # Return CSV format
        import io
        import csv as csv_module
        
        output = io.StringIO()
        writer = csv_module.writer(output)
        writer.writerow(["Rank", "Ticker", "Company", "Weight", "Sector", "Industry"])
        
        for c in result.constituents:
            writer.writerow([
                c.rank or "",
                c.ticker,
                c.company,
                f"{c.weight}%" if c.weight else "",
                c.sector or "",
                c.industry or "",
            ])
        
        return output.getvalue()
    
    # Return JSON (model_dump_json)
    return result.model_dump_json(indent=2)


@mcp.resource(
    "index://{symbol}/constituents.csv",
    mime_type="text/csv",
    description="Get index constituents as raw CSV file.",
)
async def get_index_constituents_csv(symbol: str = "") -> str:
    """Get index constituents as raw CSV file content.
    
    Args:
        symbol: Index symbol (e.g., 'NDX', 'SPX')
    
    Returns:
        Raw CSV content from the data file
    """
    csv_path = get_index_csv_path(symbol)
    return csv_path.read_text(encoding="utf-8")


@mcp.resource(
    "index://list",
    mime_type="application/json",
    description="List all available indexes with metadata.",
)
async def list_indexes_resource() -> str:
    """List all available indexes as a resource.
    
    Returns:
        JSON array of IndexInfoModel objects
    """
    from super_trader.utils.index_data import get_available_indexes
    indexes = get_available_indexes()
    import json
    return json.dumps([idx.model_dump() for idx in indexes], indent=2)