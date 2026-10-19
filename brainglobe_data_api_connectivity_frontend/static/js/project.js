const submitButtons = document.querySelectorAll(".submit-query-btn")

// For every query form, add an event listener to the submit button.
// This enables a spinner and loading text when the button is pushed.
document.querySelectorAll(".query-form").forEach((form) => {
    const spinner = form.querySelector(".query-spinner");
    const text = form.querySelector(".query-text");

    form.addEventListener("submit", () => {
      // Disable all submit buttons on the page when a form is submitted.
      // We don't want multiple submits while a query is loading.
      submitButtons.forEach((b) => (b.disabled = true));

      spinner.classList.remove("d-none");
      text.textContent = "Running query...";
    });
  });
