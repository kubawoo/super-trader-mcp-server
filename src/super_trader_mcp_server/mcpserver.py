from fastmcp import FastMCP
from mcp.types import Request

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

mcp = FastMCP(
    "SuperTrader",
    instructions="Set of tools and prompts useful for home-grown traders",
    website_url="https://github.com/kubawoo/super-trader-mcp-server",
    version="0.1.0",
)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK\n")


from super_trader_mcp_server.tools import register_tools

register_tools()

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "mcp-session-id"
        ],  # Fixes "Missing session ID" in MCP Inspector
    )
]


@mcp.prompt
def ask_about_stock_price(company: str) -> str:
    """Generates a user message asking for a current price of a stock."""
    return f"What is the current price of '{company}'?"


def start_server():
    mcp.run(transport="http", middleware=middleware)
