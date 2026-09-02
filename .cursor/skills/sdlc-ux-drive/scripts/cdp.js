/**
 * Paste one IIFE into browser_cdp Runtime.evaluate with returnByValue: true.
 * Replace NEEDLE with a live substring from state.choices (not a memorized label).
 */

export const stateNote = "Prefer tools/ux_drive/state.js for stage/choices/waiting/brdVisible/widths.";

export const roundInfo = `(() => {
  const visible = (el) => !!(el && !el.hidden && el.offsetParent !== null);
  const box = document.querySelector(".choices");
  const r = box?.getBoundingClientRect();
  return {
    progress: document.querySelector(".round-progress")?.textContent || null,
    title: document.querySelector(".question-title")?.innerText || "",
    choices: [...document.querySelectorAll("button.choice")]
      .filter((el) => !el.disabled && visible(el))
      .map((el) => (el.textContent || "").trim()),
    inView: r ? r.top < innerHeight && r.bottom > 0 : false,
    choiceTop: r ? Math.round(r.top) : null,
    windowH: innerHeight,
  };
})()`;

export const clickChoice = `(() => {
  const needle = "NEEDLE";
  const b = [...document.querySelectorAll("button.choice")].find(
    (el) => !el.disabled && (el.textContent || "").includes(needle),
  );
  if (!b) return { ok: false, error: "no match", needle };
  b.click();
  return { ok: true, clicked: (b.textContent || "").trim() };
})()`;

export const clickFirstNonOther = `(() => {
  const b = [...document.querySelectorAll("button.choice")].find(
    (el) => !el.disabled && el.offsetParent && !/other/i.test(el.textContent || ""),
  );
  if (!b) return { ok: false };
  b.click();
  return { ok: true, clicked: (b.textContent || "").trim() };
})()`;

export const pickerRepos = `(() => {
  const menu = document.getElementById("project-menu");
  return {
    open: !!(menu && !menu.hidden),
    repos: [...document.querySelectorAll("#repo-list button")].map((el) =>
      (el.textContent || "").replace(/\\s+/g, " ").trim(),
    ),
  };
})()`;

export const clickRepo = `(() => {
  const needle = "NEEDLE";
  const b = [...document.querySelectorAll("#repo-list button")].find((el) =>
    (el.textContent || "").toLowerCase().includes(needle.toLowerCase()),
  );
  if (!b) return { ok: false, error: "no repo", needle };
  b.click();
  return { ok: true, clicked: (b.textContent || "").trim() };
})()`;

export const scrollChoices = `(() => {
  const el = document.querySelector(".choices") || document.querySelector(".round-stage");
  el?.scrollIntoView({ block: "center" });
  const panel = document.querySelector(".transcript-panel");
  if (panel) panel.scrollTop = panel.scrollHeight;
  return { scrolled: !!el };
})()`;

export const confirmAndApprove = `(() => {
  window.confirm = () => true;
  const btn = document.getElementById("approve-btn");
  if (!btn) return { ok: false, error: "no approve-btn" };
  btn.click();
  return { ok: true };
})()`;
