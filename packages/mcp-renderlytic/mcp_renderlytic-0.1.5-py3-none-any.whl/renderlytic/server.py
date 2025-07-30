from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import os
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')
# Initialize FastMCP server
mcp = FastMCP("renderlytic")


from dotenv import load_dotenv
load_dotenv()
RENDERLYTIC_API_KEY = os.getenv("RENDERLYTIC_API_KEY")
BASE_URL            = "https://renderlytic-fastapi-692915077423.asia-southeast1.run.app"


@mcp.tool()
async def get_projects() -> Any:
    """ Always start with fetching projects. 
        Fetch all projects belonging to the API‑key owner. 
        It will return lists of projects with their IDs, names, and descriptions."""
    url     = f"{BASE_URL}/api/v1/projects"
    headers = {"X-API-Key": RENDERLYTIC_API_KEY}

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Projects request failed: {resp.status_code} – {resp.text}")

    return {
        "projects": resp.json(),
        "message":  "Projects fetched successfully."
    }


def main():
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()