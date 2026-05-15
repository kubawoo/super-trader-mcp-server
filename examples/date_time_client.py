import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def main():
    transport = StreamableHttpTransport(url="http://localhost:8001/mcp")
    client = Client(transport)
    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {', '.join([t.name for t in tools])}")

        time = await client.call_tool("get_current_time")
        date = await client.call_tool("get_current_date")
        print(f"Today is {date.data} and the current time is {time.data}")


if __name__ == "__main__":
    asyncio.run(main())
