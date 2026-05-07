"""Offline tests for thclaws-telegram MCP.

The tests patch httpx so they never call the real Telegram Bot API.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from telegram_mcp.server import (
    TelegramApiError,
    TelegramConfigError,
    _api_url,
    _check_chat_allowed,
    _telegram_result,
    telegram_get_updates,
    telegram_send_document,
    telegram_send_message,
    telegram_send_photo,
)


@pytest.fixture(autouse=True)
def telegram_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "123,-456")


def _fake_response(data: dict) -> AsyncMock:
    response = AsyncMock()
    response.raise_for_status = lambda: None
    response.json = lambda: data
    return response


def test_missing_bot_token_fails_clearly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN")
    with pytest.raises(TelegramConfigError, match="TELEGRAM_BOT_TOKEN"):
        _api_url("sendMessage")


def test_allowed_chat_id_passes() -> None:
    assert _check_chat_allowed("123") == "123"
    assert _check_chat_allowed(-456) == "-456"


def test_disallowed_chat_id_fails() -> None:
    with pytest.raises(TelegramConfigError, match="not allowed"):
        _check_chat_allowed("999")


def test_missing_allowlist_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_ALLOWED_CHAT_IDS")
    with pytest.raises(TelegramConfigError, match="TELEGRAM_ALLOWED_CHAT_IDS"):
        _check_chat_allowed("123")


@pytest.mark.asyncio
async def test_send_message_builds_telegram_request() -> None:
    fake_post = AsyncMock(
        return_value=_fake_response(
            {
                "ok": True,
                "result": {
                    "message_id": 42,
                    "date": 1710000000,
                    "chat": {"id": 123, "type": "private"},
                },
            }
        )
    )

    with patch("telegram_mcp.server.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = fake_post
        out = await telegram_send_message("123", "hello", parse_mode="HTML")

    assert "Telegram message sent" in out
    assert '"message_id": 42' in out
    fake_post.assert_awaited_once()
    _, kwargs = fake_post.await_args
    assert kwargs["json"] == {
        "chat_id": "123",
        "text": "hello",
        "parse_mode": "HTML",
    }
    assert kwargs["timeout"] == 20.0


@pytest.mark.asyncio
async def test_get_updates_filters_to_allowed_chats() -> None:
    fake_post = AsyncMock(
        return_value=_fake_response(
            {
                "ok": True,
                "result": [
                    {
                        "update_id": 1,
                        "message": {
                            "message_id": 10,
                            "date": 1710000000,
                            "chat": {"id": 123, "type": "private"},
                            "from": {"username": "allowed"},
                            "text": "ping",
                        },
                    },
                    {
                        "update_id": 2,
                        "message": {
                            "message_id": 11,
                            "date": 1710000001,
                            "chat": {"id": 999, "type": "private"},
                            "from": {"username": "blocked"},
                            "text": "secret",
                        },
                    },
                ],
            }
        )
    )

    with patch("telegram_mcp.server.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = fake_post
        out = await telegram_get_updates(limit=200, offset=3)

    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["chat_id"] == 123
    assert data[0]["text"] == "ping"
    _, kwargs = fake_post.await_args
    assert kwargs["json"] == {"limit": 100, "timeout": 0, "offset": 3}


@pytest.mark.asyncio
async def test_file_upload_rejects_missing_file() -> None:
    with pytest.raises(TelegramConfigError, match="does not exist"):
        await telegram_send_photo("123", "/tmp/not-a-real-telegram-file.png")


@pytest.mark.asyncio
async def test_file_upload_rejects_url() -> None:
    with pytest.raises(TelegramConfigError, match="local path"):
        await telegram_send_document("123", "https://example.com/report.pdf")


@pytest.mark.asyncio
async def test_send_document_uploads_local_file(tmp_path: Path) -> None:
    doc = tmp_path / "report.txt"
    doc.write_text("hello", encoding="utf-8")
    fake_post = AsyncMock(
        return_value=_fake_response(
            {
                "ok": True,
                "result": {
                    "message_id": 77,
                    "date": 1710000000,
                    "chat": {"id": 123, "type": "private"},
                },
            }
        )
    )

    with patch("telegram_mcp.server.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = fake_post
        out = await telegram_send_document("123", str(doc), caption="report")

    assert "Telegram document sent" in out
    _, kwargs = fake_post.await_args
    assert kwargs["data"] == {"chat_id": "123", "caption": "report"}
    assert "document" in kwargs["files"]


def test_telegram_api_error_surfaces() -> None:
    with pytest.raises(TelegramApiError, match=r"\[400\] Bad Request"):
        _telegram_result(
            {"ok": False, "error_code": 400, "description": "Bad Request"},
            "sendMessage",
        )
