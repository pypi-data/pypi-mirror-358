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

# getTask tool
@mcp.tool()
def get_task(taskID: str) -> str:

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
    return response.text
    
def main():
    mcp.run()

if __name__ == "__main__":
    main()