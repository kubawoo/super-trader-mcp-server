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
        news = await client.call_tool("get_company_news", {"ticker": "AAPL"})
        data = get_data(news)
        print(f"AAPL Latest News ({len(data)} items):")
        for item in data[:5]:
            print(f"  - {item.title} ({item.publisher})")
            print(f"    {item.link}")


if __name__ == "__main__":
    asyncio.run(main())