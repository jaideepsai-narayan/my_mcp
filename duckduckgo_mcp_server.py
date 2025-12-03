#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import urllib.parse

# Initialize MCP server
mcp = FastMCP("duckduckgo-tools", json_response=True)

@mcp.tool()
def duckduckgo_search(query: str) -> List[Dict[str, Any]]:
    print(f"[INFO] Received query: {query}")

    encoded_query = urllib.parse.quote(query)
    url = f"https://duckduckgo.com/html/?q={encoded_query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10,verify=False)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return [{"error": str(e)}]

    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    for elem in soup.select(".result"):
        title_el = elem.select_one("a.result__a")
        snippet_el = elem.select_one(".result__snippet")
        if title_el:
            results.append({
                "title": title_el.get_text(strip=True),
                "url": title_el.get("href"),
                "snippet": snippet_el.get_text(strip=True) if snippet_el else ""
            })
        if len(results) >= 10:
            break

    print(f"[INFO] Found {len(results)} results")
    return results

if __name__ == "__main__":
    print("[INFO] Starting MCP server with streamable-http transport (default port 5003)")
    mcp.run(transport="streamable-http")
