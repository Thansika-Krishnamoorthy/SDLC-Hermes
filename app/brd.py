from __future__ import annotations

import re
from pathlib import Path

from app.filesystem import PathError, resolve_under_root

BRD_FENCE_RE = re.compile(r"```brd\s*(.*?)```", re.DOTALL | re.IGNORECASE)
HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def extract_brd_markdown(text: str) -> str | None:
    fenced = BRD_FENCE_RE.search(text)
    if fenced:
        return fenced.group(1).strip()
    if "## Executive Summary" in text and "## Business Objectives" in text:
        start = text.find("# ")
        if start < 0:
            start = text.find("## Executive Summary")
        return text[start:].strip()
    return None


def slugify_feature(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")
    return slug or "Untitled-Feature"


def feature_name_from_brd(markdown: str, fallback: str = "Untitled Feature") -> str:
    match = HEADING_RE.search(markdown)
    if not match:
        return fallback
    title = match.group(1).strip()
    title = re.sub(r"^Business Requirements Document\s*[-–—:]\s*", "", title, flags=re.I)
    title = re.sub(r"^BRD\s*[-–—:]\s*", "", title, flags=re.I)
    return title or fallback


def brd_filename(feature_name: str) -> str:
    return f"BRD-{slugify_feature(feature_name)}.md"


def preview_brd_path(
    browse_root: Path,
    project_root: Path,
    markdown: str,
    feature_name: str | None = None,
) -> Path:
    project = resolve_under_root(browse_root, project_root)
    if not project.is_dir():
        raise PathError(f"Project directory does not exist: {project}")
    name = feature_name or feature_name_from_brd(markdown)
    return project / "docs" / brd_filename(name)


def save_brd(
    browse_root: Path,
    project_root: Path,
    markdown: str,
    feature_name: str | None = None,
    unique: bool = False,
) -> Path:
    project = resolve_under_root(browse_root, project_root)
    if not project.is_dir():
        raise PathError(f"Project directory does not exist: {project}")
    name = feature_name or feature_name_from_brd(markdown)
    docs = project / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    path = docs / brd_filename(name)
    if unique:
        stem = path.stem
        suffix = 2
        while path.exists():
            path = docs / f"{stem}-{suffix}.md"
            suffix += 1
    try:
        path.resolve().relative_to(project.resolve())
    except ValueError as exc:
        raise PathError("Refusing to write BRD outside the project directory.") from exc
    path.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    return path
