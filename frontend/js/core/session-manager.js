/**
 * Session Manager
 * Global session and user information management
 */

import { STORAGE_KEYS } from "../utils/constants.js";

export class SessionManager {
  constructor() {
    this.currentUser = null;
    this.token = null;
    this.loadFromStorage();
  }

  /**
   * Load session information from localStorage
   */
  loadFromStorage() {
    try {
      const userData = localStorage.getItem(STORAGE_KEYS.CURRENT_USER);
      const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);

      if (userData) {
        this.currentUser = JSON.parse(userData);
      }
      if (token) {
        this.token = token;
      }
    } catch (error) {
      console.error("Session loading error:", error);
      this.clearSession();
    }
  }

  /**
   * Start user session (after login)
   * @param {Object} userData - User information
   * @param {string} token - Authentication token
   */
  setSession(userData, token = null) {
    this.currentUser = userData;
    this.token = token;

    // Save to localStorage
    localStorage.setItem(STORAGE_KEYS.CURRENT_USER, JSON.stringify(userData));
    if (token) {
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
    }

    // Dispatch event for other pages to listen
    window.dispatchEvent(
      new CustomEvent("userSessionChanged", {
        detail: { user: userData }
      })
    );
  }

  /**
   * End user session (logout)
   */
  clearSession() {
    this.currentUser = null;
    this.token = null;
    localStorage.removeItem(STORAGE_KEYS.CURRENT_USER);
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);

    window.dispatchEvent(new CustomEvent("userSessionCleared"));
  }

  /**
   * Get current user
   */
  getCurrentUser() {
    return this.currentUser;
  }

  /**
   * Get current user ID
   */
  getCurrentUserId() {
    return this.currentUser?.user_id || this.currentUser?.id || null;
  }

  /**
   * Check if user is logged in
   */
  isLoggedIn() {
    return this.currentUser !== null;
  }

  /**
   * Get authentication token
   */
  getToken() {
    return this.token;
  }

  /**
   * Update current user information
   */
  updateUserInfo(userData) {
    this.currentUser = { ...this.currentUser, ...userData };
    localStorage.setItem(STORAGE_KEYS.CURRENT_USER, JSON.stringify(this.currentUser));

    window.dispatchEvent(
      new CustomEvent("userSessionChanged", {
        detail: { user: this.currentUser }
      })
    );
  }
}

// Global session manager instance
export const sessionManager = new SessionManager();
