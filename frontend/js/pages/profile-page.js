/**
 * Profile Page Module
 */

import {
  getUser,
  getUserReviews,
  getUserActivities,
  getFollowing,
  getFollowers,
  followUser,
  unfollowUser
} from "../core/api-client.js";
import { sessionManager } from "../core/session-manager.js";
import { formatDate, formatDateTime } from "../utils/formatters.js";
import { getQueryParam } from "../utils/helpers.js";
import { Loader, showSuccess, showErrorToast } from "../components/loader.js";

// API Base URL
const API_BASE = "http://127.0.0.1:8000";

// Current logged-in user
const currentUserId = sessionManager.getCurrentUserId();

// Uyumluluk fonksiyonları
const showError = (msg) => {
  showErrorToast(msg);
};

// Profile user from URL
const profileUserId = Number(getQueryParam("user") || getQueryParam("id")) || currentUserId;

// DOM References
const followBtn = document.getElementById("mainFollowBtn");
const profileBox = document.getElementById("profileBox");
const activitiesMount = document.getElementById("activities");
const reviewsMount = document.getElementById("reviews");
const followListMount = document.getElementById("followList");
const libraryContent = document.getElementById("libraryContent");
const customLists = document.getElementById("customLists");
const createListBtn = document.getElementById("createListBtn");

// Track following status
let followingStatus = {};

// Track if viewing own profile
let isOwnProfile = false;

// Track user bio
let userBio = "";

/**
 * Initialize profile page
 */
window.addEventListener("DOMContentLoaded", async () => {
  await initializePage();
});

/**
 * Initialize page
 */
async function initializePage() {
  try {
    // Check authentication
    if (!currentUserId) {
      Loader.showError(profileBox, "Giriş Gerekli - Bu sayfayı görmek için lütfen giriş yapınız.");
      return;
    }

    // Hide follow button if viewing own profile
    if (currentUserId === profileUserId) {
      followBtn.style.display = "none";
    }

    // Load all data in parallel
    await Promise.all([
      loadProfile(),
      loadActivities(),
      loadReviews(),
      loadFollowingStatus(),
      loadLibrary(),
      loadCustomLists()
    ]);

    // Setup interactive elements
    setupFollowButton();
    setupFollowLists();
    setupLibraryTabs();
    setupEditProfileButton();
    setupCreateListButton();
  } catch (error) {
    console.error("Initialization error:", error);
    Loader.showError(profileBox, error.message);
  }
}

/**
 * Load and display user profile
 */
async function loadProfile() {
  try {
    const user = await getUser(profileUserId);
    isOwnProfile = currentUserId === profileUserId;
    userBio = user.bio || "";

    // Avatar URL - fallback to placeholder if file:// protocol
    let avatarUrl = user.avatar_url;
    console.log(`📸 Avatar URL from API: ${avatarUrl}`);
    console.log(`📸 Starts with file://? ${avatarUrl?.startsWith('file://')}`);
    
    if (!avatarUrl || avatarUrl.startsWith('file://')) {
      avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.username)}&background=667eea&color=fff&bold=true`;
      console.log(`📸 Using fallback: ${avatarUrl}`);
    }
    console.log(`📸 Final avatarUrl: ${avatarUrl}`);

    profileBox.innerHTML = `
      <div class="profile-avatar">
        <img src="${avatarUrl}"
             alt="${user.username} avatar"
             onerror="console.error('Avatar load failed:', this.src); this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(user.username)}&background=667eea&color=fff&bold=true'"
             onload="console.log('Avatar loaded successfully:', this.src)"
             width="120"
             height="120">
      </div>
      <h2>@${user.username}</h2>
      <p class="muted">${user.email}</p>
      ${isOwnProfile ? `<span class="profile-badge">🔵 Bu senin profilin</span>` : ""}
      ${user.bio ? `<p class="bio" id="profileBio">${user.bio}</p>` : `<p class="muted bio" id="profileBio">Biyografi yok.</p>`}
      <p class="muted" style="margin-top: 16px;">
        📅 Katıldı: ${formatDate(user.created_at)}
      </p>
    `;

    // Show edit button only on own profile
    const editProfileBtn = document.getElementById("editProfileBtn");
    if (editProfileBtn && isOwnProfile) {
      editProfileBtn.style.display = "block";
    }
  } catch (error) {
    Loader.showError(profileBox, `Profil yüklenemedi: ${error.message}`);
  }
}

/**
 * Load and display activities
 */
async function loadActivities() {
  try {
    const acts = await getUserActivities(profileUserId);

    if (!acts || acts.length === 0) {
      Loader.showEmpty(activitiesMount, "Henüz aktivite yok.");
      return;
    }

    activitiesMount.innerHTML = acts
      .map(activity => renderActivity(activity))
      .join("");
  } catch (error) {
    Loader.showError(activitiesMount, `Aktiviteler alınamadı: ${error.message}`);
  }
}

/**
 * Render activity item
 */
function renderActivity(activity) {
  const activityTypes = {
    review: "yorum yaptı",
    rating: "puan verdi",
    list_add: "listeye ekledi"
  };

  const actionText = activityTypes[activity.activity_type] || "bir şey yaptı";
  const titleText = activity.title ? `: <em>${activity.title}</em>` : "";

  return `
    <div class="activity-item">
      <div>
        <b>${activity.username || `User #${activity.user_id}`}</b>
        ${actionText}${titleText}
      </div>
      <div class="muted" style="margin-top: 8px;">
        ${formatDateTime(activity.created_at)}
      </div>
    </div>
  `;
}

/**
 * Load and display reviews
 */
async function loadReviews() {
  try {
    const revs = await getUserReviews(profileUserId);

    if (!revs || revs.length === 0) {
      Loader.showEmpty(reviewsMount, "Henüz yorum yok.");
      return;
    }

    reviewsMount.innerHTML = revs
      .map(review => renderReview(review))
      .join("");
  } catch (error) {
    Loader.showError(reviewsMount, `Yorumlar alınamadı: ${error.message}`);
  }
}

/**
 * Render review item
 */
function renderReview(review) {
  return `
    <div class="review-item">
      <div>${review.review_text}</div>
      <div class="muted" style="margin-top: 8px;">
        ${formatDateTime(review.created_at)}
      </div>
    </div>
  `;
}

/**
 * Load following status
 */
async function loadFollowingStatus() {
  try {
    const following = await getFollowing(currentUserId);
    following?.forEach(user => {
      followingStatus[user.user_id] = true;
    });
  } catch (error) {
    console.warn("Could not load following status:", error);
  }
}

/**
 * Setup follow button
 */
function setupFollowButton() {
  if (currentUserId === profileUserId) {
    return;
  }

  followBtn.style.display = "block";
  updateMainFollowButton();
  followBtn.addEventListener("click", toggleFollow);
}

/**
 * Update follow button appearance
 */
function updateMainFollowButton() {
  const isFollowing = followingStatus[profileUserId];
  followBtn.textContent = isFollowing ? "✓ Takip Ediliyor" : "Takip Et";
  followBtn.className = isFollowing
    ? "btn-primary btn-follow following"
    : "btn-primary btn-follow";
}

/**
 * Toggle follow status
 */
async function toggleFollow() {
  const isFollowing = followingStatus[profileUserId];
  followBtn.disabled = true;

  try {
    if (isFollowing) {
      await unfollowUser(profileUserId);
    } else {
      await followUser(profileUserId);
    }

    followingStatus[profileUserId] = !isFollowing;
    updateMainFollowButton();
    showSuccess(isFollowing ? "Takip bırakıldı" : "Takip ediliyor");
  } catch (error) {
    showErrorToast(error.message);
  } finally {
    followBtn.disabled = false;
  }
}

/**
 * Setup follow/follower lists
 */
function setupFollowLists() {
  const followingBtn = document.getElementById("followingBtn");
  const followersBtn = document.getElementById("followersBtn");

  followingBtn?.addEventListener("click", () => loadFollowing());
  followersBtn?.addEventListener("click", () => loadFollowers());
}

/**
 * Load and display following list
 */
async function loadFollowing() {
  Loader.show(followListMount, "Yükleniyor...");

  try {
    const following = await getFollowing(profileUserId);

    if (!following || following.length === 0) {
      Loader.showEmpty(followListMount, "Kimseyi takip etmiyor.");
      return;
    }

    followListMount.innerHTML = following
      .map(user => renderUserCard(user))
      .join("");
    attachFollowListeners();
  } catch (error) {
    Loader.showError(followListMount, `Takip listesi alınamadı: ${error.message}`);
  }
}

/**
 * Load and display followers list
 */
async function loadFollowers() {
  Loader.show(followListMount, "Yükleniyor...");

  try {
    const followers = await getFollowers(profileUserId);

    if (!followers || followers.length === 0) {
      Loader.showEmpty(followListMount, "Takipçisi yok.");
      return;
    }

    followListMount.innerHTML = followers
      .map(user => renderUserCard(user))
      .join("");
    attachFollowListeners();
  } catch (error) {
    Loader.showError(followListMount, `Takipçi listesi alınamadı: ${error.message}`);
  }
}

/**
 * Render user card
 */
function renderUserCard(user) {
  const isFollowing = followingStatus[user.user_id];
  const isCurrentUser = currentUserId === user.user_id;

  return `
    <div class="user-card">
      <div class="user-info">
        <a href="?user=${user.user_id}">@${user.username}</a>
        <div class="email muted">${user.email}</div>
      </div>
      ${
        !isCurrentUser
          ? `
        <button class="follow-btn ${isFollowing ? "following" : "follow"}"
                data-user-id="${user.user_id}">
          ${isFollowing ? "✓ Takip Ediliyor" : "Takip Et"}
        </button>
      `
          : `<span class="muted" style="font-size: 12px;">Siz</span>`
      }
    </div>
  `;
}

/**
 * Attach follow listeners
 */
function attachFollowListeners() {
  document.querySelectorAll(".follow-btn").forEach(btn => {
    btn.addEventListener("click", handleFollowClick);
  });
}

/**
 * Handle follow button click
 */
async function handleFollowClick(e) {
  const button = e.target;
  const userId = parseInt(button.dataset.userId);
  const isFollowing = followingStatus[userId];

  button.disabled = true;

  try {
    if (isFollowing) {
      await unfollowUser(userId);
    } else {
      await followUser(userId);
    }

    followingStatus[userId] = !isFollowing;
    button.textContent = !isFollowing ? "✓ Takip Ediliyor" : "Takip Et";
    button.className = !isFollowing ? "follow-btn following" : "follow-btn follow";
  } catch (error) {
    showErrorToast(error.message);
  } finally {
    button.disabled = false;
  }
}

/**
 * Load and display user library
 */
async function loadLibrary() {
  try {
    // Fetch user library
    const API_BASE = "http://127.0.0.1:8000";
    const url1 = `${API_BASE}/items/library/${profileUserId}`;
    console.log(`📡 Kütüphane yükleniyor: ${url1}`);
    
    const response = await fetch(url1, {
      headers: {
        "Authorization": `Bearer ${sessionManager.getToken()}`
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`❌ Kütüphane yükleme hatası: ${response.status}`, errorData);
      throw new Error("Kütüphane yüklenemedi");
    }
    console.log("✅ Kütüphane başarıyla yüklendi");
    
    const libraryData = await response.json();
    console.log("📚 User Library:", libraryData);

    if (!libraryData.items || libraryData.items.length === 0) {
      libraryContent.innerHTML = `
        <div class="empty-state">
          <p>📚 Henüz hiç içerik eklenmedi</p>
        </div>
      `;
      return;
    }

    // Group items by status
    const grouped = {};
    libraryData.items.forEach(item => {
      if (!grouped[item.status]) grouped[item.status] = [];
      grouped[item.status].push(item);
    });

    // Cache grouped items for tab switching
    window.cachedLibraryGroups = grouped;

    // Render watched tab by default
    renderLibraryTab("watched", grouped);
    
  } catch (error) {
    console.error("Library error:", error);
    Loader.showError(libraryContent, `Kütüphane yüklenemedi: ${error.message}`);
  }
}

/**
 * Render library tab content
 */
function renderLibraryTab(status, grouped) {
  const items = grouped[status] || [];
  
  if (items.length === 0) {
    libraryContent.innerHTML = `
      <div class="empty-state">
        <p>📚 Bu kategoride içerik yok</p>
      </div>
    `;
    return;
  }

  libraryContent.innerHTML = items.map(item => `
    <div class="library-item" style="padding: 12px; border-bottom: 1px solid #eee; display: flex; gap: 12px;">
      <img src="${item.poster_url || 'https://via.placeholder.com/60x90'}" 
           alt="${item.title}"
           style="width: 60px; height: 90px; object-fit: cover; border-radius: 4px;">
      <div style="flex: 1;">
        <h3 style="margin: 0 0 4px 0; font-size: 14px;">${item.title}</h3>
        <p style="margin: 0; color: #999; font-size: 12px;">${item.item_type === 'movie' ? '🎬 Film' : '📖 Kitap'}</p>
        <p style="margin: 4px 0 0 0; color: #666; font-size: 12px;">Eklendi: ${new Date(item.added_at).toLocaleDateString('tr-TR')}</p>
      </div>
    </div>
  `).join("");
}

/**
 * Load and display custom lists
 */
async function loadCustomLists() {
  try {
    const isOwnProfile = currentUserId === profileUserId;
    const createListBtn = document.getElementById("createListBtn");

    // Show create list button only on own profile
    if (createListBtn && isOwnProfile) {
      createListBtn.style.display = "block";
    }

    // Fetch custom lists
    const API_BASE = "http://127.0.0.1:8000";
    const url2 = `${API_BASE}/items/custom-lists/${profileUserId}`;
    console.log(`📡 Özel Listeler yükleniyor: ${url2}`);
    
    const response = await fetch(url2, {
      headers: {
        "Authorization": `Bearer ${sessionManager.getToken()}`
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`❌ Özel Listeler yükleme hatası: ${response.status}`, errorData);
      throw new Error("Listeler yüklenemedi");
    }
    console.log("✅ Özel Listeler başarıyla yüklendi");
    
    const listsData = await response.json();
    console.log("✨ Custom Lists:", listsData);

    if (!listsData.lists || listsData.lists.length === 0) {
      customLists.innerHTML = `
        <div class="empty-state">
          <p>✨ Henüz özel liste oluşturulmamış</p>
        </div>
      `;
      return;
    }

    customLists.innerHTML = listsData.lists.map(list => `
      <div class="custom-list-item" style="padding: 12px; border-bottom: 1px solid #eee; cursor: pointer; transition: background 0.3s;" 
           onmouseover="this.style.backgroundColor='#f5f5f5'" 
           onmouseout="this.style.backgroundColor='transparent'"
           onclick="window.location.href='list-detail.html?id=${list.list_id}'">
        <h3 style="margin: 0 0 4px 0; font-size: 14px;">📝 ${list.name}</h3>
        <p style="margin: 0; color: #999; font-size: 12px;">${list.description || 'Açıklama yok'}</p>
        <p style="margin: 4px 0 0 0; color: #666; font-size: 12px;">📊 ${list.item_count} içerik</p>
      </div>
    `).join("");
    
  } catch (error) {
    console.error("Custom lists error:", error);
    Loader.showError(customLists, `Listeler yüklenemedi: ${error.message}`);
  }
}

/**
 * Setup library tabs
 */
function setupLibraryTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  let groupedItems = {}; // Cache grouped items
  
  // Store grouped items from loadLibrary
  const originalLoadLibrary = loadLibrary;
  window.cachedLibraryGroups = {};
  
  tabs.forEach(tab => {
    tab.addEventListener("click", async (e) => {
      tabs.forEach(t => t.classList.remove("active"));
      e.target.classList.add("active");
      
      const tabName = e.target.dataset.tab;
      console.log("📂 Tab clicked:", tabName);
      
      // Map tab names to database status values
      const statusMap = {
        'watched': 'watched',
        'watchlist': 'towatch',
        'read': 'read',
        'readlist': 'toread'
      };
      
      const status = statusMap[tabName];
      
      // If we have cached data, render it
      if (window.cachedLibraryGroups && window.cachedLibraryGroups[status]) {
        renderLibraryTab(status, window.cachedLibraryGroups);
      } else {
        // Otherwise fetch for this specific status
        try {
          const API_BASE = "http://127.0.0.1:8000";
          const url3 = `${API_BASE}/items/library/${profileUserId}?status=${status}`;
          console.log(`📡 Kütüphane sekmesi yükleniyor (${status}): ${url3}`);
          
          const response = await fetch(url3, {
            headers: {
              "Authorization": `Bearer ${sessionManager.getToken()}`
            }
          });
          
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error(`❌ Kütüphane sekmesi yükleme hatası (${status}): ${response.status}`, errorData);
            throw new Error("Veri yüklenemedi");
          }
          console.log(`✅ Kütüphane sekmesi (${status}) başarıyla yüklendi`);
          
          const data = await response.json();
          
          if (data.items && data.items.length > 0) {
            const grouped = {};
            grouped[status] = data.items;
            renderLibraryTab(status, grouped);
          } else {
            libraryContent.innerHTML = `<div class="empty-state"><p>📚 Bu kategoride içerik yok</p></div>`;
          }
        } catch (error) {
          console.error("Tab error:", error);
          Loader.showError(libraryContent, `Yükleme başarısız: ${error.message}`);
        }
      }
    });
  });
}

function setupEditProfileButton() {
  const editProfileBtn = document.getElementById("editProfileBtn");
  const token = sessionManager.getToken();
  console.log(`🔍 Edit button setup: isOwnProfile=${isOwnProfile}, token=${token ? "✅" : "❌ null"}, button=${editProfileBtn ? "✅" : "❌ null"}`);
  
  if (editProfileBtn && isOwnProfile && token) {
    editProfileBtn.addEventListener("click", async () => {
      console.log("✏️ Profili düzenle tıklandı");
      
      const newBio = prompt("Biyografını güncelle:", userBio || "");
      
      if (newBio === null) return; // Kullanıcı iptal etti
      
      try {
        const url = `${API_BASE}/users/${currentUserId}`;
        console.log(`📡 Profil güncelleniyor: ${url}`, { bio: newBio });
        
        const response = await fetch(url, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${sessionManager.getToken()}`
          },
          body: JSON.stringify({ bio: newBio })
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          console.error(`❌ Profil güncelleme hatası: ${response.status}`, errorData);
          alert("❌ Profil güncellenirken hata oluştu!");
          return;
        }
        
        const updatedUser = await response.json();
        console.log("✅ Profil başarıyla güncellendi!", updatedUser);
        
        userBio = updatedUser.bio;
        showSuccess("✅ Biyografi başarıyla güncellendi!");
        
        // UI'ı güncellemek için profili yeniden yükle
        setTimeout(() => {
          loadProfile();
        }, 500);
      } catch (error) {
        console.error(`❌ Profil güncelleme isteği başarısız:`, error.message);
        alert("❌ Profil güncellenirken hata oluştu!");
      }
    });
  } else if (!token) {
    console.log("⚠️ Token bulunamadı - Profili düzenle butonu devre dışı");
  }
}

/**
 * Setup create list button
 */
function setupCreateListButton() {
  const createListBtn = document.getElementById("createListBtn");
  if (createListBtn) {
    createListBtn.addEventListener("click", async () => {
      const listName = prompt("Liste adını girin:");
      if (!listName || !listName.trim()) return;

      const description = prompt("Liste açıklaması (opsiyonel):", "");
      
      try {
        const url4 = `${API_BASE}/items/custom-lists`;
        console.log(`📡 Yeni liste oluşturuluyor: ${url4}`, { name: listName, description });
        
        const response = await fetch(url4, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${sessionManager.getToken()}`
          },
          body: JSON.stringify({
            user_id: currentUserId,
            name: listName.trim(),
            description: description || "",
            is_public: 0
          })
        });

        const result = await response.json();

        if (!response.ok) {
          console.error(`❌ Liste oluşturma hatası: ${response.status}`, result);
          throw new Error(result.detail || "Liste oluşturulamadı");
        }
        console.log("✅ Liste başarıyla oluşturuldu", result);

        console.log("✅ Liste oluşturuldu:", result);
        showSuccess(`"${listName}" listesi başarıyla oluşturuldu!`);
        
        // Listeyi yeniden yükle
        setTimeout(() => {
          loadCustomLists();
        }, 500);

      } catch (error) {
        console.error("❌ Liste oluşturma hatası:", error);
        showError(`Hata: ${error.message}`);
      }
    });
  }
}
