"""
YouBike MCP Server using FastMCP.
Supports both STDIO and Streamable HTTP transport modes.
"""
import sys
import os
import argparse
import asyncio

# Add current directory to path so we can import 'logic'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP
import logic

# Initialize FastMCP
mcp = FastMCP("mcp-tw-youbike")

@mcp.tool()
async def get_youbike_stations(city: str = "Taipei", area: str = None) -> str:
    """
    獲取台灣各城市的 YouBike 站點即時資訊 (車輛數、空位數)。
    Args:
        city: 城市名稱 (預設 Taipei, 支援 Taipei, NewTaipei, Taoyuan, etc.)。
        area: 行政區名稱 (例如：信義區)。
    """
    data = await logic.fetch_youbike_data(city, area)
    return str(data)

@mcp.tool()
async def search_station_by_name(keyword: str, city: str = "Taipei") -> str:
    """
    根據關鍵字搜尋特定站點。
    Args:
        keyword: 站點名稱關鍵字 (例如：台北車站)。
        city: 城市名稱。
    """
    data = await logic.search_stations(keyword, city)
    return str(data)

def main():
    parser = argparse.ArgumentParser(description="Taiwan YouBike MCP Server")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio", help="Transport mode")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (only for http mode)")
    args = parser.parse_args()

    if args.mode == "stdio":
        mcp.run()
    else:
        print(f"Starting FastMCP in streamable-http mode on port {args.port}...", file=sys.stderr)
        mcp.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=args.port,
            path="/mcp"
        )

if __name__ == "__main__":
    main()
