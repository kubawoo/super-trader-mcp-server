import asyncio
import json

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


def get_data(result):
    """Extract data from CallToolResult, handling RootModel wrapper."""
    data = result.data
    if hasattr(data, "root"):
        return data.root
    return data


async def main():
    transport = StreamableHttpTransport(url="http://localhost:8000/mcp")
    client = Client(transport)
    async with client:
        # Test get_index_constituents tool
        print("=== get_index_constituents (NDX) ===")
        result = await client.call_tool("get_index_constituents", {"symbol": "NDX"})
        data = get_data(result)
        print(f"Index: {data.index.symbol} - {data.index.name}")
        print(f"Constituents: {data.total_count}")
        for c in data.constituents[:10]:
            weight = f"{c.weight:.2f}%" if c.weight else "N/A"
            print(f"  {c.rank:3d}: {c.ticker:6s} - {c.company:40s} ({weight})")
        print()
        
        # Test list_available_indexes tool
        print("=== list_available_indexes ===")
        result = await client.call_tool("list_available_indexes", {})
        indexes = get_data(result)
        for idx in indexes:
            print(f"  {idx.symbol}: {idx.name} ({idx.constituent_count} constituents)")
        print()
        
        # Test index constituents resource (JSON)
        print("=== index://NDX/constituents (JSON resource) ===")
        resource = await client.read_resource("index://NDX/constituents?format=json")
        print(f"Resource text length: {len(resource[0].text)} chars")
        print()
        
        # Test index constituents resource (CSV)
        print("=== index://NDX/constituents (CSV resource) ===")
        resource = await client.read_resource("index://NDX/constituents?format=csv")
        lines = resource[0].text.split('\n')
        for line in lines[:6]:
            print(line)
        print("...")
        print()
        
        # Test raw CSV resource
        print("=== index://NDX/constituents.csv (raw CSV) ===")
        resource = await client.read_resource("index://NDX/constituents.csv")
        lines = resource[0].text.split('\n')
        for line in lines[:6]:
            print(line)
        print("...")
        print()
        
        # Test list indexes resource
        print("=== index://list (resource) ===")
        resource = await client.read_resource("index://list")
        print(resource[0].text)


if __name__ == "__main__":
    asyncio.run(main())