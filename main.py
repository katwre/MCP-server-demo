from fastmcp import FastMCP
import requests
import re

mcp = FastMCP("Demo 🚀")

def scrape_web_raw(url: str) -> str:
    """Plain Python function: fetch page content as markdown via Jina Reader."""
    url = url.strip()

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    reader_url = f"https://r.jina.ai/{url}"

    headers = {"User-Agent": "mcp-scraper/1.0"}
    resp = requests.get(reader_url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text

@mcp.tool
def scrape_web(url: str) -> str:
    """MCP tool wrapper around scrape_web_raw."""
    return scrape_web_raw(url)

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b




@mcp.tool
def count_word_on_page(url: str, word: str) -> int:
    """
    Count whole-word occurrences of `word` (case-insensitive)
    on a web page using Jina Reader content.
    """
    text = scrape_web_raw(url)
    pattern = rf"\b{re.escape(word)}\b"
    return len(re.findall(pattern, text, flags=re.IGNORECASE))

if __name__ == "__main__":
    mcp.run()
