from __future__ import annotations

from pathlib import Path

SKIP_DIRS = {
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".cache",
    "target",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "snap",
    "Applications",
}


def is_git_repo(path: Path) -> bool:
    git = path / ".git"
    return git.is_dir() or git.is_file()


def remote_url(path: Path) -> str | None:
    config = path / ".git" / "config"
    if not config.is_file():
        return None
    for line in config.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("url ="):
            return stripped.split("=", 1)[1].strip() or None
    return None


def _collect(current: Path, depth: int, max_depth: int, limit: int, found: list[dict], seen: set[str]) -> None:
    if len(found) >= limit or depth > max_depth:
        return
    try:
        children = list(current.iterdir())
    except OSError:
        return
    if is_git_repo(current):
        key = str(current)
        if key not in seen:
            seen.add(key)
            found.append(
                {
                    "name": current.name,
                    "path": key,
                    "remote": remote_url(current),
                }
            )
        return
    for child in sorted(children, key=lambda item: item.name.lower()):
        if not child.is_dir():
            continue
        if child.name.startswith(".") or child.name in SKIP_DIRS:
            continue
        _collect(child, depth + 1, max_depth, limit, found, seen)


def find_git_repos(
    root: Path,
    extra_roots: list[Path] | None = None,
    max_depth: int = 5,
    limit: int = 80,
) -> list[dict]:
    found: list[dict] = []
    seen: set[str] = set()
    starts: list[Path] = []
    for candidate in [*(extra_roots or []), root]:
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            continue
        if not resolved.exists() or resolved in starts:
            continue
        starts.append(resolved)
        if is_git_repo(resolved) and resolved.parent not in starts:
            starts.append(resolved.parent)
    for start in starts:
        _collect(start, 0, max_depth, limit, found, seen)
        if len(found) >= limit:
            break
    found.sort(key=lambda item: item["name"].lower())
    return found
