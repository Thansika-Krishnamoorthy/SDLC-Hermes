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
