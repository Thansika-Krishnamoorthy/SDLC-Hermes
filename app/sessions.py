from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Session:
    id: str
    skill_ids: list[str]
    project_path: str
    system_prompt: str
    messages: list[dict[str, str]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    saved_brd_path: str | None = None
    approved: bool = False


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self, skill_ids: list[str], project_path: str, system_prompt: str) -> Session:
        session = Session(
            id=str(uuid.uuid4()),
            skill_ids=skill_ids,
            project_path=project_path,
            system_prompt=system_prompt,
            messages=[{"role": "system", "content": system_prompt}],
        )
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)


store = SessionStore()
