# SDLC Skill Runner

Local web app that runs agent skills from `skills/` against a chosen project directory. The first skill is **business-requirement-analysis**: interview the stakeholder, write a Business Requirements Document, save it, and wait for approval.

## What the BRD skill does

`skills/business-requirement-analysis/SKILL.md` stays in the business domain. It does not design or implement software.

| File | Role |
|---|---|
| `SKILL.md` | Interview, write BRD, wait for Approve / Modify / Add More Requirements |
| `references/interview-guidelines.md` | One numbered question at a time, dynamic options, no fixed questionnaire |
| `references/brd-template.md` | Required BRD sections |
| `references/output-format.md` | Save to `<project-root>/docs/BRD-<Feature-Name>.md` |

The skill text references a **grill-me** interview style. 

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Put your OpenRouter key in .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

Open http://127.0.0.1:8010


Directory browsing is limited to `BROWSE_ROOT` (defaults to your home directory).


