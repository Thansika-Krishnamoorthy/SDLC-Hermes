from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.brd import (
    brd_filename,
    extract_brd_markdown,
    feature_name_from_brd,
    preview_brd_path,
    save_brd,
)
from app.config import REPO_ROOT, settings
from app.filesystem import PathError, create_directory, list_directories, resolve_under_root
from app.git_repos import find_git_repos
from app.openrouter import LLMError, stream_chat
from app.prompt_builder import build_system_prompt, wrap_untrusted
from app.sessions import store
from app.skill_loader import discover_skills, get_skill

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title=settings.app_title)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class CreateProjectBody(BaseModel):
    parent: str
    name: str = Field(min_length=1, max_length=120)


class StartSessionBody(BaseModel):
    skill_ids: list[str] = Field(min_length=1)
    project_path: str
    opening_message: str = Field(min_length=1, max_length=8000)


class ChatBody(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class SaveBrdBody(BaseModel):
    markdown: str | None = None
    feature_name: str | None = None


def _root() -> Path:
    return settings.resolved_browse_root()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "model": settings.openrouter_model,
        "provider": "openrouter",
        "skills_dir": str(settings.resolved_skills_dir()),
        "browse_root": str(_root()),
        "workspace": str(settings.default_workspace()),
        "api_key_configured": bool(
            settings.openrouter_api_key and settings.openrouter_api_key != "replace-me"
        ),
    }


@app.get("/api/skills")
def list_skills() -> dict:
    skills = discover_skills(settings.resolved_skills_dir())
    return {
        "skills": [
            {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "references": [name for name, _ in skill.references],
            }
            for skill in skills
        ]
    }


@app.get("/api/fs")
def browse_fs(path: str | None = None) -> dict:
    try:
        current = resolve_under_root(_root(), path) if path else settings.default_workspace()
        return list_directories(_root(), current)
    except PathError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/repos")
def list_repos() -> dict:
    extras: list[Path] = []
    for candidate in (
        Path.home() / "KovanLabs",
        Path.home() / "projects",
        Path.home() / "Documents",
        REPO_ROOT.parent,
        REPO_ROOT,
    ):
        try:
            resolved = candidate.resolve()
            resolved.relative_to(_root())
            extras.append(resolved)
        except (OSError, ValueError):
            continue
    return {"repos": find_git_repos(_root(), extra_roots=extras)}


@app.post("/api/projects")
def create_project(body: CreateProjectBody) -> dict:
    try:
        created = create_directory(_root(), Path(body.parent), body.name)
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail="A folder with that name already exists.") from exc
    except PathError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"path": str(created), "name": created.name}


@app.post("/api/sessions")
def start_session(body: StartSessionBody) -> dict:
    skills = []
    for skill_id in body.skill_ids:
        skill = get_skill(settings.resolved_skills_dir(), skill_id)
        if skill is None:
            raise HTTPException(status_code=404, detail=f"Unknown skill: {skill_id}")
        skills.append(skill)
    try:
        project = resolve_under_root(_root(), body.project_path)
    except PathError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not project.is_dir():
        raise HTTPException(status_code=400, detail=f"Project directory does not exist: {project}")

    session = store.create(
        skill_ids=body.skill_ids,
        project_path=str(project),
        system_prompt=build_system_prompt(skills, str(project)),
    )
    return {"id": session.id, "skill_ids": session.skill_ids, "project_path": session.project_path}


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    visible = [m for m in session.messages if m["role"] != "system"]
    return {
        "id": session.id,
        "skill_ids": session.skill_ids,
        "project_path": session.project_path,
        "saved_brd_path": session.saved_brd_path,
        "approved": session.approved,
        "messages": visible,
    }


async def _chat_stream(session_id: str, user_text: str):
    session = store.get(session_id)
    if session is None:
        yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
        return
    session.messages.append({"role": "user", "content": wrap_untrusted(user_text)})
    assembled = []
    try:
        async for token in stream_chat(session.messages):
            assembled.append(token)
            yield f"data: {json.dumps({'token': token})}\n\n"
    except LLMError as exc:
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        return
    full = "".join(assembled)
    session.messages.append({"role": "assistant", "content": full})
    brd = extract_brd_markdown(full)
    payload = {
        "done": True,
        "brd": brd,
        "feature_name": feature_name_from_brd(brd) if brd else None,
    }
    yield f"data: {json.dumps(payload)}\n\n"


@app.post("/api/sessions/{session_id}/messages")
async def send_message(session_id: str, body: ChatBody) -> StreamingResponse:
    if store.get(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return StreamingResponse(
        _chat_stream(session_id, body.content),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _latest_brd(session) -> tuple[str | None, str | None]:
    for message in reversed(session.messages):
        if message["role"] != "assistant":
            continue
        markdown = extract_brd_markdown(message["content"])
        if markdown:
            return markdown, feature_name_from_brd(markdown)
    return None, None


@app.get("/api/sessions/{session_id}/brd/preview")
def preview_brd(
    session_id: str,
    markdown: str | None = None,
    feature_name: str | None = None,
) -> dict:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if markdown:
        resolved_markdown = markdown
        resolved_feature = feature_name or feature_name_from_brd(markdown)
    else:
        resolved_markdown, extracted_name = _latest_brd(session)
        resolved_feature = feature_name or extracted_name
    if not resolved_markdown:
        raise HTTPException(status_code=400, detail="No BRD markdown is available.")
    try:
        path = preview_brd_path(
            _root(),
            Path(session.project_path),
            resolved_markdown,
            resolved_feature,
        )
    except PathError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "filename": path.name,
        "relative": str(Path("docs") / path.name),
        "absolute": str(path.resolve()),
    }


@app.post("/api/sessions/{session_id}/brd")
def persist_brd(session_id: str, body: SaveBrdBody) -> dict:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    markdown = body.markdown
    feature_name = body.feature_name
    if not markdown:
        markdown, extracted_name = _latest_brd(session)
        feature_name = feature_name or extracted_name
    if not markdown:
        raise HTTPException(status_code=400, detail="No BRD markdown is available to save.")
    filename = brd_filename(feature_name or feature_name_from_brd(markdown))
    overwrite_current = bool(
        session.saved_brd_path and Path(session.saved_brd_path).name == filename
    )
    try:
        path = save_brd(
            _root(),
            Path(session.project_path),
            markdown,
            feature_name,
            unique=not overwrite_current,
        )
    except PathError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    session.saved_brd_path = str(path)
    return {
        "path": str(path),
        "filename": path.name,
        "relative": str(path.relative_to(REPO_ROOT)) if _is_relative(path) else str(path),
    }


@app.post("/api/sessions/{session_id}/approve")
def approve(session_id: str) -> dict:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.saved_brd_path:
        persist_brd(session_id, SaveBrdBody())
        session = store.get(session_id)
    session.approved = True
    return {
        "approved": True,
        "path": session.saved_brd_path,
        "message": "BRD approved and saved. Later SDLC stages will not start automatically.",
    }


def _is_relative(path: Path) -> bool:
    try:
        path.relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False
