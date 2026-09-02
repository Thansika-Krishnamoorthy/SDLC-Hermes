"""Optional mocked UX smoke. Not the agent-driven Browser loop."""

from __future__ import annotations

import socket
import threading
from collections.abc import AsyncIterator

import pytest
import uvicorn

from app.config import settings
from app.main import app
from tools.ux_drive import STATE_JS_PATH
from tools.ux_drive.gallery import add_screenshot, ensure_run_dir

pytestmark = pytest.mark.e2e

pytest.importorskip("playwright.sync_api")

ROUND_REPLY = """Here is the first round.

Q1. Who is the primary user?
1. Operations
2. HR
3. Other
"""


async def _scripted_stream(_messages: list[dict[str, str]]) -> AsyncIterator[str]:
    for chunk in (ROUND_REPLY[:40], ROUND_REPLY[40:]):
        yield chunk


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


@pytest.fixture
def ux_server(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "browse_root", tmp_path)
    (tmp_path / "demo-app").mkdir()
    monkeypatch.setattr("app.main.stream_chat", _scripted_stream)
    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(80):
        if server.started:
            break
        thread.join(0.05)
    assert server.started
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


def test_mocked_setup_state_and_gallery(ux_server, tmp_path, monkeypatch):
    from playwright.sync_api import sync_playwright

    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
    except Exception as exc:
        pytest.skip(f"Playwright Chromium is not installed: {exc}")

    monkeypatch.setattr("tools.ux_drive.gallery.ARTIFACTS_ROOT", tmp_path / "ux")
    run_dir = ensure_run_dir("e2e-smoke")
    js = STATE_JS_PATH.read_text(encoding="utf-8")
    page = browser.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    try:
        page.goto(ux_server, wait_until="domcontentloaded")
        page.wait_for_selector("#stage-stepper li.is-active")
        state = page.evaluate(js)
        assert state["stage"] == "setup"
        assert "Business Requirement Analysis" in (state["skill"] or "")
        shot = tmp_path / "setup.png"
        page.screenshot(path=str(shot))
        dest = add_screenshot(run_dir, "setup-empty", shot)
        assert dest.exists()
        width = page.locator("#chat-stage").evaluate("el => el.getBoundingClientRect().width")
        assert width >= 0.9 * 1280
    finally:
        browser.close()
        playwright.stop()
