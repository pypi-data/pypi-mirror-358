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



@mcp.tool()
async def get_unrendered_blogs(project_id: str) -> Any:
    """
    Fetch all blogs for a given project that have not yet been rendered.
    
    Args:
      project_id: UUID of the project to fetch blogs from.

    Returns:
      A dict with:
        - blogs: list of blog objects where `isrendered` is False
        - message: status message
    """
    url = f"{BASE_URL}/api/v1/projects/{project_id}/blogs"
    headers = {"X-API-Key": RENDERLYTIC_API_KEY}

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Blogs request failed: {resp.status_code} – {resp.text}")

    all_blogs = resp.json()
    # Filter to only those not yet rendered
    unrendered = [b for b in all_blogs if not b.get("isrendered", False)]

    return {
        "blogs": unrendered,
        "message":  f"Fetched {len(unrendered)} unrendered blog(s)."
    }


@mcp.tool()
async def get_user_renderlytic_profile() -> Any:
    """
    Fetch the profile of the API‑key owner.
    
    Returns:
      A dict with:
        - profile: the user profile object
        - message: status message
    """
    url = f"{BASE_URL}/api/v1/profile"
    headers = {"X-API-Key": RENDERLYTIC_API_KEY}

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Profile request failed: {resp.status_code} – {resp.text}")

    return {
        "profile": resp.json(),
        "message": "Profile fetched successfully."
    }


@mcp.tool()
async def mark_blog_rendered(project_id: str, blog_id: str) -> Any:
    """
    Mark a specific blog as rendered.
    
    Args:
      project_id: UUID of the project.
      blog_id: UUID of the blog to mark rendered.

    Returns:
      A dict with:
        - message: confirmation message
        - status_code: HTTP status code from the API
    """
    url = f"{BASE_URL}/api/v1/projects/{project_id}/blogs/{blog_id}/render"
    headers = {"X-API-Key": RENDERLYTIC_API_KEY}

    resp = requests.put(url, headers=headers)
    if resp.status_code not in (200, 204):
        raise Exception(f"Mark rendered failed: {resp.status_code} – {resp.text}")

    return {
        "message": f"Blog {blog_id} marked as rendered.",
        "status_code": resp.status_code
    }


def main():
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()