#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import urllib.parse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

mcp = FastMCP("duckduckgo-tools", json_response=True)

@mcp.tool()
def duckduckgo_search(query: str) -> List[Dict[str, Any]]:
    print(f"[INFO] Received query: {query}")

    encoded_query = urllib.parse.quote(query)
    url = f"https://duckduckgo.com/lite/?q={encoded_query}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        res = requests.get(url, headers=headers, timeout=10, verify=False)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return [{"error": str(e)}]

    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    # DuckDuckGo Lite uses <a class="result-link">
    for link in soup.select("a.result-link"):
        title = link.get_text(strip=True)
        href = link.get("href")
        results.append({
            "title": title,
            "url": href,
            "snippet": title
        })
        if len(results) >= 10:
            break

    print(f"[INFO] Found {len(results)} results")
    return results

if __name__ == "__main__":
    print("[INFO] Starting MCP server with streamable-http transport (default port 5003)")
    mcp.run(transport="streamable-http")
