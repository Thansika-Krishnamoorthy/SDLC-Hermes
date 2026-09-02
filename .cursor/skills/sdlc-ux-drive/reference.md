# SDLC UX drive — selectors, CDP, CLI

## Selectors

| UI | Selector |
|----|----------|
| Stage (active `is-active`) | `#stage-stepper li[data-stage]` |
| Skill | `#skill-select` |
| Project | `#project-toggle`, `#project-label`, `#project-menu`, `#repo-list`, `#folder-list`, `#select-dir-btn` |
| Chat | `#chat-input`, `#chat-form` |
| Transcript | `#transcript`, `#transcript-history` |
| Choices | `button.choice` in `.choices`; Other: `.other-input`, `.round-continue` |
| BRD | `#brd-card`, `#brd-preview`, `#approve-btn`, `#modify-btn`, `#more-btn`, `#save-path` |
| Modes | `#mode-banner`, `#mode-cancel-btn` |
| Errors | `#setup-error`, `#chat-error`, `#health-meta` |
| Review layout | `#chat-stage.review-mode` |

Stages: `setup` → `interview` → `review` → `done`.

## CDP vs snapshot

| Need | How |
|------|-----|
| Stage, waiting, choices, BRD, widths | Evaluate `tools/ux_drive/state.js` |
| Progress, inView, click choice/repo, scroll, approve | [scripts/cdp.js](scripts/cdp.js) IIFEs |
| Setup refs only | `browser_snapshot` once |
| Interview choices | **Never** wait for snapshot refs — they are missing |

Always pass the locked tab **`viewId`**. After Send, poll CDP in the same turn (no long sleep). Native Approve `confirm` blocks MCP: use `confirmAndApprove` in `cdp.js`.

Gallery `add` in parallel with the next Browser call:

```bash
python -m tools.ux_drive gallery init --run-id <id>
python -m tools.ux_drive gallery add setup-empty --file /tmp/cursor/screenshots/<file>.png --run-dir tests/artifacts/ux/<id>
```

## Browser MCP map

| Intent | Tool |
|--------|------|
| List / switch tab | `browser_tabs` `list` then `select` + `index` |
| Hold tab | `browser_lock` lock / unlock; keep `viewId` |
| Setup refs | `browser_snapshot` once |
| Type opening | `browser_fill` on `#chat-input` **with viewId**, then Send |
| Interview pick | CDP `clickChoice` / `clickFirstNonOther` |
| Project | click `#project-toggle`, CDP `clickRepo` |
| Shot | `browser_take_screenshot` (budget in SKILL.md) |

## Fallback CLI (Browser MCP missing only)

Needs `playwright` + `playwright install chromium`. Do not mix with an active Browser run.

```bash
python -m tools.ux_drive start --url http://127.0.0.1:9001
python -m tools.ux_drive shot setup-empty
python -m tools.ux_drive state
python -m tools.ux_drive select-skill "Business Requirement Analysis"
python -m tools.ux_drive select-project <folder-name>
python -m tools.ux_drive send "…"
python -m tools.ux_drive wait assistant-idle
python -m tools.ux_drive choose "<live substring>"
python -m tools.ux_drive click "#approve-btn"
python -m tools.ux_drive confirm accept
python -m tools.ux_drive stop
```

`wait` conditions: `assistant-idle`, `stage=<name>`, `brd-visible`, `choice-contains:<text>`.

## CI smoke (not this skill’s loop)

`pytest -m e2e` — mocked selectors/gallery, no OpenRouter.
