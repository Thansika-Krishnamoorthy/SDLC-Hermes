const STAGES = ["setup", "interview", "review", "done"];
const DEFAULT_PLACEHOLDER = "Type a message";

const state = {
  currentPath: "",
  selectedProject: "",
  sessionId: null,
  brdMarkdown: "",
  featureName: "",
  approved: false,
  intendedSavePath: "",
  mode: null,
};

const $ = (id) => document.getElementById(id);

function showError(id, message) {
  const el = $(id);
  el.hidden = !message;
  el.textContent = message || "";
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      detail = await response.text();
    }
    throw new Error(detail);
  }
  return response.json();
}

function setStage(stage) {
  const stepper = $("stage-stepper");
  if (!stepper) return;
  const activeIndex = STAGES.indexOf(stage);
  stepper.querySelectorAll("li[data-stage]").forEach((li) => {
    const idx = STAGES.indexOf(li.dataset.stage);
    li.classList.toggle("is-active", li.dataset.stage === stage);
    li.classList.toggle("is-complete", idx >= 0 && idx < activeIndex);
  });
}

function setMode(mode) {
  const banner = $("mode-banner");
  const text = $("mode-banner-text");
  if (mode === "modify") {
    text.textContent = "Describe changes to the BRD below.";
    $("chat-input").placeholder = "Describe the BRD change…";
  } else if (mode === "add") {
    text.textContent = "Describe the new requirement.";
    $("chat-input").placeholder = "Describe the new requirement…";
  }
  banner.hidden = false;
  state.mode = mode;
  $("chat-input").focus();
}

function clearMode() {
  const banner = $("mode-banner");
  if (banner) banner.hidden = true;
  state.mode = null;
  $("chat-input").placeholder = DEFAULT_PLACEHOLDER;
}

function updateTranscriptCount() {
  const summary = $("transcript-summary");
  if (!summary) return;
  const count = $("transcript").children.length;
  summary.textContent = `Interview history (${count} message${count === 1 ? "" : "s"})`;
}

function scrollTranscriptToBottom() {
  const panel = document.querySelector(".transcript-panel");
  if (panel) panel.scrollTop = panel.scrollHeight;
}

function collapseStaleAssistantRounds() {
  for (const item of $("transcript").querySelectorAll(".bubble.assistant")) {
    if (item.querySelector(".round-collapsed")) continue;
    if (item.querySelector(".round-stage")) {
      collapseAssistantBubble(item, "Submitted answers");
      continue;
    }
    const choices = item.querySelector(".choices");
    if (!choices) continue;
    const selected = choices.querySelector(".choice.selected");
    const label = selected?.textContent?.trim();
    collapseAssistantBubble(item, label ? `Answered: ${label}` : "Round completed");
  }
}

function collapseAssistantBubble(item, summaryText) {
  item.querySelectorAll(".choices, .round-stage, .round-progress").forEach((el) => el.remove());
  let summary = item.querySelector(".round-collapsed");
  if (!summary) {
    summary = document.createElement("p");
    summary.className = "round-collapsed";
    item.appendChild(summary);
  }
  summary.textContent = summaryText;
}

function folderName(path) {
  if (!path) return "Select project";
  const parts = path.replace(/\\/g, "/").split("/").filter(Boolean);
  return parts[parts.length - 1] || path;
}

function setSelectedProject(path) {
  state.selectedProject = path;
  $("project-label").textContent = path ? folderName(path) : "Select project";
  $("project-label").title = path || "Select project";
}

function renderSkills(skills) {
  const select = $("skill-select");
  select.innerHTML = "";
  if (!skills.length) {
    select.innerHTML = '<option value="">No skills found</option>';
    return;
  }
  for (const skill of skills) {
    const option = document.createElement("option");
    option.value = skill.id;
    option.textContent = skill.name;
    option.title = skill.description || skill.name;
    select.appendChild(option);
  }
}

function selectedSkillIds() {
  const value = $("skill-select").value;
  return value ? [value] : [];
}

function addPickerItem(list, title, subtitle, onClick, selected) {
  const item = document.createElement("li");
  const button = document.createElement("button");
  button.type = "button";
  button.className = selected ? "picker-item selected" : "picker-item";
  button.innerHTML = `<strong></strong>${subtitle ? "<small></small>" : ""}`;
  button.querySelector("strong").textContent = title;
  if (subtitle) button.querySelector("small").textContent = subtitle;
  button.addEventListener("click", onClick);
  item.appendChild(button);
  list.appendChild(item);
}

async function loadRepos() {
  const data = await api("/api/repos");
  const list = $("repo-list");
  list.innerHTML = "";
  if (!data.repos.length) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "No Git repositories found under the browse root.";
    list.appendChild(empty);
    return;
  }
  for (const repo of data.repos) {
    addPickerItem(
      list,
      repo.name,
      repo.remote || repo.path,
      () => {
        setSelectedProject(repo.path);
        toggleProjectMenu(false);
      },
      repo.path === state.selectedProject,
    );
  }
}

async function loadBrowse(path) {
  const query = path ? `?path=${encodeURIComponent(path)}` : "";
  const data = await api(`/api/fs${query}`);
  state.currentPath = data.current;
  $("current-path").textContent = data.current;
  $("current-path").title = data.current;
  $("up-btn").disabled = !data.parent;
  $("up-btn").dataset.parent = data.parent || "";

  const list = $("folder-list");
  list.innerHTML = "";
  addPickerItem(list, `. (${folderName(data.current)})`, data.current, () => {
    setSelectedProject(data.current);
    toggleProjectMenu(false);
  }, data.current === state.selectedProject);
  for (const dir of data.directories) {
    const label = dir.is_git ? `${dir.name} (git)` : dir.name;
    addPickerItem(list, label, dir.path, () => {
      loadBrowse(dir.path);
    }, dir.path === state.selectedProject);
  }
}

function toggleProjectMenu(force) {
  const menu = $("project-menu");
  menu.hidden = force === undefined ? !menu.hidden : !force;
  $("project-toggle").setAttribute("aria-expanded", String(!menu.hidden));
}

function parseChoices(text) {
  const lines = text.split(/\n/);
  const optionRe = /^\s*(\d+)[\.)]\s+(.+?)\s*$/;
  const options = [];
  let start = -1;
  lines.forEach((line, index) => {
    const match = line.match(optionRe);
    if (match) {
      if (start < 0) start = index;
      options.push({ number: match[1], label: match[2] });
    }
  });
  if (options.length < 2) return { prompt: text, options: [] };
  const prompt = lines.slice(0, start).join("\n").trim() || text;
  return { prompt, options };
}

function parseRound(text) {
  const lines = text.split("\n");
  const questionRe = /^\s*(?:\*\*)?Q(\d+)[\.:)]\s*(?:\*\*)?\s*(.*)$/i;
  const starts = [];
  lines.forEach((line, index) => {
    const match = line.match(questionRe);
    if (match) starts.push({ index, n: match[1] });
  });
  if (starts.length < 2) {
    const single = parseChoices(text);
    return {
      intro: single.prompt,
      questions: single.options.length >= 2 ? [{ key: "Q1", title: single.prompt, options: single.options }] : [],
    };
  }
  const intro = lines.slice(0, starts[0].index).join("\n").trim();
  const questions = starts.map((start, i) => {
    const end = i + 1 < starts.length ? starts[i + 1].index : lines.length;
    const block = lines.slice(start.index, end).join("\n");
    const parsed = parseChoices(block);
    return {
      key: `Q${start.n}`,
      title: parsed.prompt || block.trim(),
      options: parsed.options,
    };
  });
  return { intro, questions };
}

function isControlRound(questions) {
  const labels = questions.flatMap((question) => question.options.map((option) => option.label.toLowerCase()));
  return labels.some((label) => label.includes("approve")) &&
    labels.some((label) => label.includes("modify") || label.includes("add more") || label.includes("new requirement"));
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatMarkdown(text) {
  let html = escapeHtml(text);
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([\s\S]+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__([^_]+?)__/g, "<strong>$1</strong>");
  html = html.replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, "$1<em>$2</em>");
  return html;
}

function inlineMarkdown(text) {
  return formatMarkdown(text);
}

function isTableRow(line) {
  const trimmed = line.trim();
  return trimmed.startsWith("|") && trimmed.endsWith("|");
}

function isTableSeparator(line) {
  if (!isTableRow(line)) return false;
  return line.trim().slice(1, -1).split("|").every((cell) => /^[\s\-:]+$/.test(cell.trim()));
}

function parseTableCells(line) {
  return line.trim().slice(1, -1).split("|").map((cell) => cell.trim());
}

function renderTable(tableLines) {
  const rows = tableLines.filter((line) => !isTableSeparator(line)).map(parseTableCells);
  if (!rows.length) return "";
  const [header, ...body] = rows;
  let html = '<div class="table-scroll"><table><thead><tr>';
  for (const cell of header) {
    html += `<th>${inlineMarkdown(cell)}</th>`;
  }
  html += "</tr></thead><tbody>";
  for (const row of body) {
    html += "<tr>";
    for (const cell of row) {
      html += `<td>${inlineMarkdown(cell)}</td>`;
    }
    html += "</tr>";
  }
  html += "</tbody></table></div>";
  return html;
}

function renderMarkdownDocument(text) {
  const lines = String(text || "").replace(/\r\n/g, "\n").split("\n");
  const html = [];
  let list = null;
  let i = 0;

  function closeList() {
    if (!list) return;
    html.push(list === "ol" ? "</ol>" : "</ul>");
    list = null;
  }

  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.trimEnd();

    if (isTableRow(line)) {
      closeList();
      const tableLines = [];
      while (i < lines.length && isTableRow(lines[i].trimEnd())) {
        tableLines.push(lines[i].trimEnd());
        i += 1;
      }
      html.push(renderTable(tableLines));
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      closeList();
      const level = heading[1].length;
      html.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      i += 1;
      continue;
    }
    const ul = line.match(/^[-*]\s+(.+)$/);
    if (ul) {
      if (list !== "ul") {
        closeList();
        html.push("<ul>");
        list = "ul";
      }
      html.push(`<li>${inlineMarkdown(ul[1])}</li>`);
      i += 1;
      continue;
    }
    const ol = line.match(/^\d+\.\s+(.+)$/);
    if (ol) {
      if (list !== "ol") {
        closeList();
        html.push("<ol>");
        list = "ol";
      }
      html.push(`<li>${inlineMarkdown(ol[1])}</li>`);
      i += 1;
      continue;
    }
    if (!line.trim()) {
      closeList();
      i += 1;
      continue;
    }
    closeList();
    html.push(`<p>${inlineMarkdown(line)}</p>`);
    i += 1;
  }
  closeList();
  return html.join("");
}

function containsBrd(text) {
  return /```brd/i.test(text) || /#\s+Business Requirements Document/i.test(text);
}

function setFormattedText(el, text) {
  el.innerHTML = formatMarkdown(text || "");
}

function addBubble(role, text, display) {
  $("empty-state").hidden = true;
  const item = document.createElement("li");
  item.className = `bubble ${role}`;
  if (role === "assistant") {
    renderAssistant(item, text);
  } else if (display && display.type === "round-summary") {
    renderRoundSummary(item, display.items);
  } else {
    item.textContent = text;
  }
  $("transcript").appendChild(item);
  updateTranscriptCount();
  scrollTranscriptToBottom();
  return item;
}

function renderRoundSummary(item, items) {
  const heading = document.createElement("p");
  heading.className = "summary-heading";
  heading.textContent = "Round summary";
  const list = document.createElement("ul");
  list.className = "round-summary";
  for (const entry of items) {
    const li = document.createElement("li");
    const question = document.createElement("div");
    question.className = "summary-q";
    setFormattedText(question, entry.question);
    const answer = document.createElement("div");
    answer.className = "summary-a";
    setFormattedText(answer, entry.answer);
    li.appendChild(question);
    li.appendChild(answer);
    list.appendChild(li);
  }
  item.appendChild(heading);
  item.appendChild(list);
}

function renderChoices(container, options, onPick) {
  const choices = document.createElement("div");
  choices.className = "choices";
  for (const option of options) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "choice";
    setFormattedText(button, option.label);
    button.addEventListener("click", () => onPick(option, button, choices));
    choices.appendChild(button);
  }
  container.appendChild(choices);
  return choices;
}

function renderAssistant(item, text) {
  item.innerHTML = "";
  if (containsBrd(text)) {
    const prompt = document.createElement("p");
    prompt.className = "prompt";
    prompt.textContent = "The BRD draft is ready below. Use Approve BRD, Modify BRD, or Add requirements in that panel.";
    item.appendChild(prompt);
    return;
  }
  const round = parseRound(text);
  const multi = round.questions.length >= 2 && !isControlRound(round.questions);
  const prompt = document.createElement("p");
  prompt.className = "prompt";
  setFormattedText(prompt, multi ? (round.intro || "Answer one question at a time.") : (round.intro || text));
  item.appendChild(prompt);
  if (!round.questions.length) return;

  if (!multi) {
    renderChoices(item, round.questions[0].options, async (option, button, group) => {
      if (button.disabled) return;
      for (const child of group.querySelectorAll("button")) child.disabled = true;
      const other = /other/i.test(option.label);
      if (other) {
        $("chat-input").value = "";
        $("chat-input").placeholder = "Type your own answer…";
        $("chat-input").focus();
        return;
      }
      const label = option.label.toLowerCase();
      collapseAssistantBubble(item, `Answered: ${option.label}`);
      if (label.includes("approve")) {
        await completeApproval();
        return;
      }
      if (label.includes("add more") || label.includes("new requirement")) {
        startNewRequirement();
        return;
      }
      if (label.includes("modify")) {
        setMode("modify");
        return;
      }
      try {
        await sendChat(`${option.number}. ${option.label}`);
      } catch (error) {
        showError("chat-error", error.message);
      }
    });
    return;
  }

  const answers = {};
  const progress = document.createElement("p");
  progress.className = "round-progress";
  const stage = document.createElement("div");
  stage.className = "round-stage";
  item.appendChild(progress);
  item.appendChild(stage);

  async function submitRound() {
    stage.querySelectorAll("button, input").forEach((el) => {
      el.disabled = true;
    });
    collapseAssistantBubble(item, `Submitted ${round.questions.length} answers`);
    const items = [];
    const lines = ["Round answers:"];
    for (const question of round.questions) {
      const answer = answers[question.key];
      const questionText = question.title.replace(/^\s*Q\d+[\.:)]\s*/i, "").trim();
      const value = answer.other && answer.detail
        ? `Other: ${answer.detail}`
        : `${answer.number}. ${answer.label}`;
      items.push({
        question: questionText,
        answer: answer.other && answer.detail ? answer.detail : answer.label,
      });
      lines.push(`${question.key}. ${questionText}\n→ ${value}`);
    }
    try {
      await sendChat(lines.join("\n"), { type: "round-summary", items });
    } catch (error) {
      showError("chat-error", error.message);
    }
  }

  function showQuestion(index) {
    const question = round.questions[index];
    progress.textContent = `Question ${index + 1} of ${round.questions.length}`;
    stage.innerHTML = "";
    const heading = document.createElement("p");
    heading.className = "question-title";
    setFormattedText(heading, question.title);
    stage.appendChild(heading);
    const otherInput = document.createElement("input");
    otherInput.type = "text";
    otherInput.className = "other-input";
    otherInput.placeholder = "Please specify…";
    otherInput.hidden = true;
    const nextBtn = document.createElement("button");
    nextBtn.type = "button";
    nextBtn.className = "round-continue";
    nextBtn.textContent = index === round.questions.length - 1 ? "Send this round" : "Next question";
    nextBtn.hidden = true;

    function goNext() {
      const answer = answers[question.key];
      if (!answer || (answer.other && !answer.detail)) return;
      if (index + 1 < round.questions.length) {
        showQuestion(index + 1);
      } else {
        submitRound();
      }
    }

    otherInput.addEventListener("input", () => {
      if (!answers[question.key]) return;
      answers[question.key].detail = otherInput.value.trim();
      nextBtn.disabled = !answers[question.key].detail;
    });
    otherInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        goNext();
      }
    });
    nextBtn.addEventListener("click", goNext);

    renderChoices(stage, question.options, (option, button, group) => {
      for (const child of group.querySelectorAll("button")) child.classList.remove("selected");
      button.classList.add("selected");
      const other = /other/i.test(option.label);
      answers[question.key] = {
        number: option.number,
        label: option.label,
        other,
        detail: other ? otherInput.value.trim() : "",
      };
      otherInput.hidden = !other;
      nextBtn.hidden = !other;
      nextBtn.disabled = other && !otherInput.value.trim();
      if (other) {
        otherInput.focus();
        return;
      }
      goNext();
    });
    stage.appendChild(otherInput);
    stage.appendChild(nextBtn);
  }

  showQuestion(0);
}

function hideBrd(status) {
  $("brd-card").hidden = true;
  $("brd-preview").innerHTML = "";
  $("brd-status").textContent = "";
  $("save-path").textContent = "";
  state.intendedSavePath = "";
  $("chat-stage")?.classList.remove("review-mode");
  const history = $("transcript-history");
  if (history) history.setAttribute("open", "");
  if (status) $("brd-status").textContent = status;
}

function stripBrdFromTranscript() {
  for (const item of $("transcript").querySelectorAll(".bubble.assistant")) {
    const prompt = item.querySelector(".prompt") || item;
    const text = prompt.textContent || "";
    if (!/```brd/i.test(text) && !/#\s+Business Requirements Document/i.test(text)) {
      continue;
    }
    item.innerHTML = "";
    const p = document.createElement("p");
    p.className = "prompt";
    p.textContent = "Approved BRD hidden from this view. It is saved in the selected project’s docs folder.";
    item.appendChild(p);
  }
}

async function loadBrdPreview() {
  if (!state.sessionId) return;
  const params = new URLSearchParams();
  if (state.brdMarkdown) params.set("markdown", state.brdMarkdown);
  if (state.featureName) params.set("feature_name", state.featureName);
  const query = params.toString() ? `?${params.toString()}` : "";
  try {
    const preview = await api(`/api/sessions/${state.sessionId}/brd/preview${query}`);
    state.intendedSavePath = preview.relative;
    $("save-path").textContent = `Will save to: ${preview.relative}`;
  } catch (error) {
    state.intendedSavePath = "";
    $("save-path").textContent = "";
    showError("chat-error", error.message);
  }
}

async function showBrd(markdown, featureName) {
  if (state.approved) {
    hideBrd();
    return;
  }
  state.brdMarkdown = markdown || "";
  state.featureName = featureName || "";
  $("brd-card").hidden = !markdown;
  $("brd-preview").innerHTML = markdown ? renderMarkdownDocument(markdown) : "";
  $("brd-status").textContent = markdown
    ? `Draft ready${featureName ? ` — ${featureName}` : ""}`
    : "";

  if (markdown) {
    setStage("review");
    $("chat-stage")?.classList.add("review-mode");
    const history = $("transcript-history");
    if (history) history.removeAttribute("open");
    await loadBrdPreview();
  } else {
    $("chat-stage")?.classList.remove("review-mode");
    state.intendedSavePath = "";
    $("save-path").textContent = "";
  }
}

async function consumeStream(response, bubble) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let assembled = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() || "";
    for (const chunk of chunks) {
      const line = chunk.split("\n").find((row) => row.startsWith("data:"));
      if (!line) continue;
      const payload = JSON.parse(line.slice(5).trim());
      if (payload.error) throw new Error(payload.error);
      if (payload.token) {
        assembled += payload.token;
        const prompt = bubble.querySelector(".prompt") || bubble;
        prompt.classList.remove("waiting");
        if (containsBrd(assembled)) {
          prompt.textContent = "Writing the BRD draft…";
        } else {
          setFormattedText(prompt, assembled);
        }
        scrollTranscriptToBottom();
      }
      if (payload.done) {
        renderAssistant(bubble, assembled);
        scrollTranscriptToBottom();
        if (payload.brd) await showBrd(payload.brd, payload.feature_name);
      }
    }
  }
  if (assembled) {
    renderAssistant(bubble, assembled);
    scrollTranscriptToBottom();
  }
}

async function ensureSession(opening) {
  if (state.sessionId) return;
  const skillIds = selectedSkillIds();
  if (!skillIds.length) throw new Error("Choose a skill from the dropdown.");
  if (!state.selectedProject) throw new Error("Choose a project folder from the dropdown.");
  const session = await api("/api/sessions", {
    method: "POST",
    body: JSON.stringify({
      skill_ids: skillIds,
      project_path: state.selectedProject,
      opening_message: opening,
    }),
  });
  state.sessionId = session.id;
  state.approved = false;
  setStage("interview");
}

async function sendChat(text, display) {
  showError("chat-error", "");
  showError("setup-error", "");
  clearMode();
  collapseStaleAssistantRounds();
  await ensureSession(text);
  addBubble("user", text, display);
  const bubble = addBubble("assistant", "Preparing the next round…");
  const waiting = bubble.querySelector(".prompt");
  if (waiting) waiting.classList.add("waiting");
  const response = await fetch(`/api/sessions/${state.sessionId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: text }),
  });
  if (!response.ok) throw new Error("Chat request failed");
  await consumeStream(response, bubble);
}

async function init() {
  setStage("setup");
  const health = await api("/api/health");
  const meta = $("health-meta");
  if (meta) {
    if (!health.api_key_configured) {
      meta.hidden = false;
      meta.className = "error banner health-meta";
      meta.textContent =
        "OpenRouter API key not configured — chat will fail. Set OPENROUTER_API_KEY in .env";
    } else {
      meta.hidden = true;
      meta.textContent = "";
    }
  }
  const skills = await api("/api/skills");
  renderSkills(skills.skills);
  await loadRepos();
  await loadBrowse();
}

$("project-toggle").addEventListener("click", (event) => {
  event.stopPropagation();
  toggleProjectMenu();
});

$("project-menu").addEventListener("click", (event) => event.stopPropagation());

document.addEventListener("click", () => {
  if (!$("project-menu").hidden) toggleProjectMenu(false);
});

$("up-btn").addEventListener("click", () => {
  if ($("up-btn").dataset.parent) loadBrowse($("up-btn").dataset.parent);
});

$("select-dir-btn").addEventListener("click", () => {
  setSelectedProject(state.currentPath);
  toggleProjectMenu(false);
});

$("create-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  showError("setup-error", "");
  try {
    const created = await api("/api/projects", {
      method: "POST",
      body: JSON.stringify({ parent: state.currentPath, name: $("new-folder").value }),
    });
    $("new-folder").value = "";
    await loadBrowse(state.currentPath);
    await loadRepos();
    setSelectedProject(created.path);
    toggleProjectMenu(false);
  } catch (error) {
    showError("setup-error", error.message);
  }
});

$("chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("chat-input");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  try {
    await sendChat(text);
  } catch (error) {
    showError("setup-error", error.message);
  }
});

async function saveBrd() {
  return api(`/api/sessions/${state.sessionId}/brd`, {
    method: "POST",
    body: JSON.stringify({ markdown: state.brdMarkdown, feature_name: state.featureName }),
  });
}

$("approve-btn").addEventListener("click", async () => {
  try {
    await completeApproval();
  } catch (error) {
    showError("chat-error", error.message);
  }
});

$("modify-btn").addEventListener("click", () => {
  setMode("modify");
});

$("more-btn").addEventListener("click", () => {
  startNewRequirement();
});

$("mode-cancel-btn").addEventListener("click", () => {
  clearMode();
});

async function completeApproval() {
  if (!state.sessionId) throw new Error("Start an interview before approving a BRD.");
  const path = state.intendedSavePath || "the project docs folder";
  if (!confirm(`Approve and save BRD to:\n${path}\n\nThis ends the current interview.`)) return;
  clearMode();
  const saved = await saveBrd();
  const result = await api(`/api/sessions/${state.sessionId}/approve`, { method: "POST", body: "{}" });
  state.approved = true;
  state.sessionId = null;
  state.brdMarkdown = "";
  state.featureName = "";
  state.intendedSavePath = "";
  hideBrd();
  stripBrdFromTranscript();
  setStage("done");
  addBubble("assistant", `${result.message}\nSaved to ${result.path || saved.path}`);
}

function startNewRequirement() {
  hideBrd();
  clearMode();
  state.sessionId = null;
  state.approved = false;
  state.brdMarkdown = "";
  state.featureName = "";
  state.intendedSavePath = "";
  setStage("interview");
  setMode("add");
  addBubble("assistant", "Describe the new requirement. A separate BRD will be created for that feature.");
}

init().catch((error) => showError("setup-error", error.message));
