"""Agent-driven UX helpers. Browser MCP is the primary harness; this package is the fallback CLI + gallery."""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent.parent
STATE_JS_PATH = PACKAGE_DIR / "state.js"
ARTIFACTS_ROOT = REPO_ROOT / "tests" / "artifacts" / "ux"
SESSION_PATH = ARTIFACTS_ROOT / ".session.json"

__all__ = ["PACKAGE_DIR", "REPO_ROOT", "STATE_JS_PATH", "ARTIFACTS_ROOT", "SESSION_PATH"]
