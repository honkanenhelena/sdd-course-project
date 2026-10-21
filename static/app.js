const monthPicker = document.querySelector("#month-picker");
const colors = ["#176a50", "#e9795d", "#5688d8", "#e9b84b", "#8d68b1", "#4ca89c", "#dc9b4b"];
const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const state = { expenses: [], categories: [], summary: null, toastTimer: null, searchTimer: null, editingBudget: null };

function localMonth(date = new Date()) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function escapeHTML(value = "") {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const message = Array.isArray(body.detail) ? body.detail.map((item) => item.msg).join(". ") : body.detail;
    throw new Error(message || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

function showToast(message, isError = false) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("visible");
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => toast.classList.remove("visible"), 2800);
}

function selectedMonthLabel(month) {
  return new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric", timeZone: "UTC" })
    .format(new Date(`${month}-01T12:00:00Z`));
}

function expenseFilters() {
  const startDate = document.querySelector("#date-from-filter").value;
  const endDate = document.querySelector("#date-to-filter").value;
  const params = new URLSearchParams();
  if (!startDate && !endDate) params.set("month", monthPicker.value);
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);
  const category = document.querySelector("#category-filter").value;
  const necessity = document.querySelector("#necessity-filter").value;
  const search = document.querySelector("#search-filter").value.trim();
  if (category) params.set("category", category);
  if (necessity) params.set("necessity", necessity);
  if (search) params.set("search", search);
  return params;
}

async function refresh() {
  const month = monthPicker.value;
  try {
    const [summary, expenses, categories] = await Promise.all([
      request(`/api/summary?month=${encodeURIComponent(month)}`),
      request(`/api/expenses?${expenseFilters()}`),
      request("/api/categories"),
    ]);
    state.summary = summary;
    state.expenses = expenses;
    state.categories = categories;
    renderSummary();
    renderBudgets();
    renderExpenses();
    renderCategoryOptions();
    drawChart();
  } catch (error) {
    showToast(error.message, true);
  }
}

function renderSummary() {
  const summary = state.summary;
  const monthName = selectedMonthLabel(summary.month);
  document.querySelector("#selected-month-label").textContent = `${monthName} OVERVIEW`;
  document.querySelector("#chart-period").textContent = monthName;
  document.querySelector("#total-spent").textContent = money.format(summary.total);
  document.querySelector("#expense-count").textContent = `${summary.expense_count} ${summary.expense_count === 1 ? "transaction" : "transactions"}`;
  document.querySelector("#budget-left").textContent = money.format(summary.remaining);
  document.querySelector("#budget-left").classList.toggle("over-budget", summary.remaining < 0);
  document.querySelector("#budget-caption").textContent = summary.budget ? `${money.format(summary.budget)} monthly limit` : "Set category budgets below";
  document.querySelector("#category-count").textContent = String(summary.categories.filter((item) => item.spent > 0).length);
  document.querySelector("#month-total-budget").textContent = `${money.format(summary.budget)} budgeted this month`;
  document.querySelector("#budget-total-chip").textContent = `${money.format(summary.budget)} budgeted`;
  const percent = summary.budget > 0 ? Math.min(100, (summary.total / summary.budget) * 100) : 0;
  document.querySelector("#overall-budget-meter").style.width = `${percent}%`;
  document.querySelector("#overall-budget-meter").style.background = summary.remaining < 0 ? "var(--coral)" : "var(--green)";
  document.querySelector("#category-stamps").innerHTML = summary.categories
    .filter((item) => item.spent > 0).slice(0, 8).map(() => "<i></i>").join("");
}

function renderBudgets() {
  const list = document.querySelector("#budget-list");
  const categories = state.summary.categories.filter((item) => item.has_budget);
  if (!categories.length) {
    list.innerHTML = '<p class="budget-empty">No category budgets for this month.</p>';
    return;
  }
  list.innerHTML = categories.map((item) => {
    const progress = item.budget > 0 ? Math.min(100, (item.spent / item.budget) * 100) : item.spent > 0 ? 100 : 0;
    const over = item.spent > item.budget;
    return `<div class="budget-row">
      <div class="budget-name"><span class="budget-category" title="${escapeHTML(item.category)}">${escapeHTML(item.category)}</span><span class="budget-actions"><button type="button" data-budget-edit="${escapeHTML(item.category)}">Edit</button><button type="button" data-budget-remove="${escapeHTML(item.category)}">Remove</button></span></div>
      <div class="budget-progress" role="progressbar" aria-label="${escapeHTML(item.category)} budget used" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${Math.round(progress)}"><span class="${over ? "over" : ""}" style="width:${progress}%"></span></div>
      <span class="budget-amounts"><strong>${money.format(item.spent)}</strong> / ${money.format(item.budget)}</span>
    </div>`;
  }).join("");
}

function renderCategoryOptions() {
  const current = document.querySelector("#category-filter").value;
  const categories = state.categories;
  document.querySelector("#category-filter").innerHTML = '<option value="">All categories</option>' + categories
    .map((category) => `<option value="${escapeHTML(category)}">${escapeHTML(category)}</option>`).join("");
  if (categories.includes(current)) document.querySelector("#category-filter").value = current;
  document.querySelector("#category-options").innerHTML = categories
    .map((category) => `<option value="${escapeHTML(category)}"></option>`).join("");
}

function dateLabel(value) {
  const [year, month, day] = value.split("-").map(Number);
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(new Date(year, month - 1, day));
}

function renderExpenses() {
  const rows = document.querySelector("#expense-rows");
  const empty = document.querySelector("#table-empty");
  document.querySelector("#visible-count").textContent = String(state.expenses.length);
  document.querySelector("#clear-date-filter").hidden = !(
    document.querySelector("#date-from-filter").value || document.querySelector("#date-to-filter").value
  );
  empty.hidden = state.expenses.length > 0;
  rows.innerHTML = state.expenses.map((expense) => `<tr>
    <td class="date-cell">${dateLabel(expense.date)}</td>
    <td><span class="expense-name">${escapeHTML(expense.category)}</span><span class="expense-note">${escapeHTML(expense.note || "No note")}</span></td>
    <td><span class="category-tag">${escapeHTML(expense.category)}</span></td>
    <td><span class="necessity-pill ${expense.necessity ? "essential" : ""}">${expense.necessity ? "Essential" : "Non-essential"}</span></td>
    <td class="amount-cell">${money.format(expense.amount)}</td>
    <td><div class="row-actions"><button class="row-action" type="button" data-edit="${expense.id}">Edit</button><button class="row-action delete" type="button" data-delete="${expense.id}">Delete</button></div></td>
  </tr>`).join("");
}

function drawChart() {
  if (!state.summary) return;
  const canvas = document.querySelector("#spending-chart");
  const context = canvas.getContext("2d");
  const bounds = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.round(bounds.width * ratio));
  canvas.height = Math.max(1, Math.round(bounds.height * ratio));
  context.scale(ratio, ratio);
  const width = bounds.width;
  const height = bounds.height;
  const data = state.summary.categories.filter((item) => item.spent > 0).sort((a, b) => b.spent - a.spent);
  const total = data.reduce((sum, item) => sum + item.spent, 0);
  const empty = document.querySelector("#chart-empty");
  empty.hidden = data.length > 0;
  document.querySelector("#chart-legend").innerHTML = data.map((item, index) => {
    const share = total > 0 ? (item.spent / total) * 100 : 0;
    return `<span class="legend-item"><i class="legend-swatch" style="background:${colors[index % colors.length]}"></i><span class="legend-label" title="${escapeHTML(item.category)}">${escapeHTML(item.category)}</span><span class="legend-detail">${money.format(item.spent)} · ${share.toFixed(1)}%</span></span>`;
  }).join("");
  canvas.setAttribute("aria-label", data.length
    ? `${selectedMonthLabel(state.summary.month)} spending: ${data.map((item) => `${item.category}, ${money.format(item.spent)}, ${((item.spent / total) * 100).toFixed(1)} percent`).join("; ")}. Total ${money.format(total)}.`
    : "No spending recorded for this month.");
  if (!data.length) return;

  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 2 - 5;
  let angle = -Math.PI / 2;
  data.forEach((item, index) => {
    const nextAngle = angle + (item.spent / total) * Math.PI * 2;
    context.beginPath();
    context.arc(centerX, centerY, radius, angle, nextAngle);
    context.arc(centerX, centerY, radius * 0.58, nextAngle, angle, true);
    context.closePath();
    context.fillStyle = colors[index % colors.length];
    context.fill();
    angle = nextAngle;
  });

  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillStyle = "#26352d";
  const totalLabel = money.format(total);
  context.font = `700 ${totalLabel.length > 9 ? 12 : 15}px "Manrope", sans-serif`;
  context.fillText(totalLabel, centerX, centerY - 5, radius * 1.02);
  context.fillStyle = "#87928a";
  context.font = '9px "DM Mono", monospace';
  context.fillText("TOTAL", centerX, centerY + 12);
}

function openExpenseDialog(expense = null) {
  const form = document.querySelector("#expense-form");
  form.reset();
  document.querySelector("#form-error").textContent = "";
  document.querySelector("#expense-id").value = expense?.id || "";
  document.querySelector("#dialog-title").textContent = expense ? "Edit expense" : "Add expense";
  document.querySelector("#dialog-eyebrow").textContent = expense ? "UPDATE ENTRY" : "NEW ENTRY";
  document.querySelector("#save-expense").textContent = expense ? "Save changes" : "Save expense";
  document.querySelector("#expense-amount").value = expense?.amount ?? "";
  document.querySelector("#expense-date").value = expense?.date || `${monthPicker.value}-${String(new Date().getDate()).padStart(2, "0")}`;
  document.querySelector("#expense-category").value = expense?.category || "";
  document.querySelector("#expense-note").value = expense?.note || "";
  document.querySelector("#expense-necessity").checked = expense?.necessity ?? false;
  document.querySelector("#expense-dialog").showModal();
}

document.querySelector("#today-label").textContent = new Intl.DateTimeFormat("en-US", {
  weekday: "long", month: "long", day: "numeric",
}).format(new Date());
monthPicker.value = localMonth();
monthPicker.addEventListener("change", () => {
  document.querySelector("#category-filter").value = "";
  document.querySelector("#date-from-filter").value = "";
  document.querySelector("#date-to-filter").value = "";
  document.querySelector("#clear-date-filter").hidden = true;
  refresh();
});
document.querySelector("#add-expense-button").addEventListener("click", () => openExpenseDialog());
document.querySelector("#empty-add-button").addEventListener("click", () => openExpenseDialog());
document.querySelector("#close-dialog").addEventListener("click", () => document.querySelector("#expense-dialog").close());
document.querySelector("#cancel-dialog").addEventListener("click", () => document.querySelector("#expense-dialog").close());
document.querySelector("#expense-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = document.querySelector("#expense-id").value;
  const payload = {
    amount: Number(document.querySelector("#expense-amount").value),
    date: document.querySelector("#expense-date").value,
    category: document.querySelector("#expense-category").value.trim(),
    necessity: document.querySelector("#expense-necessity").checked,
    note: document.querySelector("#expense-note").value.trim() || null,
  };
  try {
    await request(id ? `/api/expenses/${id}` : "/api/expenses", {
      method: id ? "PUT" : "POST", body: JSON.stringify(payload),
    });
    document.querySelector("#expense-dialog").close();
    if (payload.date.slice(0, 7) !== monthPicker.value) monthPicker.value = payload.date.slice(0, 7);
    await refresh();
    showToast(id ? "Expense updated" : "Expense added");
  } catch (error) {
    document.querySelector("#form-error").textContent = error.message;
  }
});

document.querySelector("#expense-rows").addEventListener("click", async (event) => {
  const editButton = event.target.closest("[data-edit]");
  const deleteButton = event.target.closest("[data-delete]");
  if (editButton) {
    openExpenseDialog(state.expenses.find((expense) => expense.id === Number(editButton.dataset.edit)));
  }
  if (deleteButton) {
    const expense = state.expenses.find((item) => item.id === Number(deleteButton.dataset.delete));
    if (!expense || !window.confirm(`Delete the ${money.format(expense.amount)} ${expense.category} expense?`)) return;
    try {
      await request(`/api/expenses/${expense.id}`, { method: "DELETE" });
      await refresh();
      showToast("Expense deleted");
    } catch (error) {
      showToast(error.message, true);
    }
  }
});

document.querySelector("#budget-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const categoryInput = document.querySelector("#budget-category");
  try {
    await request("/api/budgets", {
      method: "PUT",
      body: JSON.stringify({ month: monthPicker.value, category: categoryInput.value.trim(), amount: Number(document.querySelector("#budget-amount").value) }),
    });
    categoryInput.value = "";
    document.querySelector("#budget-amount").value = "";
    state.editingBudget = null;
    categoryInput.readOnly = false;
    document.querySelector("#budget-form button[type=submit]").textContent = "Save";
    document.querySelector("#cancel-budget-edit").hidden = true;
    await refresh();
    showToast("Monthly budget saved");
  } catch (error) {
    showToast(error.message, true);
  }
});

document.querySelector("#budget-list").addEventListener("click", async (event) => {
  const editButton = event.target.closest("[data-budget-edit]");
  const removeButton = event.target.closest("[data-budget-remove]");
  const category = editButton?.dataset.budgetEdit || removeButton?.dataset.budgetRemove;
  if (!category) return;
  if (editButton) {
    const budget = state.summary.categories.find((item) => item.category === category && item.has_budget);
    if (!budget) return;
    state.editingBudget = category;
    document.querySelector("#budget-category").value = category;
    document.querySelector("#budget-category").readOnly = true;
    document.querySelector("#budget-amount").value = budget.budget;
    document.querySelector("#budget-form button[type=submit]").textContent = "Update";
    document.querySelector("#cancel-budget-edit").hidden = false;
    document.querySelector("#budget-amount").focus();
    return;
  }
  if (!window.confirm(`Remove the ${category} budget for ${selectedMonthLabel(monthPicker.value)}?`)) return;
  try {
    const params = new URLSearchParams({ month: monthPicker.value, category });
    await request(`/api/budgets?${params}`, { method: "DELETE" });
    if (state.editingBudget === category) resetBudgetForm();
    await refresh();
    showToast("Monthly budget removed");
  } catch (error) {
    showToast(error.message, true);
  }
});

function resetBudgetForm() {
  state.editingBudget = null;
  document.querySelector("#budget-form").reset();
  document.querySelector("#budget-category").readOnly = false;
  document.querySelector("#budget-form button[type=submit]").textContent = "Save";
  document.querySelector("#cancel-budget-edit").hidden = true;
}

document.querySelector("#cancel-budget-edit").addEventListener("click", resetBudgetForm);

document.querySelector("#category-filter").addEventListener("change", refresh);
document.querySelector("#necessity-filter").addEventListener("change", refresh);
document.querySelector("#date-from-filter").addEventListener("change", refresh);
document.querySelector("#date-to-filter").addEventListener("change", refresh);
document.querySelector("#clear-date-filter").addEventListener("click", () => {
  document.querySelector("#date-from-filter").value = "";
  document.querySelector("#date-to-filter").value = "";
  document.querySelector("#clear-date-filter").hidden = true;
  refresh();
});
document.querySelector("#search-filter").addEventListener("input", () => {
  clearTimeout(state.searchTimer);
  state.searchTimer = setTimeout(refresh, 180);
});
window.addEventListener("resize", drawChart);
refresh();