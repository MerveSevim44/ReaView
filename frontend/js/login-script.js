// frontend/js/login-script.js
import { handleLogin, handleRegister } from "./auth.js";
import { sessionManager } from "./session.js";
import { initializeNavbar } from "./navbar.js";

// Navbar'ı başlat
initializeNavbar();

// Zaten giriş yapılmışsa feed'e yönlendir
if (sessionManager.isLoggedIn()) {
  window.location.href = "./feed.html";
}

// Form öğeleri
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const switchToRegisterBtn = document.getElementById("switchToRegister");
const switchToLoginBtn = document.getElementById("switchToLogin");

// Login form input'ları
const loginEmailInput = document.getElementById("login-email");
const loginPasswordInput = document.getElementById("login-password");
const loginBtn = document.getElementById("loginBtn");
const loginError = document.getElementById("loginError");
const loginSuccess = document.getElementById("loginSuccess");
const loginLoading = document.getElementById("loginLoading");

// Register form input'ları
const registerUsernameInput = document.getElementById("register-username");
const registerEmailInput = document.getElementById("register-email");
const registerPasswordInput = document.getElementById("register-password");
const registerBtn = document.getElementById("registerBtn");
const registerError = document.getElementById("registerError");
const registerSuccess = document.getElementById("registerSuccess");
const registerLoading = document.getElementById("registerLoading");

/**
 * Form seçenekleri arasında geçiş yap
 */
switchToRegisterBtn.addEventListener("click", (e) => {
  e.preventDefault();
  loginForm.classList.add("hidden");
  registerForm.classList.remove("hidden");
  clearErrors();
});

switchToLoginBtn.addEventListener("click", (e) => {
  e.preventDefault();
  registerForm.classList.add("hidden");
  loginForm.classList.remove("hidden");
  clearErrors();
});

/**
 * Hataları temizle
 */
function clearErrors() {
  loginError.classList.remove("show");
  loginSuccess.classList.remove("show");
  registerError.classList.remove("show");
  registerSuccess.classList.remove("show");
}

/**
 * Giriş formu gönderimi
 */
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearErrors();

  const email = loginEmailInput.value.trim();
  const password = loginPasswordInput.value.trim();

  // Doğrulama
  if (!email || !password) {
    showLoginError("E-posta ve şifre gereklidir");
    return;
  }

  // Yükleme göstergesi
  loginBtn.disabled = true;
  loginLoading.classList.add("show");

  try {
    const result = await handleLogin(email, password);

    if (result.success) {
      showLoginSuccess("✅ Giriş başarılı! Yönlendiriliyorsunuz...");
      
      // Form temizle
      loginForm.reset();

      // 1.5 saniye sonra ana sayfaya yönlendir
      setTimeout(() => {
        window.location.href = "./feed.html";
      }, 1500);
    } else {
      showLoginError(result.error || "Giriş başarısız");
    }
  } catch (error) {
    showLoginError("Sunucu hatası: " + error.message);
  } finally {
    loginBtn.disabled = false;
    loginLoading.classList.remove("show");
  }
});

/**
 * Kayıt formu gönderimi
 */
registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearErrors();

  const username = registerUsernameInput.value.trim();
  const email = registerEmailInput.value.trim();
  const password = registerPasswordInput.value.trim();

  // Doğrulama
  if (!username || !email || !password) {
    showRegisterError("Tüm alanlar gereklidir");
    return;
  }

  if (password.length < 6) {
    showRegisterError("Şifre en az 6 karakter olmalıdır");
    return;
  }

  // Yükleme göstergesi
  registerBtn.disabled = true;
  registerLoading.classList.add("show");

  try {
    const result = await handleRegister(username, email, password);

    if (result.success) {
      showRegisterSuccess("✅ Kayıt başarılı! Yönlendiriliyorsunuz...");
      
      // Form temizle
      registerForm.reset();

      // 1.5 saniye sonra ana sayfaya yönlendir
      setTimeout(() => {
        window.location.href = "./feed.html";
      }, 1500);
    } else {
      showRegisterError(result.error || "Kayıt başarısız");
    }
  } catch (error) {
    showRegisterError("Sunucu hatası: " + error.message);
  } finally {
    registerBtn.disabled = false;
    registerLoading.classList.remove("show");
  }
});

/**
 * Giriş hataası göster
 */
function showLoginError(message) {
  loginError.textContent = "❌ " + message;
  loginError.classList.add("show");
}

/**
 * Giriş başarısı göster
 */
function showLoginSuccess(message) {
  loginSuccess.textContent = message;
  loginSuccess.classList.add("show");
}

/**
 * Kayıt hatası göster
 */
function showRegisterError(message) {
  registerError.textContent = "❌ " + message;
  registerError.classList.add("show");
}

/**
 * Kayıt başarısı göster
 */
function showRegisterSuccess(message) {
  registerSuccess.textContent = message;
  registerSuccess.classList.add("show");
}
