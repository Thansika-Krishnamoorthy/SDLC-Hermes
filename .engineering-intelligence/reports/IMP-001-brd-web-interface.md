# IMP-001: BRD generation web interface

## Classification
- Type: feature
- Risk: medium
- Scope: new FastAPI web app, static frontend, skill/project APIs, OpenRouter chat, BRD file writer
- Depth: Standard (greenfield; no prior product code)

## Analysis
- Mode: proposal
- Freshness gate: passed — no existing intelligence or product modules (empty repo except `skills/`)
- Graph inputs consulted: none (graphs not initialized)
- Directly affected:
  - New application under `app/`
  - New tests under `tests/`
  - Config: `.env.example`, `requirements.txt`
  - Existing `skills/` is read-only input, not modified
- Indirectly affected:
  - Target project directories receive `docs/BRD-*.md` writes
  - OpenRouter/DeepSeek is an external LLM sink for stakeholder text
- Risk factors:
  - Filesystem browse/create can traverse or write unexpected paths
  - Stakeholder messages and skill markdown reach an LLM (prompt injection)
  - API keys must stay server-side
  - No auth: local-tool assumption

## Validation Requirements
- Unit tests for skill discovery, prompt composition, path containment, BRD filename
- Type safety: Python type hints + pytest
- API compatibility: not applicable (new API)
- Migration safety: not applicable
- Acceptance mapping: required
- Manual verification: start server and exercise setup + API with curl (no browser MCP in this session)

## Intelligence Artifacts Affected
- Knowledge base, memory, context, graphs (first initialization after scaffold)
- AI-DLC state, execution plan, acceptance criteria

## Evidence
- `skills/business-requirement-analysis/SKILL.md` — interview, BRD, approval gate, no technical work
- `skills/business-requirement-analysis/references/interview-guidelines.md` — one numbered MCQ at a time
- `skills/business-requirement-analysis/references/brd-template.md` — BRD sections
- `skills/business-requirement-analysis/references/output-format.md` — save `<project-root>/docs/BRD-<Feature-Name>.md`
- User request — skill picker, project dir picker/create, OpenRouter + DeepSeek V4 Flash

## Unknowns
- Whether later SDLC skills will be added under `skills/` (UI lists whatever folders exist)
- `grill-me` is referenced by the BRD skill but is not in this repo's `skills/` folder; interview behavior will be taken from `interview-guidelines.md` bundled as a reference
