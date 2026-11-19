const button = document.querySelector("#check");
const summary = document.querySelector("#summary");
const checkedAt = document.querySelector("#checked-at");
const rows = new Map(
  Array.from(document.querySelectorAll("[data-check]"), (node) => [node.dataset.check, node])
);
const messages = {
  "Connection failed or timed out": "Нет соединения или истекло время ожидания",
  "Tracker page was not found": "Страница Tracker не найдена",
  "GraphQL did not return a task list": "GraphQL не вернул список задач",
  "Record API did not report readiness": "Record API не подтвердил готовность",
};

button.addEventListener("click", async () => {
  button.disabled = true;
  summary.textContent = "Проверяю Tracker…";
  checkedAt.hidden = true;
  for (const row of rows.values()) {
    delete row.dataset.state;
    row.textContent = "Проверка…";
  }

  try {
    const response = await fetch("/api/tracker/check", { cache: "no-store" });
    if (!response.ok) throw new Error("Dashboard request failed");
    const report = await response.json();
    const checks = new Map(report.checks.map((check) => [check.name, check]));
    for (const [name, row] of rows) {
      const check = checks.get(name);
      row.dataset.state = check?.ok ? "pass" : "fail";
      row.textContent = check?.ok ? "Работает" : (messages[check?.detail] ?? check?.detail ?? "Нет результата");
    }
    if (report.ok) {
      summary.textContent = "Tracker доступен";
    } else {
      summary.textContent = report.checks.some((check) => check.ok)
        ? "Часть проверок не прошла"
        : "Tracker недоступен";
    }
    checkedAt.textContent = "Проверено в " + new Date().toLocaleTimeString();
    checkedAt.hidden = false;
  } catch {
    summary.textContent = "Дашборд не получил результат проверки";
    for (const row of rows.values()) {
      delete row.dataset.state;
      row.textContent = "Нет результата";
    }
  } finally {
    button.disabled = false;
  }
});

const formatGiB = new Intl.NumberFormat("ru", { maximumFractionDigits: 2 });
const formatPercent = new Intl.NumberFormat("ru", { maximumFractionDigits: 1 });
const gib = (value) => Number.isFinite(value) ? formatGiB.format(value / 2 ** 30) : "—";
const ratio = (part, total) => `${gib(part)} из ${gib(total)} ГиБ`;

function element(tag, text) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  return node;
}

function displayMetrics(name, entries) {
  const list = document.querySelector(`#${name}-metrics`);
  list.replaceChildren(...entries.map(([label, value]) => {
    const metric = element("div");
    metric.append(element("dt", label), element("dd", value));
    return metric;
  }));
}

function displaySampleTime(name, snapshot) {
  const note = document.querySelector(`#${name}-age`);
  delete note.dataset.state;
  note.textContent = snapshot
    ? `Последний замер: ${new Date(snapshot.collected_at).toLocaleString("ru")}`
    : "Нет замера";
}

function displayProjects(projects) {
  const target = document.querySelector("#projects");
  if (!projects?.length) {
    const note = element("p", projects ? "Контейнеров нет" : "Нет данных Docker");
    note.className = "metric-note";
    target.replaceChildren(note);
    return;
  }

  target.replaceChildren(...projects.map((project) => {
    const wrapper = element("div");
    wrapper.className = "project";
    wrapper.append(element("h3", project.name ?? "Вне Compose"));
    const scroll = element("div");
    scroll.className = "table-scroll";
    const table = element("table");
    table.setAttribute("aria-label", project.name ?? "Вне Compose");
    const header = table.createTHead().insertRow();
    for (const title of ["Контейнер", "Состояние", "CPU", "RAM"]) {
      const cell = element("th", title);
      cell.scope = "col";
      header.append(cell);
    }
    const body = table.createTBody();
    for (const container of project.containers) {
      const row = body.insertRow();
      const completed = container.state === "exited" && container.status.startsWith("Exited (0)");
      const unhealthy = container.status.includes("(unhealthy)");
      row.insertCell().textContent = container.name;
      const status = row.insertCell();
      status.textContent = completed ? "Завершён успешно" : container.status;
      status.dataset.state = unhealthy ? "unhealthy" : container.state;
      row.insertCell().textContent = container.cpu ?? "—";
      row.insertCell().textContent = container.memory ?? "—";
    }
    scroll.append(table);
    wrapper.append(scroll);
    return wrapper;
  }));
}

function displaySnapshot(source, sample) {
  const snapshot = sample?.snapshot;
  if (source === "windows") {
    displayMetrics(source, snapshot ? [
      ["Загрузка CPU", Number.isFinite(snapshot.cpu_percent) ? `${formatPercent.format(snapshot.cpu_percent)}%` : "—"],
      ["Доступная RAM", ratio(snapshot.memory_available_bytes, snapshot.memory_total_bytes)],
      [`Свободно на ${snapshot.disk_name}`, ratio(snapshot.disk_free_bytes, snapshot.disk_total_bytes)],
    ] : []);
  } else if (source === "wsl") {
    const memory = snapshot?.memory;
    displayMetrics(source, memory ? [
      ["Доступная RAM", ratio(memory.available_bytes, memory.total_bytes)],
      ["Занято swap", ratio(memory.swap_used_bytes, memory.swap_total_bytes)],
    ] : []);
  } else {
    displayProjects(snapshot?.projects);
  }
  displaySampleTime(source, snapshot);
}

const refreshButtons = [...document.querySelectorAll("[data-refresh]")];
for (const refresh of refreshButtons) {
  const source = refresh.dataset.refresh;
  refresh.addEventListener("click", async () => {
    const note = document.querySelector(`#${source}-age`);
    const previous = note.textContent.replace(/^Не удалось обновить\. /, "");
    refresh.disabled = true;
    delete note.dataset.state;
    note.textContent = "Запрашиваю новый замер…";
    try {
      const response = await fetch(`/api/metrics/${source}`, {
        method: "POST",
        headers: { "X-Dashboard-Refresh": "1" },
      });
      if (!response.ok) throw new Error("Metrics refresh failed");
      const sample = await response.json();
      if (!sample.snapshot) throw new Error("Snapshot missing");
      displaySnapshot(source, sample);
    } catch {
      note.dataset.state = "error";
      note.textContent = `Не удалось обновить. ${previous}`;
    } finally {
      refresh.disabled = false;
    }
  });
}

async function loadSavedMetrics() {
  let samples = {};
  try {
    const response = await fetch("/api/metrics");
    if (response.ok) samples = await response.json();
  } finally {
    for (const refresh of refreshButtons) {
      displaySnapshot(refresh.dataset.refresh, samples[refresh.dataset.refresh]);
      refresh.disabled = false;
    }
  }
}

loadSavedMetrics().catch(() => {});
