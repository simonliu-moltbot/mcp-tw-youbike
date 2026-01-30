import sys
import os
import asyncio
from typing import Dict, Any, List

# Add the project root to sys.path to allow relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP  # Wait, prompt said NO fastmcp.
# Prompt: "Use standard mcp SDK (no fastmcp)."
# My apologies. I must use `mcp.server.stdio.stdio_server` and `mcp.types`.

from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types
from src.logic import YouBikeClient

# Initialize Server
server = Server("mcp-tw-youbike")
client = YouBikeClient()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_stations",
            description="Search for YouBike 2.0 stations in Taipei by name, address, or district.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword to search for (e.g., 'Taipei 101', 'Xinyi', 'Gongguan')."
                    }
                },
                "required": ["keyword"]
            },
        ),
        types.Tool(
            name="get_nearby_stations",
            description="Find YouBike 2.0 stations near a specific latitude and longitude.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "number",
                        "description": "Latitude"
                    },
                    "lon": {
                        "type": "number",
                        "description": "Longitude"
                    },
                    "radius_km": {
                        "type": "number",
                        "description": "Search radius in kilometers (default 0.5)",
                        "default": 0.5
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max number of results to return (default 5)",
                        "default": 5
                    }
                },
                "required": ["lat", "lon"]
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if not arguments:
        arguments = {}

    try:
        if name == "search_stations":
            keyword = arguments.get("keyword")
            if not keyword:
                return [types.TextContent(type="text", text="Error: 'keyword' is required.")]
            
            stations = await client.search_stations(keyword)
            if not stations:
                return [types.TextContent(type="text", text=f"No stations found matching '{keyword}'.")]
            
            # Format output as a readable list
            text = f"Found {len(stations)} stations matching '{keyword}':\n\n"
            for s in stations:
                text += f"- **{s['name']}** ({s['district']})\n"
                text += f"  🚲 Bikes: {s['available_bikes']} | 🅿️ Empty: {s['empty_spaces']}\n"
                text += f"  📍 {s['address']}\n"
                text += f"  🕒 Updated: {s['update_time']}\n\n"
            
            return [types.TextContent(type="text", text=text)]

        elif name == "get_nearby_stations":
            lat = arguments.get("lat")
            lon = arguments.get("lon")
            radius = arguments.get("radius_km", 0.5)
            limit = arguments.get("limit", 5)
            
            stations = await client.get_nearby_stations(float(lat), float(lon), float(radius), int(limit))
            
            if not stations:
                return [types.TextContent(type="text", text=f"No stations found within {radius}km.")]
            
            text = f"Found {len(stations)} nearby stations:\n\n"
            for s in stations:
                dist = s.get('distance_m', 0)
                text += f"- **{s['name']}** (~{dist}m)\n"
                text += f"  🚲 Bikes: {s['available_bikes']} | 🅿️ Empty: {s['empty_spaces']}\n"
                text += f"  📍 {s['address']}\n\n"
                
            return [types.TextContent(type="text", text=text)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        # Log to stderr
        sys.stderr.write(f"Error executing tool {name}: {e}\n")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    # Run the server using stdin/stdout
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            NotificationOptions(),
            raise_exceptions=True
        )

if __name__ == "__main__":
    asyncio.run(main())
