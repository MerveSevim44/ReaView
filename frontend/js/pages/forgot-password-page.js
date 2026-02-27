/**
 * Forgot Password Page
 */

import { sessionManager } from "../core/session-manager.js";
import { API_BASE_URL } from "../core/env.js";

// Giriş yapılıysa, feed'e yönlendir
if (sessionManager.isLoggedIn()) {
  window.location.href = "./feed.html";
}

const forgotForm = document.getElementById("forgotForm");
const emailInput = document.getElementById("email");
const errorDiv = document.getElementById("errorMessage");
const successDiv = document.getElementById("successMessage");
const submitBtn = forgotForm?.querySelector("button[type='submit']");

forgotForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = emailInput.value.trim();

  if (!email || !email.includes("@")) {
    showError("Geçerli bir e-posta adresi girin");
    return;
  }

  submitBtn.disabled = true;
  errorDiv.style.display = "none";
  successDiv.style.display = "none";

  try {
    const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();
    
    console.log("Status:", response.status);
    console.log("Response:", data);

    if (response.ok) {
      successDiv.textContent = "✅ Şifre sıfırlama linki e-posta adresinize gönderildi";
      successDiv.style.display = "block";
      emailInput.value = "";

      setTimeout(() => {
        window.location.href = "./login.html";
      }, 3000);
    } else {
      console.log("Error detail:", data.detail);
      showError(data.detail || "Bir hata oluştu");
    }
  } catch (err) {
    console.error("Fetch error:", err);
    showError(err.message || "Bir hata oluştu");
  } finally {
    submitBtn.disabled = false;
  }
});

function showError(message) {
  errorDiv.textContent = "❌ " + message;
  errorDiv.style.display = "block";
  successDiv.style.display = "none";
}

emailInput?.addEventListener("input", () => {
  errorDiv.style.display = "none";
  successDiv.style.display = "none";
});
