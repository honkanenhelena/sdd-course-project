document.addEventListener('DOMContentLoaded', () => {
  const expenseForm = document.querySelector('#expense-form');
  const budgetForm = document.querySelector('#budget-form');
  const expenseList = document.querySelector('#expense-list');
  const totalDisplay = document.querySelector('#monthly-total');
  const budgetMonth = document.querySelector('[name="budget-month"]');
  const budgetCategory = document.querySelector('[name="budget-category"]');
  const budgetLimit = document.querySelector('[name="budget-limit"]');
  const budgetList = document.querySelector('#budget-list');
  const summaryMonth = document.querySelector('[name="summary-month"]');
  const fromDate = document.querySelector('[name="from-date"]');
  const toDate = document.querySelector('[name="to-date"]');
  const categoryFilter = document.querySelector('[name="filter-category"]');
  const necessityFilter = document.querySelector('[name="filter-necessity"]');
  const categoryBreakdown = document.querySelector('#category-breakdown');
  const categoryChart = document.querySelector('#category-chart');
  const summaryFeedback = document.querySelector('#summary-feedback');

  const currentDate = new Date();
  const currentMonth = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`;
  if (summaryMonth && !summaryMonth.value) {
    summaryMonth.value = currentMonth;
  }
  if (budgetMonth && !budgetMonth.value) {
    budgetMonth.value = currentMonth;
  }

  function euroToCents(amount) {
    const [units, fraction = '00'] = amount.split('.');
    return BigInt(units) * 100n + BigInt(fraction.padEnd(2, '0'));
  }

  async function loadCategories() {
    if (!categoryFilter) return;
    try {
      const response = await fetch('/api/categories');
      if (!response.ok) throw new Error('Unable to load categories.');
      const categories = await response.json();
      for (const category of categories) {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.label;
        categoryFilter.append(option);
      }
    } catch (error) {
      if (summaryFeedback) summaryFeedback.textContent = error.message;
    }
  }

  async function loadExpenses() {
    if (!expenseList) return;
    const params = new URLSearchParams();
    if (fromDate?.value) params.set('from', fromDate.value);
    if (toDate?.value) params.set('to', toDate.value);
    if (categoryFilter?.value) params.set('category', categoryFilter.value);
    if (necessityFilter?.value) params.set('necessity', necessityFilter.value);

    try {
      const response = await fetch(`/api/expenses?${params.toString()}`);
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'Unable to load expenses.');
      expenseList.replaceChildren();
      if (payload.length === 0) {
        const emptyState = document.createElement('li');
        emptyState.className = 'empty-state';
        emptyState.textContent = 'No expenses match these filters.';
        expenseList.append(emptyState);
        return;
      }
      for (const expense of payload) {
        const item = document.createElement('li');
        item.textContent = `${expense.date} | ${expense.category_label} | €${expense.amount} | ${expense.is_necessity ? 'Essential' : 'Optional'}${expense.note ? ` | ${expense.note}` : ''}`;
        expenseList.append(item);
      }
    } catch (error) {
      expenseList.replaceChildren();
      const message = document.createElement('li');
      message.className = 'empty-state';
      message.textContent = error.message;
      expenseList.append(message);
    } finally {
      void loadBudgets();
    }
  }

  async function loadBudgets() {
    if (!budgetMonth?.value || !budgetList) return;
    try {
      const params = new URLSearchParams({ month: budgetMonth.value });
      const response = await fetch(`/api/budgets?${params.toString()}`);
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'Unable to load budgets.');
      budgetList.replaceChildren();
      if (payload.length === 0) {
        const emptyState = document.createElement('li');
        emptyState.className = 'empty-state';
        emptyState.textContent = 'No budgets for this month yet.';
        budgetList.append(emptyState);
        return;
      }

      for (const budget of payload) {
        const item = document.createElement('li');
        const heading = document.createElement('div');
        const label = document.createElement('h3');
        const status = document.createElement('p');
        const amounts = document.createElement('p');
        const progress = document.createElement('progress');
        const spentCents = euroToCents(budget.spent);
        const limitCents = euroToCents(budget.limit);
        item.className = 'budget-item';
        if (spentCents > limitCents) {
          item.classList.add('over-budget');
          status.textContent = `Over budget by €${budget.overage}`;
        } else if (spentCents === limitCents) {
          item.classList.add('at-budget');
          status.textContent = 'Budget fully used';
        } else {
          item.classList.add('under-budget');
          status.textContent = `€${budget.remaining} remaining`;
        }
        heading.className = 'budget-heading';
        label.textContent = budget.category_label;
        progress.setAttribute('aria-label', `${budget.category_label} budget progress`);
        progress.max = 100;
        progress.value = Math.min(budget.progress_percent, 100);
        amounts.textContent = `Limit €${budget.limit} · Spent €${budget.spent} · Remaining €${budget.remaining} · Overage €${budget.overage} · ${budget.progress_percent.toFixed(1)}% used`;
        heading.append(label, status);
        item.append(heading, amounts, progress);
        budgetList.append(item);
      }
    } catch (error) {
      budgetList.replaceChildren();
      const message = document.createElement('li');
      message.className = 'empty-state';
      message.textContent = error.message;
      budgetList.append(message);
    }
  }

  async function loadSummary() {
    if (!summaryMonth?.value || !totalDisplay) return;
    if (summaryFeedback) summaryFeedback.textContent = '';
    const params = new URLSearchParams({ month: summaryMonth.value });
    try {
      const response = await fetch(`/api/summary?${params.toString()}`);
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'Unable to load monthly summary.');
      totalDisplay.textContent = `€${payload.total}`;
      categoryBreakdown?.replaceChildren();
      categoryChart?.replaceChildren();
      const largestCategory = Math.max(...payload.categories.map((category) => Number(category.total)));
      for (const category of payload.categories) {
        if (categoryBreakdown) {
          const row = document.createElement('li');
          const label = document.createElement('span');
          const amount = document.createElement('strong');
          label.textContent = category.label;
          amount.textContent = `€${category.total}`;
          row.append(label, amount);
          categoryBreakdown.append(row);
        }
        if (categoryChart) {
          const row = document.createElement('li');
          const heading = document.createElement('div');
          const label = document.createElement('span');
          const amount = document.createElement('strong');
          const track = document.createElement('span');
          const bar = document.createElement('span');
          row.className = 'chart-row';
          heading.className = 'chart-heading';
          track.className = 'chart-track';
          bar.className = 'chart-bar';
          label.textContent = category.label;
          amount.textContent = `€${category.total}`;
          bar.style.width = largestCategory > 0
            ? `${(Number(category.total) / largestCategory) * 100}%`
            : '0%';
          heading.append(label, amount);
          track.append(bar);
          row.append(heading, track);
          categoryChart.append(row);
        }
      }
    } catch (error) {
      totalDisplay.textContent = '€0.00';
      categoryBreakdown?.replaceChildren();
      categoryChart?.replaceChildren();
      if (summaryFeedback) summaryFeedback.textContent = error.message;
    }
  }

  if (expenseForm) {
    expenseForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const feedback = document.querySelector('#expense-form-feedback');
      if (feedback) {
        feedback.textContent = 'Expense form ready for the next implementation phase.';
      }
    });
  }

  if (budgetForm) {
    budgetForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const feedback = document.querySelector('#budget-form-feedback');
      if (!budgetForm.checkValidity()) {
        budgetForm.reportValidity();
        return;
      }
      if (feedback) feedback.textContent = '';
      try {
        const response = await fetch(
          `/api/budgets/${encodeURIComponent(budgetMonth.value)}/${encodeURIComponent(budgetCategory.value)}`,
          {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ limit: budgetLimit.value }),
          },
        );
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.detail || 'Unable to save budget.');
        if (feedback) feedback.textContent = 'Budget saved.';
        await loadBudgets();
      } catch (error) {
        if (feedback) feedback.textContent = error.message;
      }
    });
  }

  if (expenseList) {
    expenseList.replaceChildren();
  }

  void loadCategories();
  void loadExpenses();
  void loadSummary();
  void loadBudgets();
  [fromDate, toDate, categoryFilter, necessityFilter].forEach((filter) => {
    filter?.addEventListener('change', () => void loadExpenses());
  });
  summaryMonth?.addEventListener('change', () => void loadSummary());
  budgetMonth?.addEventListener('change', () => void loadBudgets());
});
