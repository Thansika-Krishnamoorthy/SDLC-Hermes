# LLM Prompt Injection Review: BRD web runner

## Data Paths
| Source | LLM / Memory Sink | Control Present | Risk | Evidence |
|---|---|---|---|---|
| Stakeholder chat text | OpenRouter chat completions system+user messages | Yes — wrapped in stakeholder_message tags; tags stripped from input | Medium | `app/prompt_builder.py`, `app/openrouter.py` |
| Selected skill markdown from local `skills/` | System prompt | Yes — local files only, not user-uploaded | Low | `app/skill_loader.py` |
| Project path string | System prompt session block | Yes — resolved under browse root | Low | `app/filesystem.py` |
| Model BRD output | `<project>/docs/BRD-*.md` | Partial — markdown written after filename slug; no HTML execution | Medium | `app/brd.py` |

## Findings
- User text is not placed in the system prompt.
- Instruction-tag breakout is stripped before wrap.
- Skill files are trusted local content; if an untrusted skill is added to `skills/`, it becomes part of the system prompt (operator-controlled).
- No output schema beyond BRD fence extraction; malicious markdown could be saved into docs (local file write, not rendered as HTML in the preview beyond text in a `<pre>`).

## Required Tests
- `test_wrap_untrusted_strips_instruction_tags` in `tests/test_skills_and_projects.py`
