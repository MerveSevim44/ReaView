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
  // Don't show navbar on auth pages (login, register, forgot-password, reset-password)
  const currentPage = window.location.pathname.split("/").pop() || "";
  const authPages = [
    "login.html",
    "register.html",
    "forgot-password.html",
    "reset-password.html",
    "login",
    "register",
    "forgot-password",
    "reset-password",
  ];
  if (authPages.includes(currentPage)) {
    return;
  }

  // Inject critical runtime styles to prevent any overlay/pseudo-element blocking clicks
  if (!document.getElementById("navbar-fix-style")) {
    const fixStyle = document.createElement("style");
    fixStyle.id = "navbar-fix-style";
    fixStyle.textContent = `
      .navbar::before, .navbar::after {
        display: none !important;
        content: none !important;
        pointer-events: none !important;
        width: 0 !important;
        height: 0 !important;
      }
      .navbar {
        position: sticky !important;
        z-index: 1000 !important;
        pointer-events: auto !important;
      }
      .navbar-user, .auth-buttons, .btn-login, .btn-register, .navbar-brand, .navbar-nav, .navbar-nav a {
        position: relative !important;
        z-index: 10001 !important;
        pointer-events: auto !important;
        cursor: pointer !important;
      }
    `;
    document.head.appendChild(fixStyle);
  }

  const navbarContent = `
    <a href="./feed.html" class="navbar-brand" style="position: relative; z-index: 10001; pointer-events: auto;">
      📚 BiblioNet
    </a>

    <div class="navbar-center" style="position: relative; z-index: 10001; pointer-events: auto;">
      <ul class="navbar-nav" style="position: relative; z-index: 10001; pointer-events: auto;">
        <li><a href="./feed.html" class="nav-link">📰 Akış</a></li>
        <li><a href="./explore.html" class="nav-link">🔍 Keşfet</a></li>
      </ul>
    </div>

    <div class="navbar-user" style="position: relative; z-index: 10001; pointer-events: auto;">
      <!-- Show when not logged in -->
      <div class="auth-buttons" id="authButtons" style="display: flex; gap: 10px; position: relative; z-index: 10001; pointer-events: auto;">
        <a href="./login.html" class="btn-login" id="navBtnLogin" data-auth-link="login" style="position: relative; z-index: 10002; pointer-events: auto; cursor: pointer;">🔐 Giriş Yap</a>
        <a href="./register.html" class="btn-register" id="navBtnRegister" data-auth-link="register" style="position: relative; z-index: 10002; pointer-events: auto; cursor: pointer;">✍️ Kayıt Ol</a>
      </div>

      <!-- Show when logged in -->
      <div class="user-dropdown" id="userDropdown" style="display: none; position: relative; z-index: 10001;">
        <div class="user-info" id="userInfo" style="position: relative; z-index: 10002; cursor: pointer;">
          <div class="user-avatar" id="userAvatar">?</div>
          <div class="user-name" id="userName">Yükleniyor...</div>
        </div>
        <div class="dropdown-menu" id="dropdownMenu" style="position: absolute; z-index: 10005;">
          <a href="./profile.html">👤 Profilim</a>
          <a href="./feed.html">📰 Akışım</a>
          <div class="dropdown-divider"></div>
          <a href="./settings.html">⚙️ Ayarlar</a>
          <button id="logoutBtn" class="logout-btn">🚪 Çıkış Yap</button>
        </div>
      </div>
    </div>
  `;

  // Check if navbar already exists on the page
  let existingNavbar = document.querySelector(".navbar");

  if (existingNavbar) {
    // Navbar already exists, just update its content
    existingNavbar.innerHTML = navbarContent;
  } else {
    // Check if there's a navbar container element
    const navbarContainer = document.getElementById("navbar");
    if (navbarContainer) {
      // Use the existing container
      navbarContainer.className = "navbar";
      navbarContainer.innerHTML = navbarContent;
    } else {
      // Create a new navbar element
      const navbarHTML = `<nav class="navbar">${navbarContent}</nav>`;
      document.body.insertAdjacentHTML("afterbegin", navbarHTML);
    }
  }

  // Add CSS file if not already added
  const existingLink = document.querySelector('link[href*="navbar.css"]');
  if (!existingLink) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "./css/navbar.css?v=20260817b";
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

  const btnLogin = document.getElementById("navBtnLogin") || document.querySelector(".btn-login");
  if (btnLogin) {
    const goToLogin = (e) => {
      e.preventDefault();
      e.stopPropagation();
      window.location.href = "./login.html";
    };
    btnLogin.onclick = goToLogin;
    btnLogin.addEventListener("click", goToLogin);
  }

  const btnRegister = document.getElementById("navBtnRegister") || document.querySelector(".btn-register");
  if (btnRegister) {
    const goToRegister = (e) => {
      e.preventDefault();
      e.stopPropagation();
      window.location.href = "./register.html";
    };
    btnRegister.onclick = goToRegister;
    btnRegister.addEventListener("click", goToRegister);
  }

  document.querySelectorAll("[data-auth-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      const href = link.getAttribute("href");
      if (href) {
        window.location.href = href;
      }
    });
  });

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
    if (authButtons) authButtons.style.display = "none";
    if (userDropdown) userDropdown.style.display = "block";

    // Display user info
    if (userName) userName.textContent = currentUser.username || "User";
    if (userAvatar) {
      const initials = getUserInitials(currentUser.username || "U");
      userAvatar.textContent = initials;
    }

    // Update profile link
    const profileLink = document.querySelector('a[href="./profile.html"]');
    if (profileLink) {
      const userId = currentUser.user_id || currentUser.id;
      profileLink.href = `./profile.html?user=${userId}`;
    }
  } else {
    // User is not logged in
    if (authButtons) authButtons.style.display = "flex";
    if (userDropdown) userDropdown.style.display = "none";
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
