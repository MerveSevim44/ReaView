// frontend/js/auth.js
import { loginUser, registerUser, API_URL } from "./api.js";
import { sessionManager } from "./session.js";

/**
 * Giriş formunu işle
 */
export async function handleLogin(email, password) {
  try {
    const response = await loginUser(email, password);
    
    // Oturumu başlat
    sessionManager.setSession(response.user, response.token);
    
    // Başarı mesajı
    console.log("✅ Giriş başarılı!", response.user);
    return { success: true, data: response };
  } catch (error) {
    console.error("❌ Giriş hatası:", error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Kayıt formunu işle
 */
export async function handleRegister(username, email, password) {
  try {
    const response = await registerUser(username, email, password);
    
    // Kayıttan sonra otomatik giriş yap
    sessionManager.setSession(response.user, response.token);
    
    console.log("✅ Kayıt başarılı!", response.user);
    return { success: true, data: response };
  } catch (error) {
    console.error("❌ Kayıt hatası:", error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Çıkış işlemi
 */
export function handleLogout() {
  sessionManager.clearSession();
  console.log("✅ Çıkış işlemi tamamlandı");
  return true;
}

/**
 * Aktif kullanıcıyı kontrol et
 */
export function getCurrentUser() {
  return sessionManager.getCurrentUser();
}

/**
 * Kullanıcı giriş yaptı mı kontrol et
 */
export function isAuthenticated() {
  return sessionManager.isLoggedIn();
}
