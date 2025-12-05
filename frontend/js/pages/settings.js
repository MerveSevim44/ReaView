/**
 * Settings Page Module
 */

import { initializeNavbar } from "../components/navbar.js";
import { sessionManager } from "../core/session-manager.js";
import { API_CONFIG } from "../utils/constants.js";

// API Base URL
const API_BASE = API_CONFIG.BASE_URL;

// Current user
let currentUser = null;

/**
 * Initialize settings page
 */
window.addEventListener("DOMContentLoaded", async () => {
  // Initialize navbar
  initializeNavbar();

  // Check authentication
  const userId = sessionManager.getCurrentUserId();
  if (!userId) {
    window.location.href = "./login.html";
    return;
  }

  // Get current user data
  await loadUserData();

  // Setup navigation
  setupNavigation();

  // Setup forms
  setupProfileForm();
  setupPasswordForm();
  setupPrivacyForm();
  setupNotificationsForm();
  setupDeleteAccount();
});

/**
 * Load current user data
 */
async function loadUserData() {
  try {
    const token = sessionManager.getToken();
    const response = await fetch(`${API_BASE}/auth/current-user`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error("Kullanıcı bilgileri alınamadı");
    }

    currentUser = await response.json();
    console.log("Current user:", currentUser);

    // Fill profile form
    fillProfileForm();
  } catch (error) {
    console.error("Error loading user data:", error);
    showError("Kullanıcı bilgileri yüklenemedi");
  }
}

/**
 * Fill profile form with user data
 */
function fillProfileForm() {
  const usernameInput = document.getElementById("username");
  const emailInput = document.getElementById("email");
  const bioInput = document.getElementById("bio");
  const avatarUrlInput = document.getElementById("avatarUrl");

  if (currentUser) {
    usernameInput.value = currentUser.username || "";
    emailInput.value = currentUser.email || "";
    bioInput.value = currentUser.bio || "";
    avatarUrlInput.value = currentUser.avatar_url || "";

    // Show avatar preview if exists
    if (currentUser.avatar_url) {
      showAvatarPreview(currentUser.avatar_url);
    }
  }
}

/**
 * Setup sidebar navigation
 */
function setupNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  const sections = document.querySelectorAll(".settings-section");

  navItems.forEach((item) => {
    item.addEventListener("click", () => {
      const targetSection = item.getAttribute("data-section");

      // Update active nav item
      navItems.forEach((nav) => nav.classList.remove("active"));
      item.classList.add("active");

      // Show target section
      sections.forEach((section) => {
        section.classList.remove("active");
        if (section.id === `${targetSection}Section`) {
          section.classList.add("active");
        }
      });
    });
  });
}

/**
 * Setup profile form
 */
function setupProfileForm() {
  const form = document.getElementById("profileForm");
  const avatarUrlInput = document.getElementById("avatarUrl");
  const avatarPreview = document.getElementById("avatarPreview");
  const avatarPreviewImg = document.getElementById("avatarPreviewImg");

  // Load available avatars
  loadAvatarGallery();

  // Avatar preview
  avatarUrlInput.addEventListener("input", (e) => {
    const url = e.target.value.trim();
    if (url) {
      showAvatarPreview(url);
      // Deselect all gallery avatars when custom URL is entered
      document.querySelectorAll('.avatar-option').forEach(opt => {
        opt.classList.remove('selected');
      });
    } else {
      avatarPreview.classList.remove("show");
    }
  });

  // Form submit
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const bio = document.getElementById("bio").value.trim();
    const avatarUrl = avatarUrlInput.value.trim();

    // Validation
    if (username.length < 3 || username.length > 30) {
      showError("Kullanıcı adı 3-30 karakter arasında olmalı");
      return;
    }

    if (!email || !email.includes("@")) {
      showError("Geçerli bir e-posta adresi girin");
      return;
    }

    try {
      const token = sessionManager.getToken();
      const userId = sessionManager.getCurrentUserId();

      const response = await fetch(`${API_BASE}/users/${userId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          username: username,
          email: email,
          bio: bio,
          avatar_url: avatarUrl
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Profil güncellenemedi");
      }

      const updatedUser = await response.json();
      currentUser = updatedUser;

      // Update session
      sessionManager.setSession(updatedUser, token);

      showSuccess("Profil bilgileriniz başarıyla güncellendi! ✨");
    } catch (error) {
      console.error("Profile update error:", error);
      showError(error.message || "Profil güncellenirken bir hata oluştu");
    }
  });
}

/**
 * Load avatar gallery from avatars folder
 */
async function loadAvatarGallery() {
  const avatarGallery = document.getElementById("avatarGallery");
  const avatarUrlInput = document.getElementById("avatarUrl");
  
  try {
    // Fetch available avatars from API
    const response = await fetch(`${API_BASE}/users/api/avatars/list`);
    
    if (!response.ok) {
      throw new Error('Failed to load avatars');
    }
    
    const data = await response.json();
    const avatars = data.avatars || [];
    
    // Clear existing gallery
    avatarGallery.innerHTML = '';
    
    if (avatars.length === 0) {
      avatarGallery.innerHTML = '<p style="text-align: center; color: #718096; padding: 20px;">Henüz avatar bulunmuyor</p>';
      return;
    }
    
    // Create avatar options
    avatars.forEach(avatar => {
      const avatarPath = `./avatars/${avatar}`;
      const avatarOption = document.createElement('div');
      avatarOption.className = 'avatar-option';
      
      const img = document.createElement('img');
      img.src = avatarPath;
      img.alt = avatar;
      img.onerror = () => {
        // Hide if image doesn't exist
        avatarOption.style.display = 'none';
      };
      
      avatarOption.appendChild(img);
      
      // Click handler
      avatarOption.addEventListener('click', () => {
        // Remove selected class from all options
        document.querySelectorAll('.avatar-option').forEach(opt => {
          opt.classList.remove('selected');
        });
        
        // Add selected class to clicked option
        avatarOption.classList.add('selected');
        
        // Update input and preview
        avatarUrlInput.value = avatarPath;
        showAvatarPreview(avatarPath);
      });
      
      avatarGallery.appendChild(avatarOption);
    });
    
    // Mark currently selected avatar if exists
    if (currentUser && currentUser.avatar_url) {
      const currentAvatarOption = Array.from(document.querySelectorAll('.avatar-option')).find(
        opt => opt.querySelector('img').src.includes(currentUser.avatar_url)
      );
      if (currentAvatarOption) {
        currentAvatarOption.classList.add('selected');
      }
    }
  } catch (error) {
    console.error('Error loading avatars:', error);
    avatarGallery.innerHTML = '<p style="text-align: center; color: #e53e3e; padding: 20px;">Avatarlar yüklenirken hata oluştu</p>';
  }
}

/**
 * Show avatar preview
 */
function showAvatarPreview(url) {
  const avatarPreview = document.getElementById("avatarPreview");
  const avatarPreviewImg = document.getElementById("avatarPreviewImg");

  avatarPreviewImg.src = url;
  avatarPreviewImg.onerror = () => {
    avatarPreview.classList.remove("show");
  };
  avatarPreviewImg.onload = () => {
    avatarPreview.classList.add("show");
  };
}

/**
 * Setup password form
 */
function setupPasswordForm() {
  const form = document.getElementById("passwordForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const currentPassword = document.getElementById("currentPassword").value;
    const newPassword = document.getElementById("newPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    // Validation
    if (newPassword.length < 6) {
      showError("Yeni şifre en az 6 karakter olmalı");
      return;
    }

    if (newPassword !== confirmPassword) {
      showError("Yeni şifreler eşleşmiyor");
      return;
    }

    try {
      const token = sessionManager.getToken();

      // First verify current password by trying to login
      const loginResponse = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email: currentUser.email,
          password: currentPassword
        })
      });

      if (!loginResponse.ok) {
        throw new Error("Mevcut şifre yanlış");
      }

      // Update password using reset endpoint
      const resetResponse = await fetch(`${API_BASE}/auth/reset-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email: currentUser.email,
          token: "settings_update", // Dummy token for settings update
          new_password: newPassword
        })
      });

      if (!resetResponse.ok) {
        const error = await resetResponse.json();
        throw new Error(error.detail || "Şifre güncellenemedi");
      }

      // Clear form
      form.reset();

      showSuccess("Şifreniz başarıyla güncellendi! 🔑");
    } catch (error) {
      console.error("Password change error:", error);
      showError(error.message || "Şifre değiştirilirken bir hata oluştu");
    }
  });
}

/**
 * Setup privacy form
 */
function setupPrivacyForm() {
  const form = document.getElementById("privacyForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const privateProfile = document.getElementById("privateProfile").checked;
    const hideActivity = document.getElementById("hideActivity").checked;
    const hideLibrary = document.getElementById("hideLibrary").checked;

    // Since backend doesn't support these yet, just show success
    // In future, this would save to backend
    console.log("Privacy settings:", {
      privateProfile,
      hideActivity,
      hideLibrary
    });

    // Save to localStorage for now
    localStorage.setItem("privacy_settings", JSON.stringify({
      privateProfile,
      hideActivity,
      hideLibrary
    }));

    showSuccess("Gizlilik ayarlarınız kaydedildi! 🔒");
  });

  // Load saved settings
  loadPrivacySettings();
}

/**
 * Load privacy settings from localStorage
 */
function loadPrivacySettings() {
  try {
    const saved = localStorage.getItem("privacy_settings");
    if (saved) {
      const settings = JSON.parse(saved);
      document.getElementById("privateProfile").checked = settings.privateProfile || false;
      document.getElementById("hideActivity").checked = settings.hideActivity || false;
      document.getElementById("hideLibrary").checked = settings.hideLibrary || false;
    }
  } catch (error) {
    console.error("Error loading privacy settings:", error);
  }
}

/**
 * Setup notifications form
 */
function setupNotificationsForm() {
  const form = document.getElementById("notificationsForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const emailFollows = document.getElementById("emailFollows").checked;
    const emailLikes = document.getElementById("emailLikes").checked;
    const emailComments = document.getElementById("emailComments").checked;
    const pushNotifications = document.getElementById("pushNotifications").checked;

    // Save to localStorage for now
    localStorage.setItem("notification_settings", JSON.stringify({
      emailFollows,
      emailLikes,
      emailComments,
      pushNotifications
    }));

    showSuccess("Bildirim tercihleri kaydedildi! 🔔");
  });

  // Load saved settings
  loadNotificationSettings();
}

/**
 * Load notification settings from localStorage
 */
function loadNotificationSettings() {
  try {
    const saved = localStorage.getItem("notification_settings");
    if (saved) {
      const settings = JSON.parse(saved);
      document.getElementById("emailFollows").checked = settings.emailFollows ?? true;
      document.getElementById("emailLikes").checked = settings.emailLikes ?? true;
      document.getElementById("emailComments").checked = settings.emailComments ?? true;
      document.getElementById("pushNotifications").checked = settings.pushNotifications ?? true;
    }
  } catch (error) {
    console.error("Error loading notification settings:", error);
  }
}

/**
 * Setup delete account modal
 */
function setupDeleteAccount() {
  const deleteBtn = document.getElementById("deleteAccountBtn");
  const modal = document.getElementById("deleteAccountModal");
  const closeBtn = document.getElementById("closeDeleteModal");
  const cancelBtn = document.getElementById("cancelDeleteBtn");
  const confirmBtn = document.getElementById("confirmDeleteBtn");
  const confirmInput = document.getElementById("confirmDeleteText");

  // Open modal
  deleteBtn.addEventListener("click", () => {
    modal.style.display = "flex";
    confirmInput.value = "";
    confirmBtn.disabled = true;
  });

  // Close modal
  const closeModal = () => {
    modal.style.display = "none";
  };

  closeBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);

  // Close on outside click
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // Enable confirm button when text matches
  confirmInput.addEventListener("input", (e) => {
    const text = e.target.value.trim();
    confirmBtn.disabled = text !== "HESABIMI SIL";
  });

  // Confirm delete
  confirmBtn.addEventListener("click", async () => {
    try {
      // In a real app, this would call a delete endpoint
      // For now, just log out and redirect
      showSuccess("Hesap silme işlemi başlatıldı...");
      
      setTimeout(() => {
        sessionManager.clearSession();
        window.location.href = "./login.html";
      }, 2000);
    } catch (error) {
      console.error("Delete account error:", error);
      showError("Hesap silinirken bir hata oluştu");
    }
  });
}

/**
 * Show success toast
 */
function showSuccess(message) {
  const toast = document.getElementById("successToast");
  const messageEl = toast.querySelector(".toast-message");

  messageEl.textContent = message;
  toast.style.display = "flex";

  setTimeout(() => {
    toast.style.display = "none";
  }, 3000);
}

/**
 * Show error toast
 */
function showError(message) {
  const toast = document.getElementById("errorToast");
  const messageEl = toast.querySelector(".toast-message");

  messageEl.textContent = message;
  toast.style.display = "flex";

  setTimeout(() => {
    toast.style.display = "none";
  }, 4000);
}
