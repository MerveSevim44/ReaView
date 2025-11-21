// frontend/js/feed.js
// Display user activity feed with interactive buttons

import { API_URL, getItems } from "./api.js";
import { sessionManager } from "./session.js";

// DOM references
const feedContainer = document.getElementById("feed-container");

// Activity type descriptions
const activityDescriptions = {
  "review": "yorum yaptı",
  "rating": "puan verdi",
  "list_add": "listeye ekledi",
  "follow": "kullanıcıyı takip etti",
  "comment": "yorum yaptı",
  "rated": "puan verdi",
  "added_to_list": "listesine ekledi",
  "favorited": "favorilerine ekledi"
};

// Initialize on page load
window.addEventListener("DOMContentLoaded", async () => {
  await initializeFeed();
});

// === MAIN INITIALIZATION ===
async function initializeFeed() {
  try {
    // Oturum kontrolü
    if (!sessionManager.isLoggedIn()) {
      showAuthMessage();
      return;
    }

    // Giriş yapıldıysa, kişisel akışı yükle
    const currentUser = sessionManager.getCurrentUser();
    console.log("✅ Aktif kullanıcı:", currentUser);
    
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get("user_id") || currentUser.id;
    
    console.log("🔄 Yükleniyor - Kullanıcı ID:", userId);
    await loadFeed();
  } catch (error) {
    console.error("Feed başlatma hatası:", error);
    showError("Akış yüklenemedi", error);
  }
}

/**
 * Giriş yapılmamışsa mesaj göster
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

// === LOAD FEED ===
async function loadFeed() {
  try {
    feedContainer.innerHTML = '<div class="loading">📡 Akış yükleniyor...</div>';

    const currentUser = sessionManager.getCurrentUser();
    if (!currentUser) {
      showAuthMessage();
      return;
    }

    // Aktif kullanıcı ID'sini kullanarak istek gönder
    const userId = currentUser.id;
    const res = await fetch(`${API_URL}/feed/?user_id=${userId}`, {
      headers: {
        "Authorization": `Bearer ${sessionManager.getToken()}`
      }
    });
    
    if (!res.ok) {
      const errorData = await res.text();
      throw new Error(`HTTP ${res.status}: ${errorData}`);
    }

    const activities = await res.json();
    console.log(`✅ ${activities.length} aktivite yüklendi`);

    if (!activities || activities.length === 0) {
      feedContainer.innerHTML = '<div class="empty-state">📭 Henüz aktivite yok. Kullanıcıları takip etmeye başlayın!</div>';
      return;
    }

    // Render all activities
    feedContainer.innerHTML = activities
      .map(activity => renderActivityCard(activity))
      .join("");
    
    // Bind event listeners after rendering new content
    bindActivityEvents();

  } catch (error) {
    console.error("Akış yükleme hatası:", error);
    showError("Akış yüklenemedi", error);
  }
}

// === RENDER ACTIVITY CARD ===
function renderActivityCard(activity) {
  const actionText = activityDescriptions[activity.activity_type] || "bir işlem yaptı";
  const timestamp = formatRelativeTime(activity.created_at);
  const username = activity.username || `Kullanıcı #${activity.user_id}`;
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

// === ACTIVITY INTERACTIONS ===
// Bind event listeners with proper event delegation on feedContainer
// Track if listener already added to prevent duplicates
let eventListenerBound = false;

function bindActivityEvents() {
  // Only bind once - prevent duplicate listeners
  if (eventListenerBound) return;
  
  feedContainer.addEventListener('click', (e) => {
    console.log('🖱️ Click detected on feedContainer', { target: e.target, className: e.target.className });
    
    // Check if clicked element is or is inside a button
    const btn = e.target.closest('.btn');
    if (!btn) {
      console.log('ℹ️ Click was not on a button, ignoring');
      return;
    }
    
    console.log('✅ Button detected:', { classes: btn.className });
    
    // Get the activity card and ID
    const card = btn.closest('.activity-card');
    if (!card) {
      console.error('❌ Activity card not found!');
      return;
    }
    
    e.preventDefault();
    const activityId = card.getAttribute('data-activity-id');
    console.log('🎯 Activity ID:', activityId);
    
    // Route to appropriate handler based on button class
    if (btn.classList.contains('btn-like')) {
      console.log('→ Handling like');
      handleLike(btn, activityId);
    } else if (btn.classList.contains('btn-comment')) {
      console.log('→ Handling comment');
      handleComment(btn, activityId);
    } else if (btn.classList.contains('btn-share')) {
      console.log('→ Handling share');
      handleShare(card);
    }
  });
  
  eventListenerBound = true;
  console.log('✅ Event listener bound to feedContainer');
}

function handleLike(btn, activityId) {
  btn.classList.toggle('liked');
  const icon = btn.querySelector('.like-icon');
  const count = btn.querySelector('.like-count');
  
  if (btn.classList.contains('liked')) {
    icon.textContent = '❤️';
    count.textContent = parseInt(count.textContent) + 1;
  } else {
    icon.textContent = '🤍';
    count.textContent = Math.max(0, parseInt(count.textContent) - 1);
  }
  
  console.log(`👍 Activity ${activityId} liked`);
}

function handleComment(btn, activityId) {
  console.log('🔍 Comment button clicked!', { btn, activityId });
  
  const commentText = prompt('💬 Yorum yazınız:\n(Sadece test amaçlı, kaydedilmez)');
  console.log('📝 Prompt result:', commentText);
  
  if (commentText && commentText.trim()) {
    const count = btn.querySelector('.comment-count');
    if (!count) {
      console.error('❌ Comment count element not found!');
      return;
    }
    
    const oldCount = parseInt(count.textContent);
    count.textContent = oldCount + 1;
    console.log(`💬 Comment added to activity ${activityId}: ${commentText}`);
    console.log(`   Count updated: ${oldCount} → ${oldCount + 1}`);
    
    alert('✅ Yorum başarıyla eklendi!');
    btn.style.color = '#667eea';
    btn.querySelector('.comment-icon').textContent = '💙';
  } else {
    console.log('⚠️ Comment cancelled or empty');
  }
}

function handleShare(card) {
  const username = card.querySelector('.activity-header strong').textContent;
  const action = card.querySelector('.activity-action').textContent;
  const title = card.querySelector('.activity-item-title').textContent;
  
  const shareText = `${username} ${action}\n${title}`;
  
  if (navigator.share) {
    navigator.share({
      title: 'BiblioNet Activity',
      text: shareText
    }).catch(err => console.log('Share failed:', err));
  } else {
    // Fallback: copy to clipboard
    navigator.clipboard.writeText(shareText).then(() => {
      alert('✅ Aktivite panoya kopyalandı!');
    }).catch(() => {
      alert('📋 ' + shareText);
    });
  }
  
  console.log('📤 Activity shared:', shareText);
}

// === UTILITY FUNCTIONS ===
function formatRelativeTime(dateString) {
  if (!dateString) return "—";
  
  try {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    // Less than a minute
    if (seconds < 60) {
      return "biraz önce";
    }
    
    // Minutes
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) {
      return `${minutes} dakika önce`;
    }
    
    // Hours
    const hours = Math.floor(minutes / 60);
    if (hours < 24) {
      return `${hours} saat önce`;
    }
    
    // Days
    const days = Math.floor(hours / 24);
    if (days < 7) {
      return `${days} gün önce`;
    }
    
    // Weeks
    const weeks = Math.floor(days / 7);
    if (weeks < 4) {
      return `${weeks} hafta önce`;
    }
    
    // Months
    const months = Math.floor(days / 30);
    if (months < 12) {
      return `${months} ay önce`;
    }
    
    // Years
    const years = Math.floor(months / 12);
    return `${years} yıl önce`;
  } catch (e) {
    console.warn("Date format error:", e);
    return dateString;
  }
}

function showError(message, error) {
  console.error(message, error);
  feedContainer.innerHTML = `
    <div class="error-message">
      <h3>❌ ${message}</h3>
      <p>${error?.message || 'Bilinmeyen hata'}</p>
      <small>Konsolu kontrol edin (F12) → Console sekmesi</small>
    </div>
  `;
}

// === AUTO-REFRESH (Optional) ===
// Uncomment to auto-refresh feed every 30 seconds
/*
setInterval(async () => {
  console.log("🔄 Auto-refreshing feed...");
  await loadFeed();
}, 30000);
*/
