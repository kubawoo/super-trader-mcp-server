"""
Generic index data loader for CSV-based index constituent files.

Supports loading index data from CSV files in the data/ directory.
Expected CSV format: Rank, Ticker, Company, Weight (percentage)
Additional columns like Sector, Industry are optional.

For Polish indexes (WIG20, mWIG40, sWIG80), alternative column names are supported:
- GPW_Name instead of Company
- ISIN column is parsed but not stored in the model
"""

import csv
import os
from pathlib import Path
from typing import Optional

from super_trader.models import IndexConstituentModel, IndexInfoModel, IndexConstituentsResponseModel


# Registry of known indexes - maps symbol to metadata
INDEX_REGISTRY: dict[str, IndexInfoModel] = {
    "NDX": IndexInfoModel(
        symbol="NDX",
        name="NASDAQ 100",
        description="The NASDAQ-100 Index includes 100 of the largest domestic and international non-financial companies listed on the NASDAQ Stock Market.",
        currency="USD",
        last_updated="2024-11-26",
    ),
    "SPX": IndexInfoModel(
        symbol="SPX",
        name="S&P 500",
        description="The S&P 500 Index measures the performance of 500 large companies listed on US stock exchanges.",
        currency="USD",
        last_updated="2024-11-26",
    ),
    "WIG20": IndexInfoModel(
        symbol="WIG20",
        name="WIG20",
        description="The WIG20 is the main index of the Warsaw Stock Exchange, comprising the 20 most liquid companies.",
        currency="PLN",
        last_updated="2024-11-26",
    ),
    "MWIG40": IndexInfoModel(
        symbol="MWIG40",
        name="mWIG40",
        description="The mWIG40 index comprises 40 medium-cap companies listed on the Warsaw Stock Exchange.",
        currency="PLN",
        last_updated="2024-11-26",
    ),
    "SWIG80": IndexInfoModel(
        symbol="SWIG80",
        name="sWIG80",
        description="The sWIG80 index comprises 80 small-cap companies listed on the Warsaw Stock Exchange.",
        currency="PLN",
        last_updated="2024-11-26",
    ),
}

# Mapping from index symbol to CSV filename (without .csv extension)
# This allows symbols like NDX to map to nasdaq100.csv
INDEX_CSV_MAP: dict[str, str] = {
    "NDX": "nasdaq100",
    "SPX": "sp500",
    "WIG20": "wig20",
    "MWIG40": "mwig40",
    "SWIG80": "swig80",
}


def get_data_dir() -> Path:
    """Get the data directory path."""
    # Check for environment variable first (for Docker deployments)
    data_dir_env = os.environ.get("INDEX_DATA_DIR")
    if data_dir_env:
        path = Path(data_dir_env)
        if path.exists():
            return path

    # Fall back to relative path (for local development)
    # Assuming this file is at src/super_trader/utils/index_data.py
    return Path(__file__).parent.parent.parent.parent / "data"


def get_index_csv_path(symbol: str) -> Path:
    """Get the CSV file path for an index symbol."""
    data_dir = get_data_dir()
    symbol_upper = symbol.upper()

    # Check explicit mapping first
    if symbol_upper in INDEX_CSV_MAP:
        csv_path = data_dir / f"{INDEX_CSV_MAP[symbol_upper]}.csv"
        if csv_path.exists():
            return csv_path

    # Try exact match first (e.g., ndx.csv for NDX)
    csv_path = data_dir / f"{symbol.lower()}.csv"
    if csv_path.exists():
        return csv_path

    # Try common naming patterns
    for pattern in [f"{symbol.lower()}.csv", f"{symbol.lower()}_constituents.csv"]:
        csv_path = data_dir / pattern
        if csv_path.exists():
            return csv_path

    # Try to find any CSV that might match
    for csv_file in data_dir.glob("*.csv"):
        if symbol_upper.lower() in csv_file.stem.lower():
            return csv_file

    raise FileNotFoundError(f"No CSV file found for index {symbol} in {data_dir}")


def parse_weight(weight_str: str) -> Optional[float]:
    """Parse weight string (e.g., '13.93%') to float."""
    if not weight_str:
        return None
    weight_str = weight_str.strip()
    if weight_str.endswith("%"):
        weight_str = weight_str[:-1]
    try:
        return float(weight_str)
    except ValueError:
        return None


def load_index_constituents(symbol: str) -> IndexConstituentsResponseModel:
    """Load index constituents from CSV file.

    Args:
        symbol: Index symbol (e.g., 'NDX', 'SPX', 'WIG20', 'MWIG40', 'SWIG80')

    Returns:
        IndexConstituentsResponseModel with index info and constituents

    Raises:
        FileNotFoundError: If no CSV file found for the symbol
        ValueError: If CSV format is invalid
    """
    symbol_upper = symbol.upper()

    # Get index info from registry or create default
    index_info = INDEX_REGISTRY.get(symbol_upper, IndexInfoModel(
        symbol=symbol_upper,
        name=symbol_upper,
        description=f"{symbol_upper} Index",
    ))

    # Load CSV
    csv_path = get_index_csv_path(symbol_upper)

    constituents = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Normalize headers to lowercase
        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames] if reader.fieldnames else []

        # Support both 'company' and 'gpw_name' columns for company name
        company_field = None
        if "company" in (reader.fieldnames or []):
            company_field = "company"
        elif "gpw_name" in (reader.fieldnames or []):
            company_field = "gpw_name"

        required_fields = {"ticker", company_field} if company_field else {"ticker"}
        if not required_fields.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV must contain 'ticker' and 'company' (or 'gpw_name') columns. Found: {reader.fieldnames}")

        for row in reader:
            # Skip empty rows
            if not any(row.values()):
                continue

            # Parse rank
            rank = None
            if "rank" in row and row["rank"]:
                try:
                    rank = int(row["rank"])
                except ValueError:
                    pass

            # Parse weight
            weight = None
            if "weight" in row:
                weight = parse_weight(row["weight"])

            # Optional fields
            sector = row.get("sector") if "sector" in row else None
            industry = row.get("industry") if "industry" in row else None

            constituent = IndexConstituentModel(
                rank=rank,
                ticker=row["ticker"].strip().upper(),
                company=row[company_field].strip() if company_field else "Unknown",
                weight=weight,
                sector=sector,
                industry=industry,
            )
            constituents.append(constituent)

    # Update index info with actual count
    index_info.constituent_count = len(constituents)

    return IndexConstituentsResponseModel(
        index=index_info,
        constituents=constituents,
        total_count=len(constituents),
        data_source=f"CSV ({csv_path.name})",
    )


def get_available_indexes() -> list[IndexInfoModel]:
    """Get list of available indexes (from registry and discovered CSV files)."""
    data_dir = get_data_dir()
    available = list(INDEX_REGISTRY.values())

    # Discover additional indexes from CSV files
    for csv_file in data_dir.glob("*.csv"):
        # Try to infer symbol from filename
        stem = csv_file.stem.lower()
        symbol = stem.upper()
        # Skip if already in registry
        if symbol not in INDEX_REGISTRY:
            available.append(IndexInfoModel(
                symbol=symbol,
                name=stem.replace("_", " ").title(),
                description=f"Index from {csv_file.name}",
            ))

    return available


def register_index(symbol: str, name: str, description: str | None = None, currency: str = "USD", last_updated: str | None = None) -> IndexInfoModel:
    """Register a new index in the registry.

    Args:
        symbol: Index symbol (e.g., 'NDX')
        name: Full index name
        description: Optional description
        currency: Currency (default USD)
        last_updated: ISO format date string

    Returns:
        The created IndexInfoModel
    """
    index_info = IndexInfoModel(
        symbol=symbol.upper(),
        name=name,
        description=description,
        currency=currency,
        last_updated=last_updated,
    )
    INDEX_REGISTRY[symbol.upper()] = index_info
    return index_info