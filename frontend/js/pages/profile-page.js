/**
 * Profile Page Module
 */

import {
  getUser,
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
const API_BASE = "http://rea-view.vercel.app";

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

    // Avatar URL - convert to proper path
    let avatarUrl = user.avatar_url;
    console.log(`📸 Avatar URL from API: ${avatarUrl}`);
    
    if (avatarUrl) {
      // If file:// protocol, extract filename and use API endpoint
      if (avatarUrl.startsWith('file://')) {
        const filename = avatarUrl.split('/').pop();
        avatarUrl = `${API_BASE}/users/avatars/${filename}`;
        console.log(`📸 Converted file:// to API endpoint: ${avatarUrl}`);
      }
      // If relative path (./avatars/), convert to absolute path
      else if (avatarUrl.startsWith('./avatars/')) {
        const filename = avatarUrl.replace('./avatars/', '');
        avatarUrl = `./avatars/${filename}`;
        console.log(`📸 Converted relative path: ${avatarUrl}`);
      }
    }
    
    // Fallback to generated avatar if no URL
    if (!avatarUrl) {
      avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.username)}&background=667eea&color=fff&bold=true`;
      console.log(`📸 Using generated avatar: ${avatarUrl}`);
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
    list_add: "listeye ekledi",
    like_review: "yorumu beğendi",
    like_item: "içeriği beğendi",
    comment_review: "yoruma yorum yaptı",
    follow: "takip etmeye başladı"
  };

  const actionText = activityTypes[activity.activity_type] || "bir şey yaptı";
  
  // Title'ı güvenli hale getir
  const displayTitle = activity.title && activity.title.trim() !== '' ? activity.title : 'İçerik';
  const titleText = activity.title ? ` - <em>${displayTitle}</em>` : "";
  
  // comment_review için review sahibinin adını da ekle
  let fullAction = actionText;
  let referencedReviewHtml = "";
  
  if (activity.activity_type === "comment_review" && activity.review_owner_username) {
    fullAction = `<strong>${activity.review_owner_username}</strong>'nin yorumuna yorum yaptı`;
    
    // Yorumun text'ini göster
    if (activity.referenced_review_text) {
      const truncated = activity.referenced_review_text.length > 150 
        ? activity.referenced_review_text.substring(0, 150) + '...' 
        : activity.referenced_review_text;
      referencedReviewHtml = `
        <div style="margin-top: 8px; padding: 8px; background: #f8f9fa; border-left: 2px solid #667eea; font-size: 12px; font-style: italic; color: #666;">
          "${truncated}"
        </div>
      `;
    }
  }

  return `
    <div class="activity-item">
      <div>
        <b>${activity.username || `User #${activity.user_id}`}</b>
        ${fullAction}${titleText}
        ${referencedReviewHtml}
      </div>
      <div class="muted" style="margin-top: 8px;">
        ${formatDateTime(activity.created_at)}
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
    const API_BASE = "http://rea-view.vercel.app";
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

  // Check if this is a "to-do" list that needs checkbox
  const showCheckbox = (status === 'towatch' || status === 'toread') && isOwnProfile;

  libraryContent.innerHTML = items.map(item => `
    <div class="library-item" 
         style="padding: 12px; border-bottom: 1px solid #eee; display: flex; gap: 12px; align-items: center; transition: background 0.3s;"
         onmouseover="this.style.backgroundColor='#f5f5f5'" 
         onmouseout="this.style.backgroundColor='transparent'">
      ${showCheckbox ? `
        <div class="checkbox-container" onclick="event.stopPropagation(); markAsCompleted(${item.item_id}, '${status}', this)" 
             style="cursor: pointer; flex-shrink: 0;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="custom-checkbox">
            <rect x="3" y="3" width="18" height="18" rx="4" stroke="#667eea" stroke-width="2" fill="white"/>
            <path d="M7 12L10.5 15.5L17 9" stroke="#667eea" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0" class="checkmark"/>
          </svg>
        </div>
      ` : ''}
      <div style="flex: 1; cursor: pointer;" onclick="window.location.href='items.html?id=${item.item_id}'">
        <div style="display: flex; gap: 12px;">
          <img src="${item.poster_url || 'https://via.placeholder.com/60x90'}" 
               alt="${item.title}"
               style="width: 60px; height: 90px; object-fit: cover; border-radius: 4px;">
          <div style="flex: 1;">
            <h3 style="margin: 0 0 4px 0; font-size: 14px;">${item.title}</h3>
            <p style="margin: 0; color: #999; font-size: 12px;">${item.item_type === 'movie' ? '🎬 Film' : '📖 Kitap'}</p>
            <p style="margin: 4px 0 0 0; color: #666; font-size: 12px;">Eklendi: ${new Date(item.added_at).toLocaleDateString('tr-TR')}</p>
          </div>
        </div>
      </div>
    </div>
  `).join("");

  // Add CSS for checkbox animation
  if (showCheckbox && !document.getElementById('checkbox-styles')) {
    const style = document.createElement('style');
    style.id = 'checkbox-styles';
    style.textContent = `
      .custom-checkbox {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .checkbox-container:hover .custom-checkbox rect {
        fill: #f0f4ff;
        stroke: #5568d3;
      }
      .custom-checkbox.checked rect {
        fill: #667eea;
        stroke: #667eea;
      }
      .custom-checkbox.checked .checkmark {
        opacity: 1;
        stroke: white;
      }
      @keyframes checkAnim {
        0% { transform: scale(0.8); opacity: 0; }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); opacity: 1; }
      }
      .custom-checkbox.checked {
        animation: checkAnim 0.3s ease-out;
      }
    `;
    document.head.appendChild(style);
  }
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

    // Fetch custom lists - current_user_id artık token'dan alınıyor
    const API_BASE = "http://rea-view.vercel.app";
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
      const emptyMessage = isOwnProfile 
        ? '✨ Henüz özel liste oluşturulmamış' 
        : '🔒 Bu kullanıcının herkese açık listesi yok';
      
      customLists.innerHTML = `
        <div class="empty-state">
          <p>${emptyMessage}</p>
        </div>
      `;
      return;
    }

    customLists.innerHTML = listsData.lists.map(list => {
      const privacyIcons = ['🔒', '👥', '🌐'];
      const privacyTexts = ['Özel', 'Takipçilerime Özel', 'Herkese Açık'];
      const privacyLevel = list.privacy_level !== undefined ? list.privacy_level : (list.is_public ? 2 : 0);
      const privacyIcon = privacyIcons[privacyLevel] || '🔒';
      const privacyText = privacyTexts[privacyLevel] || 'Özel';
      
      return `
        <div class="custom-list-item" style="padding: 12px; border-bottom: 1px solid #eee; cursor: pointer; transition: background 0.3s;" 
             onmouseover="this.style.backgroundColor='#f5f5f5'" 
             onmouseout="this.style.backgroundColor='transparent'"
             onclick="window.location.href='list-detail.html?id=${list.list_id}'">
          <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="flex: 1;">
              <h3 style="margin: 0 0 4px 0; font-size: 14px;">📝 ${list.name}</h3>
              <p style="margin: 0; color: #999; font-size: 12px;">${list.description || 'Açıklama yok'}</p>
              <p style="margin: 4px 0 0 0; color: #666; font-size: 12px;">📊 ${list.item_count} içerik</p>
            </div>
            <span style="font-size: 11px; color: #999; white-space: nowrap; margin-left: 8px;" title="${privacyText}">
              ${privacyIcon}
            </span>
          </div>
        </div>
      `;
    }).join("");
    
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
          const API_BASE = "http://rea-view.vercel.app";
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
  
  // Verify all modal elements exist
  const editProfileModal = document.getElementById("editProfileModal");
  const closeEditModal = document.getElementById("closeEditModal");
  const cancelEditBtn = document.getElementById("cancelEditBtn");
  const saveEditBtn = document.getElementById("saveEditBtn");
  const bioTextarea = document.getElementById("bioTextarea");
  const bioCharCount = document.getElementById("bioCharCount");
  const avatarPickerGrid = document.getElementById("avatarPickerGrid");
  const selectedAvatarColor = document.getElementById("selectedAvatarColor");

  console.log(`🔍 Edit button setup:`, {
    isOwnProfile,
    token: token ? "✅" : "❌",
    editProfileBtn: editProfileBtn ? "✅" : "❌",
    editProfileModal: editProfileModal ? "✅" : "❌",
    bioTextarea: bioTextarea ? "✅" : "❌",
    avatarPickerGrid: avatarPickerGrid ? "✅" : "❌"
  });
  
  if (!editProfileBtn || !isOwnProfile || !token) {
    console.log("⚠️ Edit button setup skipped - missing requirements");
    return;
  }

  if (!editProfileModal || !bioTextarea || !avatarPickerGrid) {
    console.error("❌ Modal elements not found in DOM");
    return;
  }

  // Load avatars dynamically
  loadAvatarsForProfile();

  // Open modal when edit button clicked
  editProfileBtn.addEventListener("click", () => {
    console.log("✏️ Profili düzenle modal açılıyor");
    
    // Reset form
    bioTextarea.value = userBio || "";
    bioCharCount.textContent = (userBio || "").length;
    
    // Show modal
    editProfileModal.style.display = "flex";
  });

  // Update character count
  bioTextarea.addEventListener("input", () => {
    bioCharCount.textContent = bioTextarea.value.length;
  });

  // Close modal buttons
  const closeModal = () => {
    editProfileModal.style.display = "none";
  };

  if (closeEditModal) closeEditModal.addEventListener("click", closeModal);
  if (cancelEditBtn) cancelEditBtn.addEventListener("click", closeModal);

  // Close modal when clicking outside
  editProfileModal.addEventListener("click", (e) => {
    if (e.target === editProfileModal) {
      closeModal();
    }
  });

  // Save profile
  if (saveEditBtn) {
    saveEditBtn.addEventListener("click", async () => {
      const newBio = bioTextarea.value.trim();
      const avatarUrl = selectedAvatarColor.value;

      console.log(`💾 Profil kaydediliyor:`, { bio: newBio, avatar: avatarUrl });

      saveEditBtn.disabled = true;
      try {
        const url = `${API_BASE}/users/${currentUserId}`;
        
        const response = await fetch(url, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${sessionManager.getToken()}`
          },
          body: JSON.stringify({ 
            bio: newBio,
            avatar_url: avatarUrl
          })
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          console.error(`❌ Profil güncelleme hatası: ${response.status}`, errorData);
          showErrorToast("❌ Profil güncellenirken hata oluştu!");
          return;
        }
        
        const updatedUser = await response.json();
        console.log("✅ Profil başarıyla güncellendi!", updatedUser);
        
        userBio = updatedUser.bio;
        showSuccess("✅ Profil başarıyla güncellendi!");
        closeModal();
        
        // UI'ı güncellemek için profili yeniden yükle
        setTimeout(() => {
          loadProfile();
        }, 500);
      } catch (error) {
        console.error(`❌ Profil güncelleme isteği başarısız:`, error.message);
        showErrorToast("❌ Profil güncellenirken hata oluştu!");
      } finally {
        saveEditBtn.disabled = false;
      }
    });
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
      
      // Gizlilik seçenekleri
      const privacyOptions = [
        "0 - 🔒 Sadece Ben (Özel)",
        "1 - 👥 Sadece Takipçilerim",
        "2 - 🌐 Herkes (Herkese Açık)"
      ];
      
      const privacyChoice = prompt(
        "Liste gizlilik ayarını seçin:\n\n" +
        privacyOptions.join("\n") +
        "\n\nLütfen 0, 1 veya 2 girin:",
        "0"
      );
      
      // Validate input
      const privacyLevel = parseInt(privacyChoice);
      if (![0, 1, 2].includes(privacyLevel)) {
        showError("Geçersiz gizlilik seçimi! 0, 1 veya 2 olmalı.");
        return;
      }
      
      try {
        const url4 = `${API_BASE}/items/custom-lists`;
        console.log(`📡 Yeni liste oluşturuluyor: ${url4}`, { 
          name: listName, 
          description, 
          privacy_level: privacyLevel
        });
        
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
            is_public: privacyLevel === 2 ? 1 : 0,
            privacy_level: privacyLevel
          })
        });

        const result = await response.json();

        if (!response.ok) {
          console.error(`❌ Liste oluşturma hatası: ${response.status}`, result);
          throw new Error(result.detail || "Liste oluşturulamadı");
        }
        console.log("✅ Liste başarıyla oluşturuldu", result);

        const privacyTexts = ["özel", "takipçilerime özel", "herkese açık"];
        showSuccess(`"${listName}" ${privacyTexts[privacyLevel]} liste olarak oluşturuldu!`);
        
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

/**
 * Mark item as completed (watched/read)
 */
window.markAsCompleted = async function(itemId, currentStatus, checkboxContainer) {
  try {
    const checkbox = checkboxContainer.querySelector('.custom-checkbox');
    
    // Visual feedback - immediately check the box
    checkbox.classList.add('checked');
    
    // Determine new status
    const newStatus = currentStatus === 'towatch' ? 'watched' : 'read';
    
    console.log(`✅ Durum değiştiriliyor: ${currentStatus} -> ${newStatus} (item: ${itemId})`);
    
    // Update status via API
    const response = await fetch(`${API_BASE}/items/${itemId}/library`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${sessionManager.getToken()}`
      },
      body: JSON.stringify({
        user_id: currentUserId,
        status: newStatus,
        action: "add"
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`❌ Durum güncelleme hatası: ${response.status}`, errorData);
      // Revert visual change
      checkbox.classList.remove('checked');
      throw new Error("Durum güncellenemedi");
    }

    const successMessage = currentStatus === 'towatch' ? '✅ İzledim olarak işaretlendi!' : '✅ Okudum olarak işaretlendi!';
    showSuccess(successMessage);
    
    // Wait a bit for animation then reload library
    setTimeout(async () => {
      await loadLibrary();
      
      // Switch to the appropriate tab
      const tabs = document.querySelectorAll(".tab-btn");
      const targetTab = currentStatus === 'towatch' ? 'watched' : 'read';
      tabs.forEach(tab => {
        if (tab.dataset.tab === targetTab) {
          tab.classList.add('active');
        } else {
          tab.classList.remove('active');
        }
      });
      
      // Render the new tab
      if (window.cachedLibraryGroups) {
        renderLibraryTab(targetTab, window.cachedLibraryGroups);
      }
    }, 800);

  } catch (error) {
    console.error("❌ İşaretleme hatası:", error);
    showErrorToast(`Hata: ${error.message}`);
  }
};

/**
 * Load avatars dynamically for profile edit modal
 */
async function loadAvatarsForProfile() {
  const avatarPickerGrid = document.getElementById("avatarPickerGrid");
  const selectedAvatarColor = document.getElementById("selectedAvatarColor");
  
  if (!avatarPickerGrid) {
    console.error("Avatar picker grid not found");
    return;
  }

  try {
    // Fetch available avatars from API
    const response = await fetch(`${API_BASE}/users/api/avatars/list`);
    
    if (!response.ok) {
      throw new Error('Failed to load avatars');
    }
    
    const data = await response.json();
    const avatars = data.avatars || [];
    
    // Clear existing grid
    avatarPickerGrid.innerHTML = '';
    
    if (avatars.length === 0) {
      avatarPickerGrid.innerHTML = '<p style="text-align: center; color: #718096; padding: 20px;">Henüz avatar bulunmuyor</p>';
      return;
    }
    
    // Create avatar options
    avatars.forEach((avatar, index) => {
      const avatarPath = `./avatars/${avatar}`;
      const avatarOption = document.createElement('div');
      avatarOption.className = 'avatar-option';
      avatarOption.style.cursor = 'pointer';
      avatarOption.title = avatar;
      avatarOption.dataset.avatar = avatarPath;
      
      const img = document.createElement('img');
      img.src = avatarPath;
      img.alt = avatar;
      img.className = 'avatar-img';
      img.onerror = () => {
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
        
        // Update hidden input
        selectedAvatarColor.value = avatarPath;
        console.log(`🎨 Avatar seçildi: ${avatarPath}`);
      });
      
      avatarPickerGrid.appendChild(avatarOption);
      
      // Select first avatar by default
      if (index === 0) {
        avatarOption.classList.add('selected');
        selectedAvatarColor.value = avatarPath;
      }
    });
    
    console.log(`✅ ${avatars.length} avatar yüklendi`);
  } catch (error) {
    console.error('Error loading avatars:', error);
    avatarPickerGrid.innerHTML = '<p style="text-align: center; color: #e53e3e; padding: 20px;">Avatarlar yüklenirken hata oluştu</p>';
  }
}
