"""Unit tests for browser-safe HTTP helpers."""

from unittest.mock import MagicMock, patch

import pytest

from src.utils import browser_http


def test_post_json_uses_urllib_locally(monkeypatch):
    monkeypatch.delenv("STLITE_BROWSER", raising=False)

    with patch.object(browser_http, "_use_sync_browser_http", return_value=False):
        with patch.object(browser_http, "_post_json_urllib", return_value={"ok": True}) as mock_urllib:
            result = browser_http.post_json("http://localhost/api/summary", {"model": "gpt-4o-mini"})

    assert result == {"ok": True}
    mock_urllib.assert_called_once()


def test_post_json_uses_js_function_in_browser():
    mock_result = MagicMock()
    mock_result.status = 200
    mock_result.text = '{"summary":"xhr summary"}'

    mock_function = MagicMock()
    mock_function.new.return_value = MagicMock(return_value=mock_result)
    mock_js = MagicMock(Function=mock_function)

    with patch.object(browser_http, "_use_sync_browser_http", return_value=True):
        with patch.dict("sys.modules", {"js": mock_js}):
            result = browser_http.post_json("/api/summary", {"model": "gpt-4o-mini"})

    assert result == {"summary": "xhr summary"}
    mock_function.new.assert_called_once()
    request = mock_function.new.return_value
    request.assert_called_once()


def test_post_json_js_http_error():
    mock_result = MagicMock()
    mock_result.status = 502
    mock_result.text = '{"error":"OpenAI request failed"}'

    mock_function = MagicMock()
    mock_function.new.return_value = MagicMock(return_value=mock_result)
    mock_js = MagicMock(Function=mock_function)

    with patch.object(browser_http, "_use_sync_browser_http", return_value=True):
        with patch.dict("sys.modules", {"js": mock_js}):
            with pytest.raises(RuntimeError, match="HTTP 502"):
                browser_http.post_json("/api/summary", {"model": "gpt-4o-mini"})


def test_post_json_prefers_js_runtime_even_without_browser_flag():
    mock_result = MagicMock()
    mock_result.status = 200
    mock_result.text = '{"summary":"ok"}'

    mock_function = MagicMock()
    mock_function.new.return_value = MagicMock(return_value=mock_result)
    mock_js = MagicMock(Function=mock_function)

    with patch.object(browser_http, "is_browser_runtime", return_value=False):
        with patch.dict("sys.modules", {"js": mock_js}):
            result = browser_http.post_json("/api/summary", {"model": "gpt-4o-mini"})

    assert result == {"summary": "ok"}


def test_post_json_resolves_relative_urls():
    mock_result = MagicMock()
    mock_result.status = 200
    mock_result.text = '{"summary":"xhr summary"}'

    mock_function = MagicMock()
    mock_function.new.return_value = MagicMock(return_value=mock_result)
    mock_window = MagicMock()
    mock_window.location.origin = "https://example.vercel.app"
    mock_js = MagicMock(Function=mock_function, location=mock_window.location)

    with patch.object(browser_http, "_use_sync_browser_http", return_value=True):
        with patch.dict("sys.modules", {"js": mock_js}):
            result = browser_http.post_json("/api/summary", {"model": "gpt-4o-mini"})

    assert result == {"summary": "xhr summary"}
    request = mock_function.new.return_value
    request.assert_called_once_with("https://example.vercel.app/api/summary", '{"model": "gpt-4o-mini"}')


def test_openai_proxy_uses_browser_post_json(monkeypatch):
    monkeypatch.setenv("STLITE_BROWSER", "1")
    from src.config.settings import get_settings
    from src.services.ai_service import generate_management_summary

    get_settings.cache_clear()

    with patch.object(browser_http, "is_browser_runtime", return_value=True):
        with patch(
            "src.services.ai_service.post_json",
            return_value={"summary": "# Proxy Summary\n\nGenerated in browser."},
        ) as mock_post:
            text = generate_management_summary(
                {"total_inventory_value": 1000},
                [],
                {"recommended_count": 1, "total_net_benefit": 250},
                {"candidate_count": 2, "total_recovery": 500},
                provider="openai",
            )

    assert "Proxy Summary" in text
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "/api/summary"

    get_settings.cache_clear()


def test_openai_proxy_does_not_surface_asyncio_error(monkeypatch):
    monkeypatch.setenv("STLITE_BROWSER", "1")
    from src.config.settings import get_settings
    from src.services.ai_service import AISummaryError, generate_management_summary

    get_settings.cache_clear()

    with patch.object(browser_http, "is_browser_runtime", return_value=True):
        with patch(
            "src.services.ai_service.post_json",
            side_effect=RuntimeError("HTTP 404: not found"),
        ):
            with pytest.raises(AISummaryError, match="HTTP 404"):
                generate_management_summary({}, [], {}, {}, provider="openai")

    get_settings.cache_clear()
