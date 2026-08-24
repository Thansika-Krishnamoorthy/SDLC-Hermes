# IMP-002: Git project picker, clickable interview options, Teams theme

## Classification
- Type: feature
- Risk: low
- Scope: filesystem/git listing, project dropdown UI, chat option rendering, CSS theme
- Depth: Standard

## Analysis
- Mode: proposal
- Freshness gate: passed (change is local to this greenfield app)
- Directly affected: `app/filesystem.py`, new `app/git_repos.py`, `app/main.py`, `app/prompt_builder.py`, `app/static/*`, tests
- Indirectly affected: OpenRouter interview turns (prompt asks for numbered options the UI turns into buttons)
- Risk factors: scanning the browse root for `.git` must skip heavy/unreadable trees and stay inside the browse root

## Validation Requirements
- Unit tests for git-repo discovery
- API test for `/api/repos`
- Existing skill/project/BRD tests
