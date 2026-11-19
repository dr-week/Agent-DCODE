"""
Phase 3: Crawl4AI Web-to-Markdown Research Tool Adapter (unclecode/crawl4ai).
Converts live documentation, GitHub issues, and web pages into clean LLM-ready Markdown
with a zero-dependency stdlib HTML-to-Markdown fallback.
"""

import asyncio
import html
import re
import urllib.request
from typing import Any, Dict
from dcode.framework.core.tool_decorator import tool

try:
    from crawl4ai import AsyncWebCrawler  # type: ignore

    HAS_CRAWL4AI = True
except ImportError:
    AsyncWebCrawler = None  # type: ignore
    HAS_CRAWL4AI = False


def html_to_markdown(raw_html: str) -> str:
    """Convert raw HTML string into clean, readable Markdown without external dependencies."""
    cleaned = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", "", raw_html, flags=re.DOTALL | re.I)
    cleaned = re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n# \1\n", cleaned, flags=re.DOTALL | re.I)
    cleaned = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n", cleaned, flags=re.DOTALL | re.I)
    cleaned = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n", cleaned, flags=re.DOTALL | re.I)
    cleaned = re.sub(r"<li[^>]*>(.*?)</li>", r"\n- \1", cleaned, flags=re.DOTALL | re.I)
    cleaned = re.sub(r"<a[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", r"[\2](\1)", cleaned, flags=re.I)
    cleaned = re.sub(r"<(p|div|br|tr)[^>]*>", "\n", cleaned, flags=re.I)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    text = html.unescape(cleaned)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


@tool(name="crawl_url", description="Crawl a live URL or documentation page into clean LLM-ready Markdown")
def crawl_url(url: str, max_chars: int = 8000) -> Dict[str, Any]:
    """Fetch and convert a web page to Markdown via Crawl4AI or stdlib fallback."""
    if HAS_CRAWL4AI and AsyncWebCrawler is not None:
        try:

            async def _run() -> str:
                async with AsyncWebCrawler() as crawler:
                    res = await crawler.arun(url=url)
                    return str(getattr(res, "markdown", "") or "")

            md = asyncio.run(_run())
            if md:
                return {"success": True, "url": url, "backend": "crawl4ai", "markdown": md[:max_chars]}
        except Exception:
            pass

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Agent-DCODE/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        md = html_to_markdown(raw)
        return {"success": True, "url": url, "backend": "stdlib-markdown", "markdown": md[:max_chars]}
    except Exception as exc:
        return {"success": False, "url": url, "backend": "stdlib-markdown", "error": str(exc)}
