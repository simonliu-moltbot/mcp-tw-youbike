from mcp.server import Server
import sys

try:
    s = Server("test")
    if hasattr(s, "list_tools"):
        print("Server has list_tools")
    else:
        print("Server does NOT have list_tools")
except Exception as e:
    print(e)
