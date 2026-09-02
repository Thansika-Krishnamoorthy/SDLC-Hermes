from pathlib import Path

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


client = TestClient(app)


def test_health_and_skills_endpoints():
    health = client.get("/api/health")
    assert health.status_code == 200
    body = health.json()
    assert body["provider"] == "openrouter"
    assert "deepseek" in body["model"]

    skills = client.get("/api/skills")
    assert skills.status_code == 200
    payload = skills.json()["skills"]
    ids = [item["id"] for item in payload]
    assert "business-requirement-analysis" in ids
    bra = next(item for item in payload if item["id"] == "business-requirement-analysis")
    assert bra["name"] == "Business Requirement Analysis"
    assert bra["name"] != bra["id"]


def test_index_serves_skill_and_project_dropdowns():
    page = client.get("/")
    assert page.status_code == 200
    html = page.text
    assert 'id="skill-select"' in html
    assert 'id="project-toggle"' in html
    assert 'id="repo-list"' in html
    assert 'id="stage-stepper"' in html
    assert 'id="health-meta"' in html
    assert 'id="mode-banner"' in html
    assert 'id="transcript-history"' in html
    assert 'class="brd-body"' in html
    assert 'class="brd-actions-sticky"' in html
    assert "Kovan SDLC" in html


def test_brd_preview_accepts_markdown_query(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "browse_root", tmp_path)
    project = tmp_path / "demo-app"
    project.mkdir()
    started = client.post(
        "/api/sessions",
        json={
            "skill_ids": ["business-requirement-analysis"],
            "project_path": str(project),
            "opening_message": "Need QR scanning",
        },
    )
    session_id = started.json()["id"]
    markdown = (
        "# Business Requirements Document — QR Code Scanning\n\n"
        "## Executive Summary\nScan codes.\n\n## Business Objectives\nSpeed up entry.\n"
    )
    preview = client.get(
        f"/api/sessions/{session_id}/brd/preview",
        params={"markdown": markdown},
    )
    assert preview.status_code == 200
    assert preview.json()["filename"] == "BRD-QR-Code-Scanning.md"
    assert not (project / "docs").exists()


def test_brd_preview_returns_path_without_writing(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "browse_root", tmp_path)
    project = tmp_path / "demo-app"
    project.mkdir()
    started = client.post(
        "/api/sessions",
        json={
            "skill_ids": ["business-requirement-analysis"],
            "project_path": str(project),
            "opening_message": "Need visitor check-in",
        },
    )
    assert started.status_code == 200
    session_id = started.json()["id"]
    from app.sessions import store

    session = store.get(session_id)
    session.messages.append(
        {
            "role": "assistant",
            "content": "```brd\n# Business Requirements Document — Visitor Check-In\n\n## Executive Summary\nNeed faster check-in.\n\n## Business Objectives\nReduce wait time.\n```",
        }
    )
    preview = client.get(f"/api/sessions/{session_id}/brd/preview")
    assert preview.status_code == 200
    body = preview.json()
    assert body["filename"] == "BRD-Visitor-Check-In.md"
    assert body["relative"] == "docs/BRD-Visitor-Check-In.md"
    assert not (project / "docs" / body["filename"]).exists()


def test_browse_and_create_project(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "browse_root", tmp_path)
    listing = client.get("/api/fs")
    assert listing.status_code == 200
    assert listing.json()["current"] == str(tmp_path.resolve())

    created = client.post(
        "/api/projects",
        json={"parent": str(tmp_path.resolve()), "name": "demo-app"},
    )
    assert created.status_code == 200
    assert created.json()["name"] == "demo-app"
    assert (tmp_path / "demo-app").is_dir()


def test_lists_git_repos(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "browse_root", tmp_path)
    repo = tmp_path / "payroll-app"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / ".git" / "config").write_text("[remote \"origin\"]\n\turl = git@github.com:acme/payroll-app.git\n", encoding="utf-8")
    (tmp_path / "not-a-repo").mkdir()

    listing = client.get("/api/fs")
    dirs = {item["name"]: item for item in listing.json()["directories"]}
    assert dirs["payroll-app"]["is_git"] is True
    assert dirs["not-a-repo"]["is_git"] is False

    repos = client.get("/api/repos")
    assert repos.status_code == 200
    names = [item["name"] for item in repos.json()["repos"]]
    assert names == ["payroll-app"]
    assert repos.json()["repos"][0]["remote"] == "git@github.com:acme/payroll-app.git"


def test_approve_saves_brd_automatically(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "browse_root", tmp_path)
    project = tmp_path / "demo-app"
    project.mkdir()
    started = client.post(
        "/api/sessions",
        json={
            "skill_ids": ["business-requirement-analysis"],
            "project_path": str(project),
            "opening_message": "Need visitor check-in",
        },
    )
    assert started.status_code == 200
    session_id = started.json()["id"]
    from app.sessions import store

    session = store.get(session_id)
    session.messages.append(
        {
            "role": "assistant",
            "content": "```brd\n# Business Requirements Document — Visitor Check-In\n\n## Executive Summary\nNeed faster check-in.\n\n## Business Objectives\nReduce wait time.\n```",
        }
    )
    approved = client.post(f"/api/sessions/{session_id}/approve")
    assert approved.status_code == 200
    saved = Path(approved.json()["path"])
    assert saved.exists()
    assert saved.parent.name == "docs"
    assert saved.parent.parent == project.resolve()


def test_second_feature_saves_a_new_brd_file(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "browse_root", tmp_path)
    project = tmp_path / "demo-app"
    project.mkdir()
    from app.sessions import store

    def approve_feature(title: str) -> Path:
        started = client.post(
            "/api/sessions",
            json={
                "skill_ids": ["business-requirement-analysis"],
                "project_path": str(project),
                "opening_message": title,
            },
        )
        session_id = started.json()["id"]
        session = store.get(session_id)
        session.messages.append(
            {
                "role": "assistant",
                "content": (
                    f"```brd\n# Business Requirements Document — {title}\n\n"
                    "## Executive Summary\nNeed it.\n\n## Business Objectives\nShip it.\n```"
                ),
            }
        )
        approved = client.post(f"/api/sessions/{session_id}/approve")
        assert approved.status_code == 200
        return Path(approved.json()["path"])

    first = approve_feature("Visitor Check-In")
    second = approve_feature("QR Code Scanning")
    assert first.name == "BRD-Visitor-Check-In.md"
    assert second.name == "BRD-QR-Code-Scanning.md"
    assert first.exists() and second.exists()
    assert first != second
