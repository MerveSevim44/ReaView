/**
 * Feed Page Module - Sosyal Akış
 * 
 * İsterleri:
 * 1. Aktivite Kartı: Header (avatar, kullanıcı, aksiyon, tarih), Body (içerik), Footer (beğen/yorum)
 * 2. Aktivite Türleri: Rating (yıldız gösterimi), Review (excerpt + "daha fazla" linki)
 * 3. Sayfalandırma: İlk 15 aktivite, sonra "Daha Fazla Yükle" butonu
 */

import {
  getFeed
} from "../core/api-client.js";
import { sessionManager } from "../core/session-manager.js";
import { formatRelativeTime } from "../utils/formatters.js";

// DOM References
const feedContainer = document.getElementById("feed-container");
const loadMoreContainer = document.getElementById("load-more-container");
const loadMoreBtn = document.getElementById("load-more-btn");

// Sayfalandırma durumu
let currentPage = 0;
const pageSize = 15;
let isLoading = false;
let hasMore = true;

/**
 * Başlat
 */
window.addEventListener("DOMContentLoaded", async () => {
  await initializeFeed();
});

/**
 * Feed sayfasını başlat
 */
async function initializeFeed() {
  try {
    if (!sessionManager.isLoggedIn()) {
      showAuthMessage();
      return;
    }

    console.log("✅ Kullanıcı giriş yaptı, akış yükleniyor...");
    await loadFeed();

    // "Daha Fazla Yükle" butonuna listener ekle
    loadMoreBtn.addEventListener("click", loadMoreActivities);
  } catch (error) {
    console.error("Feed başlatma hatası:", error);
    feedContainer.innerHTML = `<div class="empty-state"><p>❌ Akış yüklenemedi: ${error.message}</p></div>`;
  }
}

/**
 * Giriş mesajı göster
 */
function showAuthMessage() {
  feedContainer.innerHTML = `
    <div class="auth-message">
      <h3>👋 Hoş geldiniz!</h3>
      <p>Akışı görmek için lütfen giriş yapınız.</p>
      <a href="./login.html">Giriş Yap</a>
    </div>
  `;
}

/**
 * İlk sayfadaki aktiviteleri yükle
 */
async function loadFeed() {
  try {
    feedContainer.innerHTML = '<div class="loading">📡 Akış yükleniyor...</div>';

    const currentUser = sessionManager.getCurrentUser();
    if (!currentUser) {
      showAuthMessage();
      return;
    }

    // İlk sayfayı getir (skip=0, limit=15)
    const activities = await getFeed(currentUser.id, 0, pageSize);
    
    if (!activities || activities.length === 0) {
      feedContainer.innerHTML = '<div class="empty-state"><p>📭 Henüz aktivite yok. Kullanıcıları takip etmeye başlayın!</p></div>';
      loadMoreContainer.style.display = "none";
      return;
    }

    console.log(`✅ ${activities.length} aktivite yüklendi`);

    // Aktiviteleri render et
    const html = activities.map(activity => renderActivityCard(activity)).join("");
    feedContainer.innerHTML = html;

    // Sayfalandırma durumunu güncelle
    currentPage = 0;
    hasMore = activities.length === pageSize;
    
    // "Daha Fazla Yükle" butonunu göster/gizle
    loadMoreContainer.style.display = hasMore ? "block" : "none";

    // Event listener'ları bağla
    bindActivityEvents();
  } catch (error) {
    console.error("Akış yükleme hatası:", error);
    feedContainer.innerHTML = `<div class="empty-state"><p>❌ Hata: ${error.message}</p></div>`;
  }
}

/**
 * Daha fazla aktivite yükle (sayfalandırma)
 */
async function loadMoreActivities() {
  if (isLoading || !hasMore) return;

  try {
    isLoading = true;
    loadMoreBtn.disabled = true;
    loadMoreBtn.textContent = "Yükleniyor...";

    const currentUser = sessionManager.getCurrentUser();
    currentPage++;
    const skip = currentPage * pageSize;

    // Sonraki sayfayı getir
    const activities = await getFeed(currentUser.id, skip, pageSize);

    if (!activities || activities.length === 0) {
      hasMore = false;
      loadMoreContainer.style.display = "none";
      console.log("✅ Tüm aktiviteler yüklendi");
      return;
    }

    console.log(`✅ ${activities.length} daha aktivite yüklendi`);

    // Yeni aktiviteleri ekle
    const html = activities.map(activity => renderActivityCard(activity)).join("");
    feedContainer.insertAdjacentHTML("beforeend", html);

    // Event listener'ları yeni kartlara bağla
    bindActivityEvents();

    // Daha fazla var mı kontrol et
    hasMore = activities.length === pageSize;
    loadMoreContainer.style.display = hasMore ? "block" : "none";
  } catch (error) {
    console.error("Daha fazla aktivite yükleme hatası:", error);
  } finally {
    isLoading = false;
    loadMoreBtn.disabled = false;
    loadMoreBtn.textContent = "Daha Fazla Yükle";
  }
}

/**
 * Aktivite kartını render et
 * 
 * Kart yapısı:
 * - Header: Avatar + Kullanıcı + Aksiyon + Tarih
 * - Body: Rating (poster + yıldız) veya Review (poster + excerpt)
 * - Footer: Beğen, Yorum, Paylaş butonları
 */
function renderActivityCard(activity) {
  const { activity_id, activity_type, created_at, user_id, username, avatar_url, 
           item_id, title, item_type, poster_url, year, review_text, rating_score } = activity;

  const timestamp = formatRelativeTime(created_at);
  const displayName = username || `Kullanıcı #${user_id}`;
  const profileLink = `./profile.html?user=${user_id}`;

  // Aksiyon metni
  let actionText = "";
  if (activity_type === "rating") {
    actionText = "bir içeriğe puan verdi";
  } else if (activity_type === "review") {
    actionText = "bir yorum yaptı";
  } else {
    actionText = "bir aktivite yaptı";
  }

  // Body bölümünü aktivite türüne göre render et
  let bodyHtml = "";
  if (activity_type === "rating" && item_id) {
    bodyHtml = renderRatingBody(title, item_type, poster_url, year, rating_score);
  } else if (activity_type === "review" && item_id) {
    bodyHtml = renderReviewBody(title, item_type, poster_url, review_text);
  } else {
    bodyHtml = renderGenericBody(title);
  }

  // Kart HTML'i
  return `
    <div class="activity-card" data-activity-id="${activity_id}" data-activity-type="${activity_type}">
      <!-- Header -->
      <div class="activity-header">
        <div class="activity-avatar">
          ${avatar_url ? `<img src="${avatar_url}" alt="${displayName}" />` : `👤`}
        </div>
        <div class="activity-user-info">
          <a href="${profileLink}" class="activity-username">${displayName}</a>
          <div class="activity-action-text">${actionText}</div>
        </div>
        <div class="activity-timestamp">${timestamp}</div>
      </div>

      <!-- Body -->
      ${bodyHtml}

      <!-- Footer -->
      <div class="activity-footer">
        <button class="btn-action btn-like" title="Beğen">
          <span class="like-icon">🤍</span>
          <span class="like-count">0</span>
        </button>
        <button class="btn-action btn-comment" title="Yorum Yap">
          <span class="comment-icon">💬</span>
          <span class="comment-count">0</span>
        </button>
        <button class="btn-action btn-share" title="Paylaş">
          <span class="share-icon">📤</span>
          <span>Paylaş</span>
        </button>
      </div>
    </div>
  `;
}

/**
 * Rating aktivitesi body'si
 * Gösterim: Poster + Yıldız/Puan
 */
function renderRatingBody(title, itemType, posterUrl, year, ratingScore) {
  // Yıldız gösterimi (1-10 puanı 5 yıldıza çevir)
  const stars = Math.round((ratingScore / 10) * 5);
  let starDisplay = "★".repeat(stars) + "☆".repeat(5 - stars);

  // Placeholder poster
  const displayPoster = posterUrl || `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='120'%3E%3Crect fill='%23f0f0f0' width='80' height='120'/%3E%3Ctext x='50%' y='50%' font-size='12' fill='%23999' text-anchor='middle' dominant-baseline='middle'%3E${itemType === 'movie' ? '🎬' : '📚'}%3C/text%3E%3C/svg%3E`;

  return `
    <div class="activity-body rating-type">
      <div class="rating-poster">
        <img src="${displayPoster}" alt="${title}" />
      </div>
      <div class="rating-content">
        <h4>${title || "Bilinmeyen Başlık"}</h4>
        ${year ? `<p style="color: #999; font-size: 13px; margin: 0;">${year}</p>` : ""}
        <div class="rating-score" title="${ratingScore}/10">
          ${starDisplay}<br/>
          <span style="font-size: 16px; color: #666;">${ratingScore}/10</span>
        </div>
      </div>
    </div>
  `;
}

/**
 * Review aktivitesi body'si
 * Gösterim: Poster + Excerpt (ilk 150-200 char) + "daha fazlasını oku" linki
 */
function renderReviewBody(title, itemType, posterUrl, reviewText) {
  // Review metni truncate et (150 karakter)
  const maxExcerptLength = 150;
  const excerpt = reviewText && reviewText.length > maxExcerptLength 
    ? reviewText.substring(0, maxExcerptLength).trim() + "..."
    : reviewText;

  // Placeholder poster
  const displayPoster = posterUrl || `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='70' height='105'%3E%3Crect fill='%23f0f0f0' width='70' height='105'/%3E%3Ctext x='50%' y='50%' font-size='10' fill='%23999' text-anchor='middle' dominant-baseline='middle'%3E${itemType === 'movie' ? '🎬' : '📚'}%3C/text%3E%3C/svg%3E`;

  return `
    <div class="activity-body review-type">
      <div class="review-poster">
        <img src="${displayPoster}" alt="${title}" />
      </div>
      <div class="review-content">
        <h4>${title || "Bilinmeyen Başlık"}</h4>
        <p class="review-excerpt">"${excerpt}"</p>
        <a href="#" class="review-read-more">...daha fazlasını oku</a>
      </div>
    </div>
  `;
}

/**
 * Diğer aktiviteler için generic body
 */
function renderGenericBody(title) {
  return `
    <div class="activity-body" style="padding: 16px;">
      ${title ? `<p><strong>${title}</strong></p>` : '<p style="color: #999;">Aktivite detayı</p>'}
    </div>
  `;
}

/**
 * Event listener'ları bağla (beğen, yorum, paylaş)
 */
function bindActivityEvents() {
  // Beğen butonları
  feedContainer.querySelectorAll(".btn-like").forEach(btn => {
    if (!btn.dataset.listenerAttached) {
      btn.addEventListener("click", handleLike);
      btn.dataset.listenerAttached = "true";
    }
  });

  // Yorum butonları
  feedContainer.querySelectorAll(".btn-comment").forEach(btn => {
    if (!btn.dataset.listenerAttached) {
      btn.addEventListener("click", handleComment);
      btn.dataset.listenerAttached = "true";
    }
  });

  // Paylaş butonları
  feedContainer.querySelectorAll(".btn-share").forEach(btn => {
    if (!btn.dataset.listenerAttached) {
      btn.addEventListener("click", handleShare);
      btn.dataset.listenerAttached = "true";
    }
  });

  // Profil linklerine listener (isteğe bağlı)
  feedContainer.querySelectorAll(".activity-username").forEach(link => {
    if (!link.dataset.listenerAttached) {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        window.location.href = link.href;
      });
      link.dataset.listenerAttached = "true";
    }
  });
}

/**
 * Beğen butonu tıklandı
 */
function handleLike(e) {
  e.preventDefault();
  const btn = e.target.closest(".btn-like");
  const likeIcon = btn.querySelector(".like-icon");
  const likeCount = btn.querySelector(".like-count");

  btn.classList.toggle("active");

  if (btn.classList.contains("active")) {
    likeIcon.textContent = "❤️";
    likeCount.textContent = parseInt(likeCount.textContent) + 1;
  } else {
    likeIcon.textContent = "🤍";
    likeCount.textContent = Math.max(0, parseInt(likeCount.textContent) - 1);
  }
}

/**
 * Yorum butonu tıklandı
 */
function handleComment(e) {
  e.preventDefault();
  const commentText = prompt("💬 Yorum yazınız:");

  if (commentText && commentText.trim()) {
    const btn = e.target.closest(".btn-comment");
    const commentCount = btn.querySelector(".comment-count");
    const commentIcon = btn.querySelector(".comment-icon");

    commentCount.textContent = parseInt(commentCount.textContent) + 1;
    commentIcon.textContent = "💙";
    btn.classList.add("active");
  }
}

/**
 * Paylaş butonu tıklandı
 */
function handleShare(e) {
  e.preventDefault();
  const card = e.target.closest(".activity-card");
  const username = card.querySelector(".activity-username").textContent;
  const title = card.querySelector("h4")?.textContent || "Aktivite";
  const shareText = `${username} - ${title}`;

  if (navigator.share) {
    navigator.share({
      title: "BiblioNet",
      text: shareText
    }).catch(err => console.log("Paylaş hatası:", err));
  } else {
    navigator.clipboard.writeText(shareText).then(() => {
      alert("📋 Aktivite panoya kopyalandı!");
    }).catch(err => console.error("Kopy hatası:", err));
  }
}
