"""HTTP helpers that work in local Python and Pyodide/Stlite."""

from __future__ import annotations

import json
from typing import Any

from src.config.runtime import is_browser_runtime

_LOADING_OVERLAY_ID = "inventory-copilot-loading-overlay"


def _use_sync_browser_http() -> bool:
    """True when Pyodide's JS runtime is available (never use urllib there)."""
    if is_browser_runtime():
        return True
    try:
        from js import XMLHttpRequest  # noqa: F401
    except ImportError:
        return False
    return True


def post_json(
    url: str,
    payload: dict[str, Any],
    timeout: float = 120,
    *,
    loading_message: str | None = None,
) -> dict[str, Any]:
    """POST JSON and return a parsed JSON response."""
    if _use_sync_browser_http():
        return _post_json_pyodide(url, payload, loading_message=loading_message)
    return _post_json_urllib(url, payload, timeout)


def _post_json_urllib(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    import urllib.error
    import urllib.request

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def _resolve_browser_url(url: str) -> str:
    """Resolve relative API paths against the current browser origin."""
    if url.startswith(("http://", "https://")):
        return url
    import js

    origin = str(js.location.origin).rstrip("/")
    path = url if url.startswith("/") else f"/{url}"
    return f"{origin}{path}"


def _show_browser_loading(message: str) -> None:
    from js import Function

    show = Function.new(
        "message",
        f"""
        () => {{
            let el = document.getElementById("{_LOADING_OVERLAY_ID}");
            if (!el) {{
                el = document.createElement("div");
                el.id = "{_LOADING_OVERLAY_ID}";
                el.style.cssText = [
                    "position:fixed",
                    "inset:0",
                    "background:rgba(255,255,255,0.92)",
                    "z-index:99999",
                    "display:flex",
                    "align-items:center",
                    "justify-content:center",
                    "padding:2rem",
                    "text-align:center",
                    "font:18px/1.5 Inter,system-ui,sans-serif",
                    "color:#0f172a",
                ].join(";");
                document.body.appendChild(el);
            }}
            el.innerHTML = "<div><strong>" + message + "</strong><br><span style='color:#64748b;font-size:14px;'>This usually takes 15–45 seconds.</span></div>";
        }}
        """,
    )
    show(message)


def _hide_browser_loading() -> None:
    from js import Function

    hide = Function.new(
        f"""
        () => {{
            document.getElementById("{_LOADING_OVERLAY_ID}")?.remove();
        }}
        """,
    )
    hide()


def _post_json_pyodide(
    url: str,
    payload: dict[str, Any],
    *,
    loading_message: str | None = None,
) -> dict[str, Any]:
    """Synchronous POST via raw JS XMLHttpRequest (safe inside Streamlit's event loop)."""
    from js import Function

    if loading_message:
        _show_browser_loading(loading_message)

    target_url = _resolve_browser_url(url)
    body = json.dumps(payload)
    try:
        request = Function.new(
            "url",
            "body",
            """
            const xhr = new XMLHttpRequest();
            xhr.open("POST", url, false);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(body);
            return { status: xhr.status, text: xhr.responseText };
            """,
        )
        result = request(target_url, body)
        status = int(result.status)
        response_text = str(result.text)
        if status >= 400:
            raise RuntimeError(f"HTTP {status}: {response_text}")
        return json.loads(response_text)
    finally:
        if loading_message:
            _hide_browser_loading()

