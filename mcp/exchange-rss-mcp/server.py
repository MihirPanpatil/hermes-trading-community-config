#!/home/openclaw/angel-one-mcp-venv/bin/python
"""Read-only NSE/BSE RSS feeds exposed as an MCP server."""
import html
import re
import subprocess
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from defusedxml import ElementTree as ET
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("nse-bse-rss")

FEEDS = {
    "nse": {
        "announcements": "https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml",
        "financial_results": "https://nsearchives.nseindia.com/content/RSS/Financial_Results.xml",
        "board_meetings": "https://nsearchives.nseindia.com/content/RSS/Board_Meetings.xml",
        "corporate_actions": "https://nsearchives.nseindia.com/content/RSS/Corporate_action.xml",
    },
    "bse": {
        "announcements": "https://www.bseindia.com/data/xml/announcements.xml",
        "notices": "https://www.bseindia.com/data/xml/notices.xml",
        "sensex": "https://www.bseindia.com/data/xml/sensexrss.xml",
        "financial_results": "https://www.bseindia.com/Data/XML/FinancialResultsFeed.xml",
        "corporate_actions": "https://www.bseindia.com/Data/XML/CorpActionFeed.xml",
    },
    "indian_business": {
        "livemint_markets": "https://www.livemint.com/rss/markets",
        "moneycontrol_top": "https://www.moneycontrol.com/rss/MCtopnews.xml",
        "economic_times_markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "business_standard_finance": "https://www.business-standard.com/rss/finance-103.rss",
    },
    "global_markets": {
        "yahoo_finance": "https://www.yahoo.com/news/rss/finance",
        "investing_markets": "https://www.investing.com/rss/news_25.rss",
        "investing_india": "https://in.investing.com/rss/news_25.rss",
        "cnbc_markets": "https://search.cnbc.com/rs/search/view.html?partnerId=2000&keywords=markets&sort=date&output=rss",
    },
    "fallback_markets": {
        "google_finance_india": "https://news.google.com/rss/search?q=Indian+stock+market+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
        "google_global_markets": "https://news.google.com/rss/search?q=global+markets+Fed+oil+when:1d&hl=en-US&gl=US&ceid=US:en",
    },
}


def _text(node: Any) -> str:
    if node is None:
        return ""
    return html.unescape("".join(node.itertext()).strip())


def _fetch(url: str, limit: int) -> list[dict[str, Any]]:
    host = urlsplit(url).netloc.lower()
    user_agent = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 Chrome/131 Safari/537.36"
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
    }
    if "bseindia.com" in host:
        headers["Referer"] = "https://www.bseindia.com/"
    last_error = None
    for attempt in range(2):
        try:
            result = subprocess.run(
                ["curl", "-L", "--retry", "1", "--retry-delay", "1", "--retry-all-errors",
                 "--connect-timeout", "5", "--max-time", "15", "--silent", "--show-error",
                 "-A", user_agent, "-H", "Accept: application/rss+xml, application/xml, text/xml, */*", url],
                capture_output=True, check=True, timeout=20,
            )
            raw = result.stdout
            # Some publishers emit bare ampersands/control characters in XML.
            raw = re.sub(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", b"", raw)
            raw = re.sub(rb"&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)", b"&amp;", raw)
            root = ET.fromstring(raw)
            break
        except Exception as exc:
            last_error = exc
            if attempt < 1:
                time.sleep(0.5)
    else:
        raise last_error
    channel = root.find("channel")
    if channel is None:
        return []
    items = []
    for item in channel.findall("item")[:limit]:
        link = _text(item.find("link"))
        items.append({
            "title": _text(item.find("title")),
            "link": link,
            "published": _text(item.find("pubDate")) or _text(item.find("date")),
            "description": _text(item.find("description")),
            "source_host": host,
        })
    return items


@mcp.tool()
def list_feeds() -> dict[str, Any]:
    """List the configured official NSE and BSE RSS feeds."""
    return {"feeds": FEEDS}


@mcp.tool()
def get_exchange_news(exchange: str = "all", feed: str = "all", limit: int = 10) -> dict[str, Any]:
    """Read recent RSS items from all selected feeds; read-only.

    By default, query every configured feed across every category. Each feed is
    isolated: an unavailable or malformed endpoint is returned with an error,
    while successful feeds are still included. The caller should use the
    successful feeds as coverage and report failed feeds explicitly.

    exchange: nse, bse, indian_business, global_markets, fallback_markets, or all.
    feed: a feed name, or all. Use all to aggregate every configured feed.
    limit: maximum items per feed, capped at 50.
    """
    exchange = exchange.lower().strip()
    if exchange not in {"nse", "bse", "indian_business", "global_markets", "fallback_markets", "all"}:
        return {"status": False, "error": "invalid exchange/category"}
    limit = max(1, min(int(limit), 50))
    categories = ("nse", "bse", "indian_business", "global_markets", "fallback_markets") if exchange == "all" else (exchange,)
    jobs = [(category, name, url) for category in categories for name, url in FEEDS[category].items() if feed == "all" or name == feed]
    results = []
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(jobs)))) as pool:
        futures = {pool.submit(_fetch, url, limit): (category, name, url) for category, name, url in jobs}
        for future in as_completed(futures):
            category, name, url = futures[future]
            try:
                items = future.result()
                results.append({"category": category, "feed": name, "url": url, "items": items})
            except Exception as exc:
                results.append({"category": category, "feed": name, "url": url, "items": [], "error": str(exc)})
    # Deduplicate syndicated stories by normalized title, retaining source metadata.
    seen: dict[str, dict[str, Any]] = {}
    for result in results:
        unique = []
        for item in result["items"]:
            key = " ".join(item.get("title", "").lower().split())
            if key and key in seen:
                continue
            if key:
                seen[key] = item
            unique.append(item)
        result["items"] = unique
    results.sort(key=lambda r: (r["category"], r["feed"]))
    return {"status": True, "retrieved_at": datetime.now(timezone.utc).isoformat(), "feeds": results}


if __name__ == "__main__":
    mcp.run(transport="stdio")
