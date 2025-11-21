// frontend/js/session.js
// Global oturum yönetimi ve kullanıcı bilgileri

export class SessionManager {
  constructor() {
    this.currentUser = null;
    this.token = null;
    this.loadFromStorage();
  }

  /**
   * LocalStorage'dan oturum bilgilerini yükle
   */
  loadFromStorage() {
    try {
      const userData = localStorage.getItem("currentUser");
      const token = localStorage.getItem("authToken");
      
      if (userData) {
        this.currentUser = JSON.parse(userData);
      }
      if (token) {
        this.token = token;
      }
    } catch (error) {
      console.error("Oturum yükleme hatası:", error);
      this.clearSession();
    }
  }

  /**
   * Kullanıcı oturumu başlat (Giriş sonrası)
   * @param {Object} userData - Kullanıcı bilgileri
   * @param {string} token - Kimlik doğrulama token'ı
   */
  setSession(userData, token = null) {
    this.currentUser = userData;
    this.token = token;
    
    // LocalStorage'a kaydet
    localStorage.setItem("currentUser", JSON.stringify(userData));
    if (token) {
      localStorage.setItem("authToken", token);
    }
    
    // Event gönder (diğer sayfalar dinleyebilsin)
    window.dispatchEvent(new CustomEvent("userSessionChanged", {
      detail: { user: userData }
    }));
  }

  /**
   * Oturumu sonlandır (Çıkış)
   */
  clearSession() {
    this.currentUser = null;
    this.token = null;
    localStorage.removeItem("currentUser");
    localStorage.removeItem("authToken");
    
    window.dispatchEvent(new CustomEvent("userSessionCleared"));
  }

  /**
   * Aktif kullanıcıyı getir
   */
  getCurrentUser() {
    return this.currentUser;
  }

  /**
   * Aktif kullanıcı ID'sini getir
   */
  getCurrentUserId() {
    return this.currentUser?.user_id || this.currentUser?.id || null;
  }

  /**
   * Kullanıcı giriş yaptı mı kontrol et
   */
  isLoggedIn() {
    return this.currentUser !== null;
  }

  /**
   * Kimlik doğrulama token'ını getir
   */
  getToken() {
    return this.token;
  }

  /**
   * Aktif kullanıcının bilgilerini güncelle
   */
  updateUserInfo(userData) {
    this.currentUser = { ...this.currentUser, ...userData };
    localStorage.setItem("currentUser", JSON.stringify(this.currentUser));
    
    window.dispatchEvent(new CustomEvent("userSessionChanged", {
      detail: { user: this.currentUser }
    }));
  }
}

// Global oturum yöneticisi örneği
export const sessionManager = new SessionManager();
