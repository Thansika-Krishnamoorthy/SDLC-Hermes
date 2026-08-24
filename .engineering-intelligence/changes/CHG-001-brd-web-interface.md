# CHG-001: BRD generation web interface

## Request
Analyze the skills folder and business-requirement-analysis references; create a web interface for BRD generation with skill selection, project directory selection/creation, OpenRouter + DeepSeek V4 Flash.

## Classification
- Type: feature | Risk: medium

## Implementation Summary
Added a FastAPI app that discovers skills from `skills/`, composes SKILL.md plus references into the system prompt, lets the operator browse or create a project directory under a browse root, streams an interview through OpenRouter (`deepseek/deepseek-v4-flash`), extracts a fenced BRD, and writes `<project>/docs/BRD-<Feature>.md`.

## Files Changed
- `app/` — API, skill loader, filesystem guards, OpenRouter client, UI
- `tests/` — skill discovery, path safety, BRD save, health/skills API
- `README.md`, `requirements.txt`, `.env.example`

## Tests
- `pytest` — 8 passed after BRD title slug fix

## Acceptance Criteria Verification
| Criterion | Evidence Type | Evidence | Result | Open Item |
|---|---|---|---|---|
| AC-1 Skill selection | automated test | `tests/test_api.py`, `tests/test_skills_and_projects.py` | pass | — |
| AC-2 Existing project directory | automated test | `test_create_and_list_project_directory` | pass | Browser browse UX not exercised (no browser MCP) |
| AC-3 New project directory | automated test | `test_create_and_list_project_directory` | pass | — |
| AC-4 Interview then BRD | manual verification | Requires OpenRouter key and live model | pending | Operator run |
| AC-5 Persist BRD | automated test | `test_extract_and_save_brd` | pass | — |
| AC-6 Provider | automated test | health endpoint model/provider | pass | Live OpenRouter call not run in CI |

## Safety Gates
- Freshness gate: passed (greenfield)
- Type safety: Python type hints; pytest passed
- API compatibility: not applicable
- API snapshots: not applicable
- Migration safety: not applicable
- Dependency security: not run (new local tool; no lockfile audit)
- Environment variables: `OPENROUTER_API_KEY` and related documented in `.env.example`
- ADR compliance: not applicable (no ADRs)
- LLM prompt injection: reviewed; see `LLM-PROMPT-INJECTION-brd-web-runner.md`
- Convention enforcement: new project, FastAPI modules

## Rollback
- Code rollback: delete `app/`, `tests/`, and config files or revert the change set
- Data rollback: N/A (generated BRDs live in chosen project `docs/`)
- Feature flag rollback: N/A
- Infrastructure rollback: N/A
- Irreversible steps requiring approval: none

## Related Reports
- IMP-001: `.engineering-intelligence/reports/IMP-001-brd-web-interface.md`

## Synchronized Artifacts
- Impact report, acceptance criteria, this change record, prompt-injection review

## Unresolved Risks
- Live interview quality depends on DeepSeek following the skill prompt
- App has no authentication; intended as a local tool
- `grill-me` is not in `skills/`; interview rules come from `interview-guidelines.md`
