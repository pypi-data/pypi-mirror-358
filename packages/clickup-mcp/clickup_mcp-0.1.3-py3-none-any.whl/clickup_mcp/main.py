# server.py
from mcp.server.fastmcp import FastMCP
import requests
from utilities import validate_api_token

from typing import Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create an MCP server
mcp = FastMCP("Demo")


# getTask tool
@mcp.tool()
def get_task(taskID: str) -> str:

    """ This tool is capable of retreiving the task details for a specific task ID and return it to the user"""

    # Validate API token
    is_valid, token_or_error = validate_api_token()
    if not is_valid:
        return token_or_error
    
    api_token = token_or_error

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