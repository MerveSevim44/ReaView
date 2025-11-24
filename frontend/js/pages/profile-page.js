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

// Current logged-in user
const currentUserId = sessionManager.getCurrentUserId();

// Profile user from URL
const profileUserId = Number(getQueryParam("user") || getQueryParam("id")) || currentUserId;

// DOM References
const followBtn = document.getElementById("mainFollowBtn");
const profileBox = document.getElementById("profileBox");
const activitiesMount = document.getElementById("activities");
const reviewsMount = document.getElementById("reviews");
const followListMount = document.getElementById("followList");

// Track following status
let followingStatus = {};

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
      loadFollowingStatus()
    ]);

    // Setup interactive elements
    setupFollowButton();
    setupFollowLists();
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
      ${isOwnProfile ? `<span class="profile-badge">🔵 Bu senin profilin</span>` : ""}
      ${user.bio ? `<p class="bio">${user.bio}</p>` : `<p class="muted bio">Biyografi yok.</p>`}
      <p class="muted" style="margin-top: 16px;">
        📅 Katıldı: ${formatDate(user.created_at)}
      </p>
    `;
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
