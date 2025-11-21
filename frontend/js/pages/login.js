// ============================================
// LOGIN PAGE LOGIC
// ============================================

import { handleLogin } from "../auth.js";
import { sessionManager } from "../session.js";

// Check if already logged in
if (sessionManager.isLoggedIn()) {
  window.location.href = "./feed.html";
}

// DOM Elements
const loginForm = document.getElementById("loginForm");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const submitBtn = loginForm.querySelector("button[type='submit']");
const errorDiv = document.getElementById("errorMessage");
const successDiv = document.getElementById("successMessage");
const loadingDiv = document.getElementById("loadingMessage");

// Form submit handler
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  // Validation
  if (!email || !email.includes("@")) {
    showError("Geçerli bir e-posta girin");
    return;
  }

  if (!password || password.length < 6) {
    showError("Şifre en az 6 karakter olmalı");
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
      // Success
      successDiv.textContent = "✅ Giriş başarılı! Yönlendiriliyorsunuz...";
      successDiv.style.display = "block";

      // Redirect to feed
      setTimeout(() => {
        window.location.href = "./feed.html";
      }, 1500);
    } else {
      // Error from auth.js
      showError(result.error || "Giriş başarısız. Lütfen bilgilerinizi kontrol edin.");
    }
  } catch (err) {
    showError(err.message || "Giriş sırasında hata oluştu");
  } finally {
    submitBtn.disabled = false;
    loadingDiv.style.display = "none";
  }
});

// Helper: Show error message
function showError(message) {
  errorDiv.textContent = "❌ " + message;
  errorDiv.style.display = "block";
  successDiv.style.display = "none";
}

// Helper: Clear messages on input
emailInput.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});

passwordInput.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});
