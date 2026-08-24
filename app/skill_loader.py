from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


@dataclass
class Skill:
    id: str
    name: str
    description: str
    path: Path
    body: str
    references: list[tuple[str, str]] = field(default_factory=list)

    def compose_prompt(self) -> str:
        parts = [
            f"===== SKILL: {self.name} =====",
            self.body.strip(),
        ]
        for filename, content in self.references:
            parts.append(f"===== REFERENCE: {filename} =====")
            parts.append(content.strip())
        return "\n\n".join(parts)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, match.group(2)


def discover_skills(skills_dir: Path) -> list[Skill]:
    if not skills_dir.is_dir():
        return []
    skills: list[Skill] = []
    for child in sorted(skills_dir.iterdir()):
        skill_file = child / "SKILL.md"
        if not child.is_dir() or not skill_file.is_file():
            continue
        text = skill_file.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)
        references: list[tuple[str, str]] = []
        ref_dir = child / "references"
        if ref_dir.is_dir():
            for ref in sorted(ref_dir.glob("*.md")):
                references.append((ref.name, ref.read_text(encoding="utf-8")))
        skills.append(
            Skill(
                id=child.name,
                name=meta.get("name", child.name),
                description=meta.get("description", ""),
                path=child,
                body=body,
                references=references,
            )
        )
    return skills


def get_skill(skills_dir: Path, skill_id: str) -> Skill | None:
    for skill in discover_skills(skills_dir):
        if skill.id == skill_id:
            return skill
    return None
