document.addEventListener('DOMContentLoaded', () => {
  const expenseForm = document.querySelector('#expense-form');
  const budgetForm = document.querySelector('#budget-form');
  const expenseList = document.querySelector('#expense-list');
  const totalDisplay = document.querySelector('#monthly-total');

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
    budgetForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const feedback = document.querySelector('#budget-form-feedback');
      if (feedback) {
        feedback.textContent = 'Budget form ready for the next implementation phase.';
      }
    });
  }

  if (expenseList) {
    expenseList.innerHTML = '<li class="empty-state">No expenses yet.</li>';
  }

  if (totalDisplay) {
    totalDisplay.textContent = '€0.00';
  }
});
