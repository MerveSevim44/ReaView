/**
 * Feed Page Module
 * Display user activity feed
 */

import {
  getItemById,
  getFeed
} from "../core/api-client.js";
import { sessionManager } from "../core/session-manager.js";
import { formatRelativeTime } from "../utils/formatters.js";
import { ACTIVITY_DESCRIPTIONS } from "../utils/constants.js";
import { Loader, showSuccess } from "../components/loader.js";

// DOM References
const feedContainer = document.getElementById("feed-container");

/**
 * Initialize feed page
 */
window.addEventListener("DOMContentLoaded", async () => {
  await initializeFeed();
});

/**
 * Initialize feed
 */
async function initializeFeed() {
  try {
    // Check authentication
    if (!sessionManager.isLoggedIn()) {
      showAuthMessage();
      return;
    }

    console.log("✅ User logged in, loading feed...");
    await loadFeed();
  } catch (error) {
    console.error("Feed initialization error:", error);
    Loader.showError(feedContainer, error.message);
  }
}

/**
 * Show authentication message
 */
function showAuthMessage() {
  feedContainer.innerHTML = `
    <div class="auth-message">
      <h3>👋 Hoş geldiniz!</h3>
      <p>Akışı görmek için lütfen giriş yapınız.</p>
      <a href="./login.html">Giriş Yap veya Kayıt Ol</a>
    </div>
  `;
}

/**
 * Load feed data
 */
async function loadFeed() {
  try {
    Loader.show(feedContainer, "📡 Akış yükleniyor...");

    const currentUser = sessionManager.getCurrentUser();
    if (!currentUser) {
      showAuthMessage();
      return;
    }

    const activities = await getFeed(currentUser.id);
    console.log(`✅ Loaded ${activities.length} activities`);

    if (!activities || activities.length === 0) {
      Loader.showEmpty(feedContainer, "📭 Henüz aktivite yok. Kullanıcıları takip etmeye başlayın!");
      return;
    }

    // Render activities
    feedContainer.innerHTML = activities
      .map(activity => renderActivityCard(activity))
      .join("");

    // Bind event listeners
    bindActivityEvents();
  } catch (error) {
    console.error("Feed loading error:", error);
    Loader.showError(feedContainer, `Akış yüklenemedi: ${error.message}`);
  }
}

/**
 * Render activity card
 */
function renderActivityCard(activity) {
  const actionText = ACTIVITY_DESCRIPTIONS[activity.activity_type] || "bir işlem yaptı";
  const timestamp = formatRelativeTime(activity.created_at);
  const username = activity.username || `User #${activity.user_id}`;
  const itemTitle = activity.title ? `<em>${activity.title}</em>` : "—";
  const activityId = activity.activity_id || activity.item_id || 0;

  return `
    <div class="card activity-card" data-activity-id="${activityId}">
      <div class="activity-header">
        <strong>👤 ${username}</strong>
        <span class="activity-action">${actionText}</span>
      </div>
      <div class="activity-item-title">
        📚 ${itemTitle}
      </div>
      <div class="activity-timestamp">
        <small>⏰ ${timestamp}</small>
      </div>
      <div class="activity-actions">
        <button class="btn btn-like" title="Beğen">
          <span class="like-icon">🤍</span>
          <span class="like-count">0</span>
        </button>
        <button class="btn btn-comment" title="Yorum Yap">
          <span class="comment-icon">💬</span>
          <span class="comment-count">0</span>
        </button>
        <button class="btn btn-share" title="Paylaş">
          <span class="share-icon">📤</span>
        </button>
      </div>
    </div>
  `;
}

/**
 * Bind activity interactions
 */
let eventListenerBound = false;

function bindActivityEvents() {
  if (eventListenerBound) return;

  feedContainer.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn");
    if (!btn) return;

    const card = btn.closest(".activity-card");
    if (!card) return;

    e.preventDefault();
    const activityId = card.getAttribute("data-activity-id");

    if (btn.classList.contains("btn-like")) {
      handleLike(btn, activityId);
    } else if (btn.classList.contains("btn-comment")) {
      handleComment(btn, activityId);
    } else if (btn.classList.contains("btn-share")) {
      handleShare(card);
    }
  });

  eventListenerBound = true;
}

/**
 * Handle like action
 */
function handleLike(btn, activityId) {
  btn.classList.toggle("liked");
  const icon = btn.querySelector(".like-icon");
  const count = btn.querySelector(".like-count");

  if (btn.classList.contains("liked")) {
    icon.textContent = "❤️";
    count.textContent = parseInt(count.textContent) + 1;
  } else {
    icon.textContent = "🤍";
    count.textContent = Math.max(0, parseInt(count.textContent) - 1);
  }

  console.log(`👍 Activity ${activityId} liked`);
}

/**
 * Handle comment action
 */
function handleComment(btn, activityId) {
  const commentText = prompt("💬 Yorum yazınız:\n(Test amaçlı, kaydedilmez)");

  if (commentText && commentText.trim()) {
    const count = btn.querySelector(".comment-count");
    const oldCount = parseInt(count.textContent);
    count.textContent = oldCount + 1;
    btn.style.color = "#667eea";
    btn.querySelector(".comment-icon").textContent = "💙";
    showSuccess("Yorum başarıyla eklendi!");
  }
}

/**
 * Handle share action
 */
function handleShare(card) {
  const username = card.querySelector(".activity-header strong").textContent;
  const action = card.querySelector(".activity-action").textContent;
  const title = card.querySelector(".activity-item-title").textContent;
  const shareText = `${username} ${action}\n${title}`;

  if (navigator.share) {
    navigator.share({
      title: "BiblioNet Activity",
      text: shareText
    }).catch(err => console.log("Share failed:", err));
  } else {
    navigator.clipboard.writeText(shareText).then(() => {
      showSuccess("Aktivite panoya kopyalandı!");
    });
  }
}
