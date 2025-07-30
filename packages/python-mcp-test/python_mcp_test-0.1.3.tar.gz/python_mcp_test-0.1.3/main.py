# server.py
from mcp.server.fastmcp import FastMCP
import requests
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def getTask(taskID: str) -> str:

    """ This tool is capable of retreieving the task details for a specific task ID and return it to the user"""

    # Get the API token from environment variables
    api_token = os.getenv("CLICKUP_API_TOKEN")
    
    if not api_token:
        return "Error: CLICKUP_API_TOKEN environment variable not set"
    
    url = f"https://api.clickup.com/api/v2/task/{taskID}"

    headers = {
        "accept": "application/json",
        "Authorization": api_token
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.text

def main():
    """Main entry point for the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()