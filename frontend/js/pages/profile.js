// ============================================
// PROFILE PAGE LOGIC
// ============================================

import { sessionManager } from "../session.js";
import * as API from "../api.js";

// Check if logged in
if (!sessionManager.isLoggedIn()) {
  window.location.href = "./login.html";
}

// ============================================
// DOM ELEMENTS
// ============================================

// Profile elements
const profileAvatar = document.getElementById("profileAvatar");
const profileName = document.getElementById("profileName");
const profileUsername = document.getElementById("profileUsername");
const profileBio = document.getElementById("profileBio");
const reviewCount = document.getElementById("reviewCount");
const followingCount = document.getElementById("followingCount");
const followerCount = document.getElementById("followerCount");

// Action buttons
const ownProfileActions = document.getElementById("ownProfileActions");
const otherProfileActions = document.getElementById("otherProfileActions");
const editProfileBtn = document.getElementById("editProfileBtn");
const createListBtn = document.getElementById("createListBtn");
const followBtn = document.getElementById("followBtn");

// Modals
const editProfileModal = document.getElementById("editProfileModal");
const createListModal = document.getElementById("createListModal");
const closeEditModal = document.getElementById("closeEditModal");
const closeListModal = document.getElementById("closeListModal");

// Forms
const editProfileForm = document.getElementById("editProfileForm");
const createListForm = document.getElementById("createListForm");
const editBioInput = document.getElementById("editBio");
const bioCharCount = document.getElementById("bioCharCount");

// Tabs
const tabButtons = document.querySelectorAll(".tab-button");
const tabContents = document.querySelectorAll(".tab-content");

// Library tabs
const libTabButtons = document.querySelectorAll(".lib-tab-button");
const libContents = document.querySelectorAll(".lib-content");

// Content containers
const watchedItems = document.getElementById("watchedItems");
const toWatchItems = document.getElementById("toWatchItems");
const readItems = document.getElementById("readItems");
const toReadItems = document.getElementById("toReadItems");
const customLists = document.getElementById("customLists");
const reviewsList = document.getElementById("reviewsList");

// ============================================
// STATE
// ============================================

let currentUser = sessionManager.getCurrentUser();
let viewingUserId = new URLSearchParams(window.location.search).get("user_id");
let isOwnProfile = !viewingUserId || viewingUserId == currentUser.user_id;

// ============================================
// INITIALIZATION
// ============================================

async function initializeProfile() {
  try {
    if (isOwnProfile) {
      // Load own profile
      await loadOwnProfile();
      ownProfileActions.style.display = "flex";
      otherProfileActions.style.display = "none";
    } else {
      // Load other user's profile
      await loadUserProfile(viewingUserId);
      ownProfileActions.style.display = "none";
      otherProfileActions.style.display = "flex";
    }

    // Load library data
    await loadLibraryData();

    // Load custom lists
    await loadCustomLists();

    // Load reviews
    await loadReviews();
  } catch (error) {
    console.error("Profil yükleme hatası:", error);
    showError("Profil yüklenirken hata oluştu");
  }
}

// ============================================
// LOAD PROFILE DATA
// ============================================

async function loadOwnProfile() {
  try {
    const user = await API.getCurrentUser();
    displayProfile(user);
  } catch (error) {
    console.error("Kendi profil yükleme hatası:", error);
  }
}

async function loadUserProfile(userId) {
  try {
    const user = await API.getUserProfile(userId);
    displayProfile(user);
  } catch (error) {
    console.error("Kullanıcı profili yükleme hatası:", error);
  }
}

function displayProfile(user) {
  profileName.textContent = user.username || "Kullanıcı";
  profileUsername.textContent = `@${user.username}`;
  profileBio.textContent = user.bio || "Biyografi henüz eklenmemiş";
  profileAvatar.src = user.avatar_url || "https://via.placeholder.com/150";

  // Update stats
  reviewCount.textContent = user.reviews_count || 0;
  followingCount.textContent = user.following_count || 0;
  followerCount.textContent = user.followers_count || 0;

  // Pre-fill edit form if own profile
  if (isOwnProfile) {
    editBioInput.value = user.bio || "";
    document.getElementById("editAvatar").value = user.avatar_url || "";
  }
}

// ============================================
// LIBRARY DATA
// ============================================

async function loadLibraryData() {
  try {
    const userId = isOwnProfile ? currentUser.user_id : viewingUserId;

    // Load watched items (films)
    const watchedReviews = await API.getUserReviews(userId, { type: "film", watched: true });
    displayItems(watchedItems, watchedReviews);

    // Load to-watch items
    const toWatchReviews = await API.getUserReviews(userId, { type: "film", watched: false });
    displayItems(toWatchItems, toWatchReviews);

    // Load read items (books)
    const readReviews = await API.getUserReviews(userId, { type: "book", read: true });
    displayItems(readItems, readReviews);

    // Load to-read items
    const toReadReviews = await API.getUserReviews(userId, { type: "book", read: false });
    displayItems(toReadItems, toReadReviews);
  } catch (error) {
    console.error("Kütüphane verisi yükleme hatası:", error);
  }
}

function displayItems(container, reviews) {
  if (!reviews || reviews.length === 0) {
    container.innerHTML = '<div class="empty-state">📭 Henüz öğe eklenmemiş</div>';
    return;
  }

  container.innerHTML = reviews.map((review) => `
    <div class="item-card" onclick="window.location.href='./items.html?id=${review.item_id}'">>
      <img src="${review.item_image || "https://via.placeholder.com/150x220"}" alt="${review.item_title}" class="item-image" />
      <div class="item-title">${review.item_title}</div>
    </div>
  `).join("");
}

// ============================================
// CUSTOM LISTS
// ============================================

async function loadCustomLists() {
  try {
    const userId = isOwnProfile ? currentUser.user_id : viewingUserId;
    const lists = await API.getUserLists(userId);

    if (!lists || lists.length === 0) {
      customLists.innerHTML = '<div class="empty-state">📋 Henüz liste oluşturulmamış</div>';
      return;
    }

    customLists.innerHTML = lists.map((list) => `
      <div class="list-card">
        <div class="list-header">
          <div class="list-title">${list.name}</div>
          ${isOwnProfile ? `
            <div class="list-actions">
              <button class="list-btn" title="Düzenle" onclick="editList(${list.list_id})">✏️</button>
              <button class="list-btn" title="Sil" onclick="deleteList(${list.list_id})">🗑️</button>
            </div>
          ` : ""}
        </div>
        <p class="list-description">${list.description || "Açıklama yok"}</p>
        <div class="list-stats">
          <div class="list-stat">
            <span class="list-stat-value">${list.items_count || 0}</span>
            <span>öğe</span>
          </div>
        </div>
      </div>
    `).join("");
  } catch (error) {
    console.error("Özel listeler yükleme hatası:", error);
  }
}

// ============================================
// REVIEWS
// ============================================

async function loadReviews() {
  try {
    const userId = isOwnProfile ? currentUser.user_id : viewingUserId;
    const reviews = await API.getUserReviews(userId);

    if (!reviews || reviews.length === 0) {
      reviewsList.innerHTML = '<div class="empty-state">💬 Henüz yorum yapılmamış</div>';
      return;
    }

    reviewsList.innerHTML = reviews.slice(0, 10).map((review) => `
      <div class="review-card">
        <div class="review-header">
          <div class="review-item-info">
            <div class="review-item-title">${review.item_title}</div>
            <div class="review-item-type">${review.item_type === "film" ? "Film" : "Kitap"}</div>
          </div>
          <div class="review-rating">
            <span class="rating-stars">${"⭐".repeat(review.rating)}</span>
            <span>${review.rating}/5</span>
          </div>
        </div>
        <p class="review-content">${review.review_text}</p>
        <p class="review-date">${new Date(review.created_at).toLocaleDateString("tr-TR")}</p>
      </div>
    `).join("");
  } catch (error) {
    console.error("Yorumlar yükleme hatası:", error);
  }
}

// ============================================
// MODALS & FORMS
// ============================================

// Edit Profile Modal
editProfileBtn?.addEventListener("click", () => {
  editProfileModal.style.display = "flex";
});

closeEditModal?.addEventListener("click", () => {
  editProfileModal.style.display = "none";
});

editProfileForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  try {
    const bio = editBioInput.value;
    const avatarUrl = document.getElementById("editAvatar").value;

    await API.updateProfile({ bio, avatar_url: avatarUrl });

    showSuccess("Profil başarıyla güncellendi");
    editProfileModal.style.display = "none";
    
    // Reload profile
    await loadOwnProfile();
  } catch (error) {
    showError(error.message || "Profil güncelleme hatası");
  }
});

// Bio character counter
editBioInput?.addEventListener("input", (e) => {
  const count = e.target.value.length;
  bioCharCount.textContent = `${count} / 200`;
});

// Create List Modal
createListBtn?.addEventListener("click", () => {
  createListModal.style.display = "flex";
  document.getElementById("listName").value = "";
  document.getElementById("listDescription").value = "";
});

closeListModal?.addEventListener("click", () => {
  createListModal.style.display = "none";
});

createListForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  try {
    const name = document.getElementById("listName").value;
    const description = document.getElementById("listDescription").value;

    await API.createList({ name, description });

    showSuccess("Liste başarıyla oluşturuldu");
    createListModal.style.display = "none";

    // Reload lists
    await loadCustomLists();
  } catch (error) {
    showError(error.message || "Liste oluşturma hatası");
  }
});

// ============================================
// TAB NAVIGATION
// ============================================

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    // Deactivate all tabs
    tabButtons.forEach((btn) => btn.classList.remove("active"));
    tabContents.forEach((content) => content.classList.remove("active"));

    // Activate clicked tab
    button.classList.add("active");
    const tabId = button.dataset.tab;
    document.getElementById(`${tabId}Tab`)?.classList.add("active");
  });
});

// Library sub-tabs
libTabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    // Deactivate all lib tabs
    libTabButtons.forEach((btn) => btn.classList.remove("active"));
    libContents.forEach((content) => content.classList.remove("active"));

    // Activate clicked tab
    button.classList.add("active");
    const tabId = button.dataset.libTab;
    document.getElementById(`${tabId}Content`)?.classList.add("active");
  });
});

// ============================================
// UTILITIES
// ============================================

function showSuccess(message) {
  // Simple alert - can be replaced with toast notification
  alert("✅ " + message);
}

function showError(message) {
  // Simple alert - can be replaced with toast notification
  alert("❌ " + message);
}

// Close modal when clicking outside
window.addEventListener("click", (e) => {
  if (e.target === editProfileModal) {
    editProfileModal.style.display = "none";
  }
  if (e.target === createListModal) {
    createListModal.style.display = "none";
  }
});

// ============================================
// START
// ============================================

initializeProfile();
