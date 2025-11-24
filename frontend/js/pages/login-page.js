/**
 * Login Page Module
 */

import { handleLogin } from "../core/auth-handler.js";
import { sessionManager } from "../core/session-manager.js";
import { validateLoginForm } from "../utils/validators.js";
import { MESSAGES } from "../utils/constants.js";

// Check if already logged in
if (sessionManager.isLoggedIn()) {
  window.location.href = "./feed.html";
}

// DOM Elements
const loginForm = document.getElementById("loginForm");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const submitBtn = loginForm?.querySelector("button[type='submit']");
const errorDiv = document.getElementById("errorMessage");
const successDiv = document.getElementById("successMessage");
const loadingDiv = document.getElementById("loadingMessage");

// Form submit handler
loginForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  // Validate form
  const validation = validateLoginForm(email, password);
  if (!validation.isValid) {
    showError(validation.errors[0]);
    return;
  }

  // Disable button & show loading
  submitBtn.disabled = true;
  loadingDiv.style.display = "flex";
  errorDiv.style.display = "none";
  successDiv.style.display = "none";

  try {
    const result = await handleLogin(email, password);

    if (result.success) {
      // Show success message
      successDiv.textContent = MESSAGES.AUTH.LOGIN_SUCCESS;
      successDiv.style.display = "block";

      // Redirect after delay
      setTimeout(() => {
        window.location.href = "./feed.html";
      }, 1500);
    } else {
      showError(result.error || MESSAGES.AUTH.LOGIN_FAILED);
    }
  } catch (err) {
    showError(err.message || MESSAGES.AUTH.LOGIN_FAILED);
  } finally {
    submitBtn.disabled = false;
    loadingDiv.style.display = "none";
  }
});

/**
 * Show error message
 */
function showError(message) {
  errorDiv.textContent = "❌ " + message;
  errorDiv.style.display = "block";
  successDiv.style.display = "none";
}

/**
 * Clear messages on input
 */
emailInput?.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});

passwordInput?.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});
