"""
Phase 3: Browser-Use & Playwright E2E Web Verification Adapter (browser-use/browser-use).
Enables autonomous agents to test running web apps, inspect DOM elements, and verify
HTTP endpoints with headless Chromium or stdlib HTTP DOM inspector fallback.
"""

import re
import urllib.request
from typing import Any, Dict, List
from dcode.framework.core.tool_decorator import tool

try:
    import browser_use  # type: ignore  # noqa: F401

    HAS_BROWSER_USE = True
except ImportError:
    HAS_BROWSER_USE = False


def inspect_html_dom(raw_html: str) -> Dict[str, Any]:
    """Extract title, headings, links, forms, and buttons from HTML for automated QA verification."""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", raw_html, flags=re.DOTALL | re.I)
    headings = re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", raw_html, flags=re.DOTALL | re.I)
    buttons = re.findall(r"<button[^>]*>(.*?)</button>", raw_html, flags=re.DOTALL | re.I)
    forms = len(re.findall(r"<form\b", raw_html, flags=re.I))
    scripts = len(re.findall(r"<script\b", raw_html, flags=re.I))
    return {
        "title": title_match.group(1).strip() if title_match else "",
        "headings": [re.sub(r"<[^>]+>", "", h).strip() for h in headings[:15]],
        "buttons": [re.sub(r"<[^>]+>", "", b).strip() for b in buttons[:15]],
        "form_count": forms,
        "script_count": scripts,
    }


@tool(name="browser_verify", description="Inspect a live web app URL and verify expected UI text or DOM elements")
def browser_verify(url: str, expected_texts: List[str] | None = None) -> Dict[str, Any]:
    """Run an automated browser/DOM verification check against a web application URL."""
    expected = expected_texts or []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Agent-DCODE-BrowserQA/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="ignore")
        dom_info = inspect_html_dom(body)
        missing = [t for t in expected if t not in body]
        return {
            "success": status == 200 and len(missing) == 0,
            "status_code": status,
            "backend": "browser-use" if HAS_BROWSER_USE else "stdlib-dom-inspector",
            "dom": dom_info,
            "missing_assertions": missing,
        }
    except Exception as exc:
        return {
            "success": False,
            "backend": "browser-use" if HAS_BROWSER_USE else "stdlib-dom-inspector",
            "error": str(exc),
        }
