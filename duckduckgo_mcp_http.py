import json
import urllib3
import requests
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from bs4 import BeautifulSoup

# -------------------------------------------------------------------
#  DISABLE SSL WARNINGS (Windows cert problems)
# -------------------------------------------------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------------------------------------------------------
#  MCP MODELS (Pydantic v2 compatible)
# -------------------------------------------------------------------
class TextContent(BaseModel):
    type: str  # required: MUST be "text"
    text: str

class CallToolResult(BaseModel):
    content: List[TextContent]

# -------------------------------------------------------------------
#  FASTAPI APP
# -------------------------------------------------------------------
app = FastAPI(title="DuckDuckGo MCP HTTP Tool")

# -------------------------------------------------------------------
#  DUCKDUCKGO SEARCH FUNCTION
# -------------------------------------------------------------------
async def duckduckgo_search_tool(params: dict) -> CallToolResult:
    query = params.get("query", "").strip()

    if not query:
        return CallToolResult(
            content=[TextContent(type="text", text="ERROR: No query provided.")]
        )

    search_url = f"https://html.duckduckgo.com/html/?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(
            search_url,
            headers=headers,
            verify=False,     # bypass SSL
            timeout=15
        )
        response.raise_for_status()

    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"HTTP request failed: {str(e)}")]
        )

    # -------------------------------------------------------------------
    # Parse DuckDuckGo HTML
    # -------------------------------------------------------------------
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for result in soup.select("a.result__a"):
        results.append({
            "title": result.get_text(strip=True),
            "url": result.get("href")
        })

    if not results:
        results = [{"title": "No results found.", "url": ""}]

    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=json.dumps(results, indent=2)
            )
        ]
    )

# -------------------------------------------------------------------
#  FASTAPI ROUTE
# -------------------------------------------------------------------
@app.get("/search")
async def search(query: str = Query(..., description="Search query")):
    """
    Example:
    http://127.0.0.1:8000/search?query=python
    """
    return await duckduckgo_search_tool({"query": query})


# -------------------------------------------------------------------
#  RUN COMMAND (DON'T PUT IF __name__ == "__main__")
#  START SERVER USING:
#  uvicorn duckduckgo_mcp_http:app --reload
# -------------------------------------------------------------------
