/**
 * Register Page Module
 */

import { handleRegister } from "../core/auth-handler.js";
import { sessionManager } from "../core/session-manager.js";
import { validateRegisterForm } from "../utils/validators.js";
import { MESSAGES } from "../utils/constants.js";

// Check if already logged in
if (sessionManager.isLoggedIn()) {
  window.location.href = "./feed.html";
}

// DOM Elements
const registerForm = document.getElementById("registerForm");
const usernameInput = document.getElementById("username");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const submitBtn = registerForm?.querySelector("button[type='submit']");
const errorDiv = document.getElementById("errorMessage");
const successDiv = document.getElementById("successMessage");
const loadingDiv = document.getElementById("loadingMessage");

// Form submit handler
registerForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = usernameInput.value.trim();
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  // Validate form
  const validation = validateRegisterForm(username, email, password);
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
    const result = await handleRegister(username, email, password);

    if (result.success) {
      // Show success message
      successDiv.textContent = MESSAGES.AUTH.REGISTER_SUCCESS;
      successDiv.style.display = "block";

      // Clear form
      registerForm.reset();

      // Redirect after delay
      setTimeout(() => {
        window.location.href = "./feed.html";
      }, 1500);
    } else {
      showError(result.error || MESSAGES.AUTH.REGISTER_FAILED);
    }
  } catch (err) {
    showError(err.message || MESSAGES.AUTH.REGISTER_FAILED);
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
usernameInput?.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});

emailInput?.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});

passwordInput?.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});
