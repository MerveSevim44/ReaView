/**
 * Auth Handler
 * Authentication logic
 */

import { loginUser, registerUser } from "./api-client.js";
import { sessionManager } from "./session-manager.js";

/**
 * Handle login form
 */
export async function handleLogin(email, password) {
  try {
    const response = await loginUser(email, password);

    // Start session
    sessionManager.setSession(response.user, response.token);

    console.log("✅ Login successful!", response.user);
    return { success: true, data: response };
  } catch (error) {
    console.error("❌ Login error:", error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Handle registration form
 */
export async function handleRegister(username, email, password) {
  try {
    const response = await registerUser(username, email, password);

    // Auto login after registration
    sessionManager.setSession(response.user, response.token);

    console.log("✅ Registration successful!", response.user);
    return { success: true, data: response };
  } catch (error) {
    console.error("❌ Registration error:", error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Handle logout
 */
export function handleLogout() {
  sessionManager.clearSession();
  console.log("✅ Logout successful");
  return true;
}

/**
 * Get current user
 */
export function getCurrentUser() {
  return sessionManager.getCurrentUser();
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
  return sessionManager.isLoggedIn();
}

/**
 * Require authentication (redirect if not logged in)
 */
export function requireAuth() {
  if (!sessionManager.isLoggedIn()) {
    window.location.href = "./login.html";
    return false;
  }
  return true;
}
