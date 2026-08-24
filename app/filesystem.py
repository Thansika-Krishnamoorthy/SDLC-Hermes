from __future__ import annotations

from pathlib import Path


class PathError(ValueError):
    pass


def resolve_under_root(root: Path, raw: str | Path) -> Path:
    root = root.expanduser().resolve()
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise PathError(f"Path is outside the allowed root: {resolved}") from exc
    return resolved


def list_directories(root: Path, current: Path) -> dict:
    current = resolve_under_root(root, current)
    if not current.exists():
        raise PathError(f"Directory does not exist: {current}")
    if not current.is_dir():
        raise PathError(f"Not a directory: {current}")

    parent = current.parent if current != root else None
    entries = []
    for child in sorted(current.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir() and not child.name.startswith("."):
            git_dir = child / ".git"
            entries.append(
                {
                    "name": child.name,
                    "path": str(child),
                    "is_git": git_dir.is_dir() or git_dir.is_file(),
                }
            )
    return {
        "root": str(root),
        "current": str(current),
        "parent": str(parent) if parent else None,
        "is_git": (current / ".git").is_dir() or (current / ".git").is_file(),
        "directories": entries,
    }


def create_directory(root: Path, parent: Path, name: str) -> Path:
    name = name.strip().strip("/").replace("\\", "")
    if not name or name in {".", ".."} or "/" in name:
        raise PathError("Provide a single folder name without path separators.")
    parent_resolved = resolve_under_root(root, parent)
    if not parent_resolved.is_dir():
        raise PathError(f"Parent directory does not exist: {parent_resolved}")
    target = resolve_under_root(root, parent_resolved / name)
    target.mkdir(parents=False, exist_ok=False)
    return target
