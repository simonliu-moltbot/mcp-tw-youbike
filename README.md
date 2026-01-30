# Taiwan YouBike 2.0 MCP Server

An MCP server that provides real-time YouBike 2.0 station data in Taipei City.
Uses official Open Data from Taipei City Government.

## Features
- **Search Stations**: Find stations by name, address, or district (e.g., "Taipei 101", "Daan").
- **Nearby Stations**: Find stations near a specific location (Latitude/Longitude).
- **Real-time Data**: Returns available bikes and empty spaces instantly.

## Setup

### Prerequisites
- Python 3.10 or higher
- `uv` or `pip`

### Installation

1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd mcp-tw-youbike
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Configuration

### Claude Desktop
Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "youbike": {
      "command": "/absolute/path/to/mcp-tw-youbike/.venv/bin/python",
      "args": ["/absolute/path/to/mcp-tw-youbike/src/server.py"]
    }
  }
}
```

### Dive
Configure the server with the following settings:

- **Type**: `stdio`
- **Command**: `/absolute/path/to/mcp-tw-youbike/.venv/bin/python`
- **Args**: `/absolute/path/to/mcp-tw-youbike/src/server.py`

## License
MIT
