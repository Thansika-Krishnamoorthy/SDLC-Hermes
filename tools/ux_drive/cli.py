from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from tools.ux_drive import STATE_JS_PATH
from tools.ux_drive.gallery import (
    add_screenshot,
    append_index,
    clear_session,
    ensure_run_dir,
    load_session,
    next_index,
    save_session,
    write_findings,
    write_state,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_state_js() -> str:
    return STATE_JS_PATH.read_text(encoding="utf-8")


def _require_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is not installed. pip install playwright && playwright install chromium"
        ) from exc
    return sync_playwright


def _run_dir() -> Path:
    session = load_session()
    run_dir = session.get("run_dir")
    if not run_dir:
        raise SystemExit("No active run. Start with: python -m tools.ux_drive start")
    return Path(run_dir)


def _connect(playwright):
    session = load_session()
    cdp = session.get("cdp")
    if not cdp:
        raise SystemExit("No active browser session. Run: python -m tools.ux_drive start")
    browser = playwright.chromium.connect_over_cdp(cdp)
    if not browser.contexts:
        raise SystemExit("Browser has no context; restart with: python -m tools.ux_drive start")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    dialog_pref = session.get("dialog")
    if dialog_pref:

        def _on_dialog(dialog):
            if dialog_pref == "accept":
                dialog.accept()
            else:
                dialog.dismiss()

        page.on("dialog", _on_dialog)
    return browser, page


def cmd_start(args: argparse.Namespace) -> int:
    run_dir = ensure_run_dir(args.run_id)
    log_path = run_dir / "driver.log"
    env = os.environ.copy()
    env["UX_DRIVE_RUN_DIR"] = str(run_dir)
    env["UX_DRIVE_URL"] = args.url
    env["UX_DRIVE_CDP_PORT"] = str(args.cdp_port)
    env["UX_DRIVE_HEADED"] = "1" if args.headed else "0"
    with log_path.open("a", encoding="utf-8") as log:
        proc = subprocess.Popen(
            [sys.executable, "-m", "tools.ux_drive", "serve"],
            cwd=str(REPO_ROOT),
            stdout=log,
            stderr=subprocess.STDOUT,
            env=env,
            start_new_session=True,
        )
    cdp = f"http://127.0.0.1:{args.cdp_port}"
    save_session(
        {
            "cdp": cdp,
            "run_id": run_dir.name,
            "run_dir": str(run_dir),
            "url": args.url,
            "pid": proc.pid,
        }
    )
    sync_playwright = _require_playwright()
    errors: list[str] = []
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(cdp)
                page = browser.contexts[0].pages[0]
                page.wait_for_selector("#stage-stepper", timeout=5000)
                browser.close()
            print(json.dumps({"ok": True, "run_dir": str(run_dir), "url": args.url, "cdp": cdp, "pid": proc.pid}))
            return 0
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            time.sleep(0.4)
    print(
        json.dumps(
            {
                "ok": False,
                "error": "browser did not become ready",
                "log": str(log_path),
                "detail": errors[-3:],
            }
        ),
        file=sys.stderr,
    )
    return 1


def cmd_serve(_args: argparse.Namespace) -> int:
    sync_playwright = _require_playwright()
    url = os.environ.get("UX_DRIVE_URL", "http://127.0.0.1:9001")
    port = int(os.environ.get("UX_DRIVE_CDP_PORT", "9222"))
    headed = os.environ.get("UX_DRIVE_HEADED") == "1"
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=not headed, args=[f"--remote-debugging-port={port}"])
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_selector("#stage-stepper")
    try:
        while True:
            page.wait_for_timeout(60_000)
    except KeyboardInterrupt:
        pass
    finally:
        browser.close()
        p.stop()
    return 0


def cmd_state(_args: argparse.Namespace) -> int:
    sync_playwright = _require_playwright()
    with sync_playwright() as p:
        browser, page = _connect(p)
        payload = page.evaluate(_load_state_js())
        write_state(_run_dir(), payload)
        print(json.dumps(payload, indent=2))
        browser.close()
    return 0


def cmd_shot(args: argparse.Namespace) -> int:
    sync_playwright = _require_playwright()
    run_dir = _run_dir()
    with sync_playwright() as p:
        browser, page = _connect(p)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        page.screenshot(path=str(tmp_path), full_page=True)
        dest = add_screenshot(run_dir, args.label, tmp_path, note=args.note or "")
        tmp_path.unlink(missing_ok=True)
        payload = page.evaluate(_load_state_js())
        write_state(run_dir, payload)
        print(json.dumps({"ok": True, "file": str(dest), "state": payload}))
        browser.close()
    return 0


def cmd_select_skill(args: argparse.Namespace) -> int:
    sync_playwright = _require_playwright()
    with sync_playwright() as p:
        browser, page = _connect(p)
        select = page.locator("#skill-select")
        texts = [t.strip() for t in select.locator("option").all_text_contents()]
        match = next((t for t in texts if args.name.lower() in t.lower()), None)
        if not match:
            print(json.dumps({"ok": False, "error": "skill not found", "options": texts}))
            browser.close()
            return 1
        select.select_option(label=match)
        print(json.dumps({"ok": True, "skill": match}))
        browser.close()
    return 0


def cmd_select_project(args: argparse.Namespace) -> int:
    sync_playwright = _require_playwright()
    with sync_playwright() as p:
        browser, page = _connect(p)
        page.locator("#project-toggle").click()
        page.wait_for_selector("#project-menu:not([hidden])")
        loc = page.locator("#repo-list button, #folder-list button").filter(has_text=args.name)
        if loc.count() == 0:
            print(json.dumps({"ok": False, "error": f"no project matching {args.name!r}"}))
            browser.close()
            return 1
        loc.first.click()
        print(json.dumps({"ok": True, "project": page.locator("#project-label").inner_text()}))
        browser.close()
    return 0


def cmd_send(args: argparse.Namespace) -> int:
    sync_playwright = _require_playwright()
    with sync_playwright() as p:
        browser, page = _connect(p)
        page.locator("#chat-input").fill(args.text)
        page.locator("#chat-form button[type=submit]").click()
        print(json.dumps({"ok": True}))
        browser.close()
    return 0


def cmd_choose(args: argparse.Namespace) -> int:
    sync_playwright = _require_playwright()
    with sync_playwright() as p:
        browser, page = _connect(p)
        loc = page.locator("button.choice:not([disabled])").filter(has_text=args.substring)
        if loc.count() == 0:
            print(json.dumps({"ok": False, "error": "no matching choice"}))
            browser.close()
            return 1
        clicked = loc.first.inner_text()
        loc.first.click()
        print(json.dumps({"ok": True, "clicked": clicked}))
        browser.close()
    return 0


def cmd_click(args: argparse.Namespace) -> int:
    sync_playwright = _require_playwright()
    with sync_playwright() as p:
        browser, page = _connect(p)
        page.locator(args.selector).first.click()
        print(json.dumps({"ok": True, "selector": args.selector}))
        browser.close()
    return 0


def cmd_confirm(args: argparse.Namespace) -> int:
    session = load_session()
    if not session:
        raise SystemExit("No active session")
    session["dialog"] = args.action
    save_session(session)
    print(json.dumps({"ok": True, "dialog": args.action}))
    return 0


def cmd_wait(args: argparse.Namespace) -> int:
    sync_playwright = _require_playwright()
    condition = args.condition
    with sync_playwright() as p:
        browser, page = _connect(p)
        deadline = time.time() + args.timeout_ms / 1000
        last = None
        while time.time() < deadline:
            last = page.evaluate(_load_state_js())
            ok = False
            if condition == "assistant-idle":
                ok = not last.get("waiting")
            elif condition.startswith("stage="):
                ok = last.get("stage") == condition.split("=", 1)[1]
            elif condition == "brd-visible":
                ok = bool(last.get("brdVisible"))
            elif condition.startswith("choice-contains:"):
                needle = condition.split(":", 1)[1].lower()
                ok = any(needle in c.lower() for c in last.get("choices") or [])
            else:
                print(json.dumps({"ok": False, "error": f"unknown condition {condition}"}))
                browser.close()
                return 1
            if ok:
                write_state(_run_dir(), last)
                print(json.dumps({"ok": True, "state": last}))
                browser.close()
                return 0
            page.wait_for_timeout(250)
        print(json.dumps({"ok": False, "error": f"timeout waiting for {condition}", "state": last}))
        browser.close()
        return 1


def cmd_stop(_args: argparse.Namespace) -> int:
    session = load_session()
    pid = session.get("pid")
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    clear_session()
    print(json.dumps({"ok": True, "stopped": pid}))
    return 0


def cmd_gallery_init(args: argparse.Namespace) -> int:
    run_dir = ensure_run_dir(args.run_id)
    print(json.dumps({"ok": True, "run_dir": str(run_dir)}))
    return 0


def cmd_gallery_add(args: argparse.Namespace) -> int:
    if args.run_dir:
        run_dir = Path(args.run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        if not (run_dir / "INDEX.md").exists():
            (run_dir / "INDEX.md").write_text(
                f"# UX run `{run_dir.name}`\n\n| # | Label | File | When | Note |\n|---|-------|------|------|------|\n",
                encoding="utf-8",
            )
    else:
        session = load_session()
        run_dir = Path(session["run_dir"]) if session.get("run_dir") else ensure_run_dir(None)
    dest = add_screenshot(run_dir, args.label, Path(args.file), note=args.note or "")
    print(json.dumps({"ok": True, "file": str(dest), "run_dir": str(run_dir)}))
    return 0


def cmd_gallery_note(args: argparse.Namespace) -> int:
    raw = args.run_dir or load_session().get("run_dir")
    if not raw:
        raise SystemExit("Pass --run-dir or start a session")
    run_dir = Path(raw)
    append_index(run_dir, next_index(run_dir), "note", "", args.text)
    print(json.dumps({"ok": True}))
    return 0


def cmd_findings(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir) if args.run_dir else Path(load_session()["run_dir"])
    path = write_findings(run_dir, args.text)
    print(json.dumps({"ok": True, "file": str(path)}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.ux_drive", description="SDLC UX drive fallback CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    start = sub.add_parser("start", help="Launch Chromium and open the app")
    start.add_argument("--url", default="http://127.0.0.1:9001")
    start.add_argument("--run-id")
    start.add_argument("--cdp-port", type=int, default=9222)
    start.add_argument("--headed", action="store_true")
    start.set_defaults(func=cmd_start)

    sub.add_parser("serve", help="Internal: keep Chromium alive").set_defaults(func=cmd_serve)
    sub.add_parser("state").set_defaults(func=cmd_state)

    shot = sub.add_parser("shot")
    shot.add_argument("label")
    shot.add_argument("--note", default="")
    shot.set_defaults(func=cmd_shot)

    sk = sub.add_parser("select-skill")
    sk.add_argument("name")
    sk.set_defaults(func=cmd_select_skill)

    sp = sub.add_parser("select-project")
    sp.add_argument("name")
    sp.set_defaults(func=cmd_select_project)

    send = sub.add_parser("send")
    send.add_argument("text")
    send.set_defaults(func=cmd_send)

    choose = sub.add_parser("choose")
    choose.add_argument("substring")
    choose.set_defaults(func=cmd_choose)

    click = sub.add_parser("click")
    click.add_argument("selector")
    click.set_defaults(func=cmd_click)

    conf = sub.add_parser("confirm")
    conf.add_argument("action", choices=["accept", "dismiss"])
    conf.set_defaults(func=cmd_confirm)

    wait = sub.add_parser("wait")
    wait.add_argument("condition")
    wait.add_argument("--timeout-ms", type=int, default=120000)
    wait.set_defaults(func=cmd_wait)

    sub.add_parser("stop").set_defaults(func=cmd_stop)

    gal = sub.add_parser("gallery")
    galsub = gal.add_subparsers(dest="gallery_cmd", required=True)
    gi = galsub.add_parser("init")
    gi.add_argument("--run-id")
    gi.set_defaults(func=cmd_gallery_init)
    ga = galsub.add_parser("add")
    ga.add_argument("label")
    ga.add_argument("--file", required=True)
    ga.add_argument("--run-dir")
    ga.add_argument("--note", default="")
    ga.set_defaults(func=cmd_gallery_add)
    gn = galsub.add_parser("note")
    gn.add_argument("text")
    gn.add_argument("--run-dir")
    gn.set_defaults(func=cmd_gallery_note)

    findings = sub.add_parser("findings")
    findings.add_argument("text")
    findings.add_argument("--run-dir")
    findings.set_defaults(func=cmd_findings)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
