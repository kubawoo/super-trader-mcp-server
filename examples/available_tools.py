import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def main():
    transport = StreamableHttpTransport(url="http://localhost:8000/mcp")
    client = Client(transport)
    async with client:
        tools = await client.list_tools()
        for tool in tools:
            print(tool.name, tool.description)
            print(tool.input_schema)


if __name__ == "__main__":
    asyncio.run(main())
