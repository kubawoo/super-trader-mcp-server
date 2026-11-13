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
        price = await client.call_tool("get_current_stock_price", {"ticker": "AAPL"})
        print(f"AAPL current price: ${get_data(price):.2f}")


if __name__ == "__main__":
    asyncio.run(main())