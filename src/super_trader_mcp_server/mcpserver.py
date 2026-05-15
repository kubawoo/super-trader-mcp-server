import importlib

from fastmcp import FastMCP
from mcp.types import Request
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from super_trader_mcp_server.prompts import register_prompts
from super_trader_mcp_server.resources import register_resources
from super_trader_mcp_server.tools import register_tools

server_version = importlib.metadata.version("super_trader_mcp_server")
mcp = FastMCP(
    "SuperTrader",
    instructions="Set of tools, resources, and prompts useful for home-grown traders",
    website_url="https://github.com/kubawoo/super-trader-mcp-server",
    version=server_version,
)

register_resources()
register_prompts()
register_tools()


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK\n")


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],
    )
]


def start_server():
    mcp.run(transport="http", middleware=middleware)
