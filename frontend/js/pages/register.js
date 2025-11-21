// ============================================
// REGISTER PAGE LOGIC
// ============================================

import { handleRegister } from "../auth.js";
import { sessionManager } from "../session.js";

// Check if already logged in
if (sessionManager.isLoggedIn()) {
  window.location.href = "./feed.html";
}

// DOM Elements
const registerForm = document.getElementById("registerForm");
const usernameInput = document.getElementById("username");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const submitBtn = registerForm.querySelector("button[type='submit']");
const errorDiv = document.getElementById("errorMessage");
const successDiv = document.getElementById("successMessage");
const loadingDiv = document.getElementById("loadingMessage");

// Form submit handler
registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = usernameInput.value.trim();
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  // Validation
  if (!username || username.length < 3) {
    showError("Kullanıcı adı en az 3 karakter olmalı");
    return;
  }

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
    const result = await handleRegister(username, email, password);

    if (result.success) {
      // Success
      successDiv.textContent = "✅ Kayıt başarılı! Yönlendiriliyorsunuz...";
      successDiv.style.display = "block";

      // Clear form
      registerForm.reset();

      // Redirect to feed
      setTimeout(() => {
        window.location.href = "./feed.html";
      }, 1500);
    } else {
      // Error from auth.js
      showError(result.error || "Kayıt başarısız. Lütfen bilgilerinizi kontrol edin.");
    }
  } catch (err) {
    showError(err.message || "Kayıt sırasında hata oluştu");
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
usernameInput.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});

emailInput.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});

passwordInput.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});
