/**
 * Navbar Component
 * Shared navigation bar for all pages
 */

import { sessionManager } from "../core/session-manager.js";
import { handleLogout } from "../core/auth-handler.js";
import { getUserInitials } from "../utils/formatters.js";

/**
 * Initialize navbar
 */
export function initializeNavbar() {
  // Don't show navbar on login and register pages
  const currentPage = window.location.pathname.split("/").pop() || "";
  if (currentPage === "login.html" || currentPage === "register.html") {
    return;
  }

  const navbarContent = `
    <a href="./feed.html" class="navbar-brand">
      📚 BiblioNet
    </a>

    <div class="navbar-center">
      <ul class="navbar-nav">
        <li><a href="./feed.html" class="nav-link">📰 Akış</a></li>
        <li><a href="./explore.html" class="nav-link">🔍 Keşfet</a></li>
      </ul>
    </div>

    <div class="navbar-user">
      <!-- Show when not logged in -->
      <div class="auth-buttons" id="authButtons">
        <a href="./login.html" class="btn-login">🔐 Giriş Yap</a>
        <a href="./login.html" class="btn-register">✍️ Kayıt Ol</a>
      </div>

      <!-- Show when logged in -->
      <div class="user-dropdown" id="userDropdown" style="display: none;">
        <div class="user-info" id="userInfo">
          <div class="user-avatar" id="userAvatar">?</div>
          <div class="user-name" id="userName">Yükleniyor...</div>
        </div>
        <div class="dropdown-menu" id="dropdownMenu">
          <a href="./profile.html">👤 Profilim</a>
          <a href="./feed.html">📰 Akışım</a>
          <div class="dropdown-divider"></div>
          <a href="./settings.html">⚙️ Ayarlar</a>
          <button id="logoutBtn" class="logout-btn">🚪 Çıkış Yap</button>
        </div>
      </div>
    </div>
  `;

  // Check if navbar element exists (e.g., in list-detail.html)
  const existingNavbar = document.getElementById("navbar");
  if (existingNavbar && existingNavbar.classList.contains("navbar")) {
    // Navbar container exists, just fill it
    existingNavbar.innerHTML = navbarContent;
  } else {
    // No navbar element, create one
    const navbarHTML = `<nav class="navbar">${navbarContent}</nav>`;
    document.body.insertAdjacentHTML("afterbegin", navbarHTML);
  }

  // Add CSS file if not already added
  if (!document.querySelector('link[href="./css/navbar.css"]')) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "./css/navbar.css";
    document.head.appendChild(link);
  }

  // Setup event listeners
  setupNavbarEvents();

  // Check user status on load
  updateNavbarUser();

  // Listen for session changes
  window.addEventListener("userSessionChanged", updateNavbarUser);
  window.addEventListener("userSessionCleared", updateNavbarUser);
}

/**
 * Setup navbar event listeners
 */
function setupNavbarEvents() {
  const userInfo = document.getElementById("userInfo");
  const dropdownMenu = document.getElementById("dropdownMenu");
  const logoutBtn = document.getElementById("logoutBtn");

  // Toggle dropdown menu
  userInfo?.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdownMenu?.classList.toggle("show");
  });

  // Close menu when clicking outside
  document.addEventListener("click", () => {
    dropdownMenu?.classList.remove("show");
  });

  // Logout handler
  logoutBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    if (confirm("Çıkış yapmak istediğinize emin misiniz?")) {
      handleLogout();
      window.location.href = "./login.html";
    }
  });

  // Highlight current page
  highlightActivePage();
}

/**
 * Update navbar user information
 */
function updateNavbarUser() {
  const currentUser = sessionManager.getCurrentUser();
  const authButtons = document.getElementById("authButtons");
  const userDropdown = document.getElementById("userDropdown");
  const userName = document.getElementById("userName");
  const userAvatar = document.getElementById("userAvatar");

  if (currentUser) {
    // User is logged in
    authButtons.style.display = "none";
    userDropdown.style.display = "block";

    // Display user info
    userName.textContent = currentUser.username || "User";
    const initials = getUserInitials(currentUser.username || "U");
    userAvatar.textContent = initials;

    // Update profile link
    const profileLink = document.querySelector('a[href="./profile.html"]');
    if (profileLink) {
      const userId = currentUser.user_id || currentUser.id;
      profileLink.href = `./profile.html?user=${userId}`;
    }
  } else {
    // User is not logged in
    authButtons.style.display = "flex";
    userDropdown.style.display = "none";
  }
}

/**
 * Highlight the active page in navbar
 */
function highlightActivePage() {
  const currentPage = window.location.pathname.split("/").pop() || "feed.html";
  document.querySelectorAll(".nav-link").forEach((link) => {
    const href = link.getAttribute("href");
    if (href === "./" + currentPage || (currentPage === "" && href === "./feed.html")) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
}

/**
 * Initialize navbar on page load
 */
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeNavbar);
} else {
  initializeNavbar();
}
