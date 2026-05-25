const API_BASE = "https://ves-on-set-d8co3.ondigitalocean.app/api/v1";

const dom = {
  form: document.getElementById("searchForm"),
  queryInput: document.getElementById("queryInput"),
  toggleAllBtn: document.getElementById("toggleAllBtn"),
  status: document.getElementById("status"),
  allOptionsPanel: document.getElementById("allOptionsPanel"),
  allOptionsList: document.getElementById("allOptionsList"),
  resultPanel: document.getElementById("resultPanel"),
  suggestionsPanel: document.getElementById("suggestionsPanel"),
  suggestionsList: document.getElementById("suggestionsList"),
  datasetTitle: document.getElementById("datasetTitle"),
  datasetMeta: document.getElementById("datasetMeta"),
  creatorsList: document.getElementById("creatorsList"),
  consumersList: document.getElementById("consumersList"),
};

let datasetItems = [];
let inputDebounce = null;
let allOptionsVisible = false;

function setStatus(text) {
  dom.status.textContent = text;
}

function stripLeadingId(text) {
  return String(text || "")
    .replace(/^\s*\d+(?:\.\d+)*\s+/, "")
    .trim();
}

function displayName(item) {
  return stripLeadingId(item.name || item.title || "");
}

function label(item) {
  return displayName(item);
}

function norm(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "");
}

function renderList(ul, names) {
  ul.innerHTML = "";
  if (!names.length) {
    const li = document.createElement("li");
    li.textContent = "None";
    ul.appendChild(li);
    return;
  }

  names.forEach((name) => {
    const li = document.createElement("li");
    li.textContent = name;
    ul.appendChild(li);
  });
}

async function loadDataSets() {
  setStatus("Loading keywords...");
  const res = await fetch(`${API_BASE}/data-sets`);
  if (!res.ok) {
    throw new Error(`Failed to load list: ${res.status}`);
  }

  const payload = await res.json();
  datasetItems = payload.data || [];
  datasetItems.sort((a, b) =>
    label(a).localeCompare(label(b), undefined, { numeric: true }),
  );

  setStatus(
    `Loaded ${datasetItems.length} keywords. Enter a query to search.`,
  );
}

function clearSuggestions() {
  dom.suggestionsList.innerHTML = "";
  dom.suggestionsPanel.hidden = true;
}

function renderAllOptions() {
  dom.allOptionsList.innerHTML = "";

  datasetItems.forEach((item) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.className = "suggestion-btn";
    btn.type = "button";
    btn.textContent = label(item);
    btn.addEventListener("click", () => {
      dom.queryInput.value = displayName(item);
      dom.resultPanel.hidden = true;
      clearSuggestions();
      loadDependencies(item.slug);
    });
    li.appendChild(btn);
    dom.allOptionsList.appendChild(li);
  });
}

function setAllOptionsVisible(visible) {
  allOptionsVisible = visible;
  dom.allOptionsPanel.hidden = !visible;
  dom.toggleAllBtn.textContent = visible
    ? "Hide all options"
    : "Show all options";
  dom.toggleAllBtn.setAttribute("aria-expanded", String(visible));

  if (visible && !dom.allOptionsList.childElementCount) {
    renderAllOptions();
  }
}

function showSuggestions(matches) {
  dom.suggestionsList.innerHTML = "";
  matches.slice(0, 8).forEach((item) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.className = "suggestion-btn";
    btn.type = "button";
    btn.textContent = label(item);
    btn.addEventListener("click", () => {
      dom.queryInput.value = displayName(item);
      clearSuggestions();
      loadDependencies(item.slug);
    });
    li.appendChild(btn);
    dom.suggestionsList.appendChild(li);
  });
  dom.suggestionsPanel.hidden = false;
}

function searchMatches(query, limit = 6) {
  const q = query.trim();
  if (!q) return [];

  const lower = q.toLowerCase();
  const compact = norm(q);

  const starts = datasetItems.filter(
    (d) =>
      norm(d.name).startsWith(compact) ||
      norm(d.title).startsWith(compact) ||
      String(d.id || "")
        .toLowerCase()
        .startsWith(lower),
  );

  const partial = datasetItems.filter(
    (d) =>
      norm(d.name).includes(compact) ||
      norm(d.title).includes(compact) ||
      String(d.id || "")
        .toLowerCase()
        .includes(lower),
  );

  const merged = [...starts, ...partial];
  const unique = [];
  const seen = new Set();

  merged.forEach((item) => {
    if (seen.has(item.slug)) return;
    seen.add(item.slug);
    unique.push(item);
  });

  return unique.slice(0, limit);
}

function findDataset(query) {
  const q = query.trim();
  if (!q) return { type: "empty" };

  const lower = q.toLowerCase();
  const compact = norm(q);

  let exact = datasetItems.find((d) => d.slug === lower);
  if (!exact)
    exact = datasetItems.find(
      (d) => String(d.id || "").toLowerCase() === lower,
    );
  if (!exact)
    exact = datasetItems.find(
      (d) => norm(d.name) === compact || norm(d.title) === compact,
    );
  if (exact) return { type: "single", item: exact };

  const partial = datasetItems.filter(
    (d) =>
      norm(d.name).includes(compact) ||
      norm(d.title).includes(compact) ||
      String(d.id || "")
        .toLowerCase()
        .includes(lower),
  );

  if (partial.length === 1) return { type: "single", item: partial[0] };
  if (partial.length > 1) return { type: "many", items: partial };
  return { type: "none" };
}

async function loadDependencies(slug) {
  setStatus("Loading dependencies...");
  const res = await fetch(
    `${API_BASE}/data-sets/${encodeURIComponent(slug)}/dependencies`,
  );
  if (!res.ok) {
    throw new Error(`Failed to load dependencies: ${res.status}`);
  }

  const payload = await res.json();
  const data = payload.data || {};
  const dataset = data.dataset || {};
  const deps = data.dependencies || {};

  dom.datasetTitle.textContent = stripLeadingId(
    dataset.title || dataset.name || slug,
  );
  dom.datasetMeta.textContent = dataset.category
    ? `Category: ${dataset.category}`
    : "";

  const creators = (deps.inbound || [])
    .map((edge) => edge.from?.name)
    .filter(Boolean);
  const consumers = (deps.outbound || [])
    .map((edge) => edge.to?.name)
    .filter(Boolean);

  renderList(dom.creatorsList, creators);
  renderList(dom.consumersList, consumers);

  dom.resultPanel.hidden = false;
  setStatus("");
}

async function init() {
  try {
    await loadDataSets();
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  }
}

dom.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  dom.resultPanel.hidden = true;
  clearSuggestions();

  const result = findDataset(dom.queryInput.value);

  if (result.type === "empty") {
    setStatus("Type a keyword first.");
    return;
  }

  if (result.type === "none") {
    setStatus("No keyword found. Try a broader query.");
    return;
  }

  if (result.type === "many") {
    setStatus(`Found ${result.items.length} matches.`);
    showSuggestions(result.items);
    return;
  }

  try {
    await loadDependencies(result.item.slug);
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  }
});

dom.toggleAllBtn.addEventListener("click", () => {
  setAllOptionsVisible(!allOptionsVisible);
});

dom.queryInput.addEventListener("input", () => {
  if (inputDebounce) {
    clearTimeout(inputDebounce);
  }

  inputDebounce = setTimeout(() => {
    const value = dom.queryInput.value.trim();

    if (!value) {
      clearSuggestions();
      setStatus(
        `Loaded ${datasetItems.length} keywords. Enter a query to search.`,
      );
      return;
    }

    const matches = searchMatches(value);
    if (!matches.length) {
      clearSuggestions();
      setStatus("No quick matches yet. Keep typing or press Enter.");
      return;
    }

    showSuggestions(matches);
    setStatus(`Suggestions: ${matches.length}. Press Enter to search.`);
  }, 120);
});

init();
