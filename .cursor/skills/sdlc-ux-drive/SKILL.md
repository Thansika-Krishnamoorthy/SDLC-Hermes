---
name: sdlc-ux-drive
description: Drive live SDLC Skill Runner UX testing as a Cursor agent — CDP-first, few screenshots, live choice clicks. Use when the user asks to test usability, walk the interview/BRD UI, take screenshots, use @Browser, or fall back to Playwright ux_drive.
---

# SDLC UX drive (fast path)

You are the tester. Invent a short concrete business need. Pick **live** `button.choice` labels (never hardcoded option lists). Do not mock OpenRouter unless `pytest -m e2e`.

Human playbook (not this loop): `docs/UX-DRIVE.md`. Snippets: [scripts/cdp.js](scripts/cdp.js). Selectors/CLI: [reference.md](reference.md). Compact state: `tools/ux_drive/state.js`.

## Harness

- If the user tagged `@Browser`, **call** `cursor-ide-browser` immediately. Catalog/`GetDynamicTools` often returns empty; tools still work.
- `browser_tabs` list → `select` the `http://127.0.0.1:9001/` (or `:8000`) tab → `browser_lock`. Pass that **`viewId` on every later call**. Never fill/click unlocked (fill can land on a second Skill Runner tab).
- Do **not** start `python -m tools.ux_drive start` in the same run as Browser.
- Confirm uvicorn is up (`curl` 200). `gallery init --run-id <short-id>`.

## Sense (CDP first)

Default: `browser_cdp` `Runtime.evaluate` of `tools/ux_drive/state.js` with `returnByValue: true`.

Use [scripts/cdp.js](scripts/cdp.js) for: choices + progress + inView, click-by-text, picker click, scroll `.choices`, confirm+approve.

`browser_snapshot` **only** at setup (refs for skill/project/chat) or if CDP fails. Interview snapshots are huge and **omit choice buttons** as interactive refs — do not wait for them.

Ignore snapshot nodes for collapsed picker lists and hidden BRD.

## Act

1. Setup shot. Open picker; CDP-click `#repo-list button` by name. If snapshot click is intercepted by `#transcript`, pick a **visible** (top) repo once — do not retry the same intercepted ref.
2. Shot project selected. Fill opening need + Send on the **locked** tab.
3. Poll state in the **same turn** after Send (`waiting`, then `choices` or `brdVisible`). Do not sleep 8–15s first. A few short polls; if stuck, one waiting/error screenshot.
4. Interview: CDP click first sensible **non-Other** live choice. Multi-Q round: Q2–Qn via CDP **with no extra screenshots**. After last click, poll until `waiting === false`.
5. After a round, if `.choices` `inView === false`, `scrollIntoView` before the next shot.
6. Stop interviewing once `brdVisible`. Shot BRD (tables if any, sticky actions, `#save-path`, `#chat-stage` width vs window). Shot modify banner once, Cancel. Then approve: `window.confirm = () => true` then `#approve-btn.click()`. Shot done.
7. `FINDINGS.md` from this run. Unlock. Gallery `add` **in parallel** with the next Browser call.

## Screenshot budget (~6)

setup · project selected · first idle round · BRD review · modify banner · done

Skip per-question and picker-open shots unless a bug is on screen.

## Traps (workaround, don’t rediscover)

- Picker vs `#transcript` intercept; document click closes the menu.
- Choice buttons missing from the a11y tree.
- Next round below the fold after collapse.
- Hidden picker/BRD still listed in snapshots.
