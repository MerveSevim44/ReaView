/**
 * Reset Password Page
 */

import { sessionManager } from "../core/session-manager.js";

// Giriş yapılıysa, feed'e yönlendir
if (sessionManager.isLoggedIn()) {
  window.location.href = "./feed.html";
}

// URL parametrelerinden token ve email'i al
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get("token");
const email = urlParams.get("email");

// Token ve email varsa devam et, yoksa hata göster
if (!token || !email) {
  document.body.innerHTML = `
    <div class="auth-container" style="text-align: center; margin-top: 50px;">
      <h2>❌ Geçersiz Bağlantı</h2>
      <p>Şifre sıfırlama bağlantısı geçerli değil.</p>
      <a href="./forgot-password.html" class="btn btn-primary" style="display: inline-block; margin-top: 20px;">← Tekrar Dene</a>
    </div>
  `;
}

const resetForm = document.getElementById("resetForm");
const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirmPassword");
const errorDiv = document.getElementById("errorMessage");
const successDiv = document.getElementById("successMessage");
const submitBtn = resetForm?.querySelector("button[type='submit']");

resetForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const password = passwordInput.value;
  const confirmPassword = confirmPasswordInput.value;

  // Şifre validasyonu
  if (!password || password.length < 6) {
    showError("Şifre en az 6 karakter olmalıdır");
    return;
  }

  if (password !== confirmPassword) {
    showError("Şifreler eşleşmiyor");
    return;
  }

  submitBtn.disabled = true;
  errorDiv.style.display = "none";
  successDiv.style.display = "none";

  try {
    const response = await fetch("http://127.0.0.1:8000/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        token,
        new_password: password,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      successDiv.textContent = "✅ Şifre başarıyla güncellendi. Giriş sayfasına yönlendiriliyorsunuz...";
      successDiv.style.display = "block";

      setTimeout(() => {
        window.location.href = "./login.html";
      }, 2000);
    } else {
      showError(data.detail || "Şifre güncelleme başarısız");
    }
  } catch (err) {
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

passwordInput?.addEventListener("input", () => {
  errorDiv.style.display = "none";
});

confirmPasswordInput?.addEventListener("input", () => {
  errorDiv.style.display = "none";
});
