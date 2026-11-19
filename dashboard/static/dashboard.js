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
