// profile.js
import { getUser, getUserReviews, getUserActivities, API_URL } from "./api.js";
import { sessionManager } from "./session.js";

// Current logged-in user from session
const currentUserId = sessionManager.getCurrentUserId();

// Profile user from URL
const urlParams = new URLSearchParams(window.location.search);
const profileUserId = Number(urlParams.get("user") || urlParams.get("id")) || currentUserId;

// DOM references
const followBtn = document.getElementById("mainFollowBtn");
const profileBox = document.getElementById("profileBox");
const activitiesMount = document.getElementById("activities");
const reviewsMount = document.getElementById("reviews");
const followListMount = document.getElementById("followList");

// Track following status
let followingStatus = {};

// Initialize on page load
window.addEventListener("DOMContentLoaded", async () => {
  await initializePage();
});

// === MAIN INITIALIZATION ===
async function initializePage() {
  try {
    // Oturum kontrolü
    if (!currentUserId) {
      profileBox.innerHTML = `
        <div class="error-message">
          <h3>❌ Giriş Gerekli</h3>
          <p>Bu sayfayı görmek için lütfen giriş yapınız.</p>
          <a href="./login.html" style="color: #667eea; text-decoration: underline;">Giriş Yap</a>
        </div>
      `;
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
      loadFollowingStatus()
    ]);

    // Setup interactive elements
    setupFollowButton();
    setupFollowLists();
  } catch (error) {
    console.error("Başlatma hatası:", error);
  }
}

// === LOAD PROFILE ===
async function loadProfile() {
  try {
    const user = await getUser(profileUserId);
    const isOwnProfile = currentUserId === profileUserId;
    
    profileBox.innerHTML = `
      <div class="profile-avatar">
        <img src="${user.avatar_url || "https://via.placeholder.com/120"}" 
             alt="${user.username} avatar" 
             width="120" 
             height="120">
      </div>
      <h2>@${user.username}</h2>
      <p class="muted">${user.email}</p>
      ${isOwnProfile ? `<span class="profile-badge">🔵 Bu senin profilin</span>` : ''}
      ${user.bio ? `<p class="bio">${user.bio}</p>` : '<p class="muted bio">Biyografi yok.</p>'}
      <p class="muted" style="margin-top: 16px;">
        📅 Katıldı: ${formatDate(user.created_at)}
      </p>
    `;
  } catch (error) {
    showError(profileBox, "Profil yüklenemedi", error);
  }
}

// === LOAD ACTIVITIES ===
async function loadActivities() {
  try {
    const acts = await getUserActivities(profileUserId);
    
    if (!acts || acts.length === 0) {
      activitiesMount.innerHTML = '<p class="empty-state">Henüz aktivite yok.</p>';
      return;
    }

    activitiesMount.innerHTML = acts
      .map(activity => renderActivity(activity))
      .join("");
  } catch (error) {
    showError(activitiesMount, "Aktiviteler alınamadı", error);
  }
}

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
        <b>${activity.username || 'Kullanıcı ' + activity.user_id}</b>
        ${actionText}${titleText}
      </div>
      <div class="muted" style="margin-top: 8px;">
        ${formatDateTime(activity.created_at)}
      </div>
    </div>
  `;
}

// === LOAD REVIEWS ===
async function loadReviews() {
  try {
    const revs = await getUserReviews(profileUserId);
    
    if (!revs || revs.length === 0) {
      reviewsMount.innerHTML = '<p class="empty-state">Henüz yorum yok.</p>';
      return;
    }

    reviewsMount.innerHTML = revs
      .map(review => renderReview(review))
      .join("");
  } catch (error) {
    showError(reviewsMount, "Yorumlar alınamadı", error);
  }
}

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

// === LOAD FOLLOWING STATUS ===
async function loadFollowingStatus() {
  try {
    const res = await fetch(`${API_URL}/users/${currentUserId}/following`);
    
    if (res.ok) {
      const following = await res.json();
      following.forEach(user => {
        followingStatus[user.user_id] = true;
      });
    }
  } catch (error) {
    console.warn("Could not load following status:", error);
  }
}

// === SETUP MAIN FOLLOW BUTTON ===
function setupFollowButton() {
  if (currentUserId === profileUserId) {
    return;
  }

  followBtn.style.display = "block";
  updateMainFollowButton();
  followBtn.addEventListener("click", toggleFollow);
}

function updateMainFollowButton() {
  const isFollowing = followingStatus[profileUserId];
  
  followBtn.textContent = isFollowing ? "✓ Takip Ediliyor" : "Takip Et";
  followBtn.className = isFollowing 
    ? "btn-primary btn-follow following" 
    : "btn-primary btn-follow";
}

async function toggleFollow() {
  const isFollowing = followingStatus[profileUserId];
  const method = isFollowing ? "DELETE" : "POST";
  const endpoint = isFollowing 
    ? `${API_URL}/users/${profileUserId}/unfollow?follower_id=${currentUserId}`
    : `${API_URL}/users/${profileUserId}/follow?follower_id=${currentUserId}`;

  followBtn.disabled = true;

  try {
    const res = await fetch(endpoint, { method });
    const data = await res.json();
    
    if (res.ok) {
      followingStatus[profileUserId] = !isFollowing;
      updateMainFollowButton();
    } else {
      showAlert(`❌ ${data.detail || "Hata oluştu"}`);
    }
  } catch (error) {
    showAlert("❌ Sunucu hatası: " + error.message);
  } finally {
    followBtn.disabled = false;
  }
}

// === SETUP FOLLOW/FOLLOWER LISTS ===
function setupFollowLists() {
  const followingBtn = document.getElementById("followingBtn");
  const followersBtn = document.getElementById("followersBtn");

  followingBtn.addEventListener("click", () => loadFollowing());
  followersBtn.addEventListener("click", () => loadFollowers());
}

async function loadFollowing() {
  followListMount.innerHTML = '<div class="loading">Yükleniyor...</div>';
  
  try {
    const res = await fetch(`${API_URL}/users/${profileUserId}/following`);
    
    if (!res.ok) throw new Error("API hatası");
    
    const following = await res.json();
    
    if (!following || following.length === 0) { 
      followListMount.innerHTML = '<p class="empty-state">Kimseyi takip etmiyor.</p>'; 
      return; 
    }
    
    followListMount.innerHTML = following.map(user => renderUserCard(user)).join("");
    attachFollowListeners();
  } catch (error) {
    showError(followListMount, "Takip listesi alınamadı", error);
  }
}

async function loadFollowers() {
  followListMount.innerHTML = '<div class="loading">Yükleniyor...</div>';
  
  try {
    const res = await fetch(`${API_URL}/users/${profileUserId}/followers`);
    
    if (!res.ok) throw new Error("API hatası");
    
    const followers = await res.json();
    
    if (!followers || followers.length === 0) { 
      followListMount.innerHTML = '<p class="empty-state">Takipçisi yok.</p>'; 
      return; 
    }
    
    followListMount.innerHTML = followers.map(user => renderUserCard(user)).join("");
    attachFollowListeners();
  } catch (error) {
    showError(followListMount, "Takipçi listesi alınamadı", error);
  }
}

// === RENDER USER CARD ===
function renderUserCard(user) {
  const isFollowing = followingStatus[user.user_id];
  const isCurrentUser = currentUserId === user.user_id;
  
  return `
    <div class="user-card">
      <div class="user-info">
        <a href="?id=${user.user_id}">@${user.username}</a>
        <div class="email muted">${user.email}</div>
      </div>
      ${!isCurrentUser ? `
        <button class="follow-btn ${isFollowing ? 'following' : 'follow'}" 
                data-user-id="${user.user_id}">
          ${isFollowing ? '✓ Takip Ediliyor' : 'Takip Et'}
        </button>
      ` : `<span class="muted" style="font-size: 12px;">Siz</span>`}
    </div>
  `;
}

// === ATTACH FOLLOW LISTENERS ===
function attachFollowListeners() {
  document.querySelectorAll('.follow-btn').forEach(btn => {
    btn.addEventListener('click', handleFollowClick);
  });
}

async function handleFollowClick(e) {
  const button = e.target;
  const userId = parseInt(button.dataset.userId);
  const isFollowing = followingStatus[userId];
  const method = isFollowing ? "DELETE" : "POST";
  const endpoint = isFollowing 
    ? `${API_URL}/users/${userId}/unfollow?follower_id=${currentUserId}`
    : `${API_URL}/users/${userId}/follow?follower_id=${currentUserId}`;

  button.disabled = true;

  try {
    const res = await fetch(endpoint, { method });
    const data = await res.json();
    
    if (res.ok) {
      followingStatus[userId] = !isFollowing;
      button.textContent = !isFollowing ? '✓ Takip Ediliyor' : 'Takip Et';
      button.className = !isFollowing ? 'follow-btn following' : 'follow-btn follow';
    } else {
      showAlert(`❌ ${data.detail || "Hata oluştu"}`);
    }
  } catch (error) {
    showAlert("❌ Sunucu hatası: " + error.message);
  } finally {
    button.disabled = false;
  }
}

// === UTILITY FUNCTIONS ===
function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("tr-TR", {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString("tr-TR", {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function showError(element, message, error) {
  console.error(message, error);
  element.innerHTML = `
    <div class="error">
      ❌ ${message}: ${error.message || 'Bilinmeyen hata'}
    </div>
  `;
}

function showAlert(message) {
  alert(message);
}