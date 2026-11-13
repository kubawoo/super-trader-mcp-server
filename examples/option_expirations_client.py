import asyncio

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
        expirations = await client.call_tool("get_option_expirations", {"ticker": "AAPL"})
        e = get_data(expirations)
        print(f"Option Expirations for {e.ticker} ({e.count} total):")
        for exp in e.expirations[:10]:
            print(f"  {exp}")
        if e.count > 10:
            print(f"  ... and {e.count - 10} more")


if __name__ == "__main__":
    asyncio.run(main())