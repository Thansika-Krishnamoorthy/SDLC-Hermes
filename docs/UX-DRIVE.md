# UX drive playbook (Cursor agent)

The **Browser tool** (`@Browser` / `cursor-ide-browser`) is the primary harness. You decide each user input and when to screenshot. A Playwright CLI exists only when Browser MCP is missing.

Live OpenRouter is the default (real interview). Do not mock the model unless you are running the optional CI smoke.

## Prefer Browser MCP

If `GetDynamicTools` lists `cursor-ide-browser`, use it. Do **not** start `tools.ux_drive` in the same run.

| Intent | Browser tool |
|--------|----------------|
| Open app | `browser_navigate` → `http://127.0.0.1:9001/` (or `:8000` if that is what is running) |
| Hold the tab | `browser_lock` with `action: lock` after navigate |
| See structure | `browser_snapshot` |
| Compact flags | `browser_cdp` `Runtime.evaluate` with the snippet in [State snippet](#state-snippet) |
| Type a message | `browser_fill` / `browser_type` on `#chat-input`, then submit (`#chat-form` button or Enter) |
| Skill | `browser_select_option` on `#skill-select` |
| Project | click `#project-toggle`, then a repo/folder in `#repo-list` / `#folder-list` or `#select-dir-btn` |
| Interview choice | click a visible `.choice` button from the snapshot (match live labels; do not hardcode) |
| Round “Other” | fill `.other-input`, click `.round-continue` |
| Screenshot | `browser_take_screenshot` after each milestone below |
| Persist shot | `python -m tools.ux_drive gallery add <label> --file <png>` (if you have a PNG path) |
| Unlock | `browser_lock` `action: unlock` when the run is finished |

If Browser tools are unavailable, use [Fallback CLI](#fallback-cli).

## When to screenshot

Take a shot (and review the image before the next input) at:

1. Setup empty (skill/project not confirmed)
2. After project selected
3. After the opening message, once `.waiting` is gone
4. After each answered round (collapsed prior choices, new choices visible)
5. When the BRD card appears (review stage)
6. Modify / Add mode banners
7. After Approve + confirm (Done)

Also screenshot if layout looks wrong (narrow chat column, overlapping controls, missing tables).

## Selectors

| UI | Selector |
|----|----------|
| Stage stepper | `#stage-stepper li[data-stage]` — active class is `is-active` |
| Skill | `#skill-select` |
| Project toggle / label | `#project-toggle`, `#project-label` |
| Project menu | `#project-menu` |
| Chat | `#chat-input`, `#chat-form` |
| Transcript | `#transcript`, `#transcript-history`, `#transcript-summary` |
| Choice buttons | `button.choice` inside `.choices` |
| Round progress | `.round-progress`, `.round-continue` |
| BRD | `#brd-card`, `#brd-preview`, `#brd-actions`, `#approve-btn`, `#modify-btn`, `#more-btn`, `#save-path` |
| Modes | `#mode-banner`, `#mode-banner-text`, `#mode-cancel-btn` |
| Errors | `#setup-error`, `#chat-error`, `#health-meta` |
| Review layout | `#chat-stage.review-mode` |

Approve uses `window.confirm`. In Browser MCP, accept the native dialog if the tool exposes it; with the CLI use `confirm accept`.

## Review checklist (read the PNG)

- Setup: skill is human-readable; project picker usable; empty-state copy is clear
- Interview: one round of choices at a time; completed rounds collapse; no wall of disabled buttons
- Review: BRD uses remaining viewport; markdown **tables** render as `<table>`; sticky Approve/Modify/Add; `#save-path` shown; interview history collapsed
- `#chat-stage` width should be ~full remaining viewport (not a narrow centered column)
- After approve: stage `done`; BRD hidden; save path mentioned in transcript

## Stop criteria

Stop and write `FINDINGS.md` in the run gallery when:

- You completed Setup → Interview → Review → Approve → Done, or
- You found a blocker (chat error, missing choices, BRD never appears, layout broken)

Findings: bugs first, then UX suggestions. Do not approve the BRD until you have reviewed a BRD screenshot (tables, sticky bar, save path).

## State snippet

Use this with `browser_cdp` `Runtime.evaluate` (`returnByValue: true`), or `python -m tools.ux_drive state`.

```javascript
(() => {
  const $ = (id) => document.getElementById(id);
  const stepper = $("stage-stepper");
  const stage =
    stepper?.querySelector("li.is-active")?.dataset.stage || null;
  const brd = $("brd-card");
  const banner = $("mode-banner");
  const chat = $("chat-stage");
  const visible = (el) => !!(el && !el.hidden && el.offsetParent !== null);
  const choices = [...document.querySelectorAll("button.choice")]
    .filter((el) => !el.disabled && visible(el))
    .map((el) => (el.textContent || "").trim())
    .filter(Boolean);
  const err = (id) => {
    const el = $(id);
    if (!el || el.hidden) return "";
    return (el.textContent || "").trim();
  };
  return {
    stage,
    skill: $("skill-select")?.selectedOptions?.[0]?.textContent?.trim() || "",
    project: $("project-label")?.textContent?.trim() || "",
    messageCount: $("transcript")?.children?.length || 0,
    waiting: !!document.querySelector(".prompt.waiting"),
    choices,
    brdVisible: !!(brd && !brd.hidden),
    savePath: $("save-path")?.textContent?.trim() || "",
    reviewMode: !!chat?.classList.contains("review-mode"),
    modeBanner: banner && !banner.hidden
      ? $("mode-banner-text")?.textContent?.trim() || ""
      : "",
    errors: {
      setup: err("setup-error"),
      chat: err("chat-error"),
      health: err("health-meta"),
    },
    chatStageWidth: chat ? Math.round(chat.getBoundingClientRect().width) : 0,
    windowWidth: window.innerWidth,
  };
})()
```

The same script lives in `tools/ux_drive/state.js`.

## Gallery

```
tests/artifacts/ux/<run-id>/
  INDEX.md
  STATE.json
  01-setup-empty.png
  FINDINGS.md
```

```bash
python -m tools.ux_drive gallery init --run-id 2026-08-24-kit-allocation
python -m tools.ux_drive gallery add setup-empty --file /tmp/shot.png
python -m tools.ux_drive gallery note "Opening project picker"
```

`tests/artifacts/` is gitignored.

## Fallback CLI

Only if Browser MCP is missing:

```bash
python -m tools.ux_drive start --url http://127.0.0.1:9001
python -m tools.ux_drive shot setup-empty
python -m tools.ux_drive state
python -m tools.ux_drive select-skill "Business Requirement Analysis"
python -m tools.ux_drive select-project IT-asset-management-system
python -m tools.ux_drive send "Add onboarding kit allocation"
python -m tools.ux_drive wait assistant-idle
python -m tools.ux_drive choose "New hires"
python -m tools.ux_drive click "#approve-btn"
python -m tools.ux_drive confirm accept
python -m tools.ux_drive stop
```

Requires: `pip install playwright && playwright install chromium`

## Optional CI smoke

Not the UX loop. `pytest -m e2e` runs a mocked selector/gallery smoke (no OpenRouter). Regular `pytest` stays the API unit suite.
