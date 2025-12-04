#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import urllib.parse
import json

# Initialize MCP server
mcp = FastMCP("duckduckgo-tools", json_response=True)

# @mcp.tool()
def weather_search(query: str) -> List[Dict[str, Any]]:
    print(f"[INFO] Received Location: {query}")
    
    encoded_query=query
    
    url=f'https://geocoding-api.open-meteo.com/v1/search?name={encoded_query}&count=1'
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10,verify=False)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return [{"error": str(e)}]

    soup = BeautifulSoup(res.text, "html.parser")
    print(soup)
    data = json.loads(str(soup))

    # extract fields
    city = data["results"][0]["name"]
    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]
    print(city,lat,lon)
    return (city,lat,lon)
    # return [{"html": str(soup)}]
    
@mcp.tool()
def weather_details(query)-> List[Dict[str, Any]]:
# def weather_details(lat:float,lon:floa)-> List[Dict[str, Any]]:
    # print(f"[INFO] Received latitude & longitude: {lat}&{lon}")

    city,lat,lon=weather_search(query)
    print(f"[INFO] Received latitude & longitude: {lat}&{lon}")
    
    url=f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,rain,weather_code'
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10,verify=False)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return [{"error": str(e)}]

    soup = BeautifulSoup(res.text, "html.parser")
    print(soup)
    
    return [{"html": str(soup)}]

if __name__ == "__main__":
    print("[INFO] Starting MCP server with streamable-http transport (default port 5003)")
    mcp.run(transport="streamable-http")
