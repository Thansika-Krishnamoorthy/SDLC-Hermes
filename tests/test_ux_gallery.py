from pathlib import Path

from tools.ux_drive import STATE_JS_PATH
from tools.ux_drive.cli import build_parser, main
from tools.ux_drive.gallery import add_screenshot, ensure_run_dir, write_state


def test_state_js_covers_review_flags():
    script = STATE_JS_PATH.read_text(encoding="utf-8")
    for token in ("is-active", "brdVisible", "reviewMode", "chatStageWidth", "button.choice"):
        assert token in script


def test_gallery_writes_index_and_state(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("tools.ux_drive.gallery.ARTIFACTS_ROOT", tmp_path)
    run_dir = ensure_run_dir("demo-run")
    png = tmp_path / "src.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    dest = add_screenshot(run_dir, "setup-empty", png, note="first viewport")
    assert dest.name == "01-setup-empty.png"
    index = (run_dir / "INDEX.md").read_text(encoding="utf-8")
    assert "setup-empty" in index
    assert "01-setup-empty.png" in index
    write_state(run_dir, {"stage": "setup"})
    assert '"stage": "setup"' in (run_dir / "STATE.json").read_text(encoding="utf-8")


def test_cli_gallery_init_and_add(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("tools.ux_drive.gallery.ARTIFACTS_ROOT", tmp_path)
    assert main(["gallery", "init", "--run-id", "cli-run"]) == 0
    png = tmp_path / "shot.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n")
    assert main(["gallery", "add", "after-round", "--file", str(png), "--run-dir", str(tmp_path / "cli-run")]) == 0
    assert (tmp_path / "cli-run" / "01-after-round.png").exists()


def test_cli_help_lists_drive_commands():
    help_text = build_parser().format_help()
    for cmd in ("start", "state", "shot", "send", "choose", "click", "confirm", "wait", "stop", "gallery"):
        assert cmd in help_text
