// frontend/js/navbar.js
import { sessionManager } from "./session.js";
import { handleLogout } from "./auth.js";

/**
 * Navbar'ı HTML'e enjekte et
 */
export function initializeNavbar() {
  const navbarHTML = `
    <nav class="navbar">
      <a href="./feed.html" class="navbar-brand">
        📚 BiblioNet
      </a>

      <div class="navbar-center">
        <ul class="navbar-nav">
          <li><a href="./feed.html" class="nav-link">Akış</a></li>
          <li><a href="./explore.html" class="nav-link">Keşfet</a></li>
          <li><a href="./items.html" class="nav-link">İçerikler</a></li>
        </ul>
      </div>

      <div class="navbar-user">
        <!-- Giriş yapılmamışsa göster -->
        <div class="auth-buttons" id="authButtons">
          <a href="./login.html" class="btn-login">Giriş Yap</a>
          <a href="./login.html" class="btn-register">Kayıt Ol</a>
        </div>

        <!-- Giriş yapıldıysa göster -->
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
    </nav>
  `;

  // Body'nin en başına navbar'ı ekle
  document.body.insertAdjacentHTML("afterbegin", navbarHTML);

  // CSS dosyasını ekle
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "./css/navbar.css";
  document.head.appendChild(link);

  // Event listener'ları ekle
  setupNavbarEvents();

  // İlk yüklemede kullanıcı durumunu kontrol et
  updateNavbarUser();

  // Oturum değişikliğini dinle
  window.addEventListener("userSessionChanged", updateNavbarUser);
  window.addEventListener("userSessionCleared", updateNavbarUser);
}

/**
 * Navbar olaylarını kur
 */
function setupNavbarEvents() {
  const userInfo = document.getElementById("userInfo");
  const dropdownMenu = document.getElementById("dropdownMenu");
  const logoutBtn = document.getElementById("logoutBtn");

  // Dropdown menüsünü aç/kapat
  userInfo?.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdownMenu.classList.toggle("show");
  });

  // Dışa tıklanırsa menüyü kapat
  document.addEventListener("click", () => {
    dropdownMenu?.classList.remove("show");
  });

  // Çıkış düğmesi
  logoutBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    if (confirm("Çıkış yapmak istediğinize emin misiniz?")) {
      handleLogout();
      window.location.href = "./login.html";
    }
  });

  // Aktif sayfayı vurgula
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
 * Navbar kullanıcı bilgilerini güncelle
 */
function updateNavbarUser() {
  const currentUser = sessionManager.getCurrentUser();
  const authButtons = document.getElementById("authButtons");
  const userDropdown = document.getElementById("userDropdown");
  const userName = document.getElementById("userName");
  const userAvatar = document.getElementById("userAvatar");

  if (currentUser) {
    // Kullanıcı giriş yapmış
    authButtons.style.display = "none";
    userDropdown.style.display = "block";

    // Kullanıcı bilgilerini göster
    userName.textContent = currentUser.username || "Kullanıcı";
    const initials = (currentUser.username || "U")
      .substring(0, 2)
      .toUpperCase();
    userAvatar.textContent = initials;

    // Profil sayfasında kendi profilime git
    const profileLink = document.querySelector('a[href="./profile.html"]');
    if (profileLink) {
      const userId = currentUser.user_id || currentUser.id;
      profileLink.href = `./profile.html?user=${userId}`;
    }
  } else {
    // Kullanıcı giriş yapmamış
    authButtons.style.display = "flex";
    userDropdown.style.display = "none";
  }
}

/**
 * Sayfa yüklendiğinde navbar'ı başlat
 */
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeNavbar);
} else {
  initializeNavbar();
}
