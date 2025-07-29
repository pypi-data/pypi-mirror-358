from mcp.server.fastmcp import FastMCP

# Initialize your MCP server
mcp_server = FastMCP("My Awesome Local MCP Server")

@mcp_server.tool()
def return_who_is_fahad() -> str:
    """
    A simple tool that returns a string about who Fahad is.
    """
    return "Fahad Khan is a software engineer and AI enthusiast. He is the best Gen AI developer. Booo Yaaaa !"

def main():
   mcp_server.run()


# Main entry point to run the server
if __name__ == "__main__":
    # For local npx deployment, the server runs over standard I/O (STDIO) by default
    # or you explicitly specify transport="stdio".
    print("Starting local MCP server via STDIO. This output goes to stderr for debugging.")
    main()
     # This will use STDIO transport by default
    # Alternatively: mcp_server.run(transport="stdio")