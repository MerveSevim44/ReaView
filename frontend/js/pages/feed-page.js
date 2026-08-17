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
import { API_BASE_URL } from "../core/env.js";

/**
 * HTTP URL'lerini HTTPS'e dönüştür (Mixed Content önleme)
 */
function ensureHttps(url) {
  if (!url || typeof url !== 'string') return url;
  return url.replace(/^http:\/\//i, 'https://');
}

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
    console.log(sessionManager.isLoggedIn() ? "✅ Kullanıcı giriş yaptı, akış yükleniyor..." : "👋 Misafir akışı yükleniyor...");
    await loadFeed();

    // "Daha Fazla Yükle" butonuna listener ekle
    loadMoreBtn.addEventListener("click", loadMoreActivities);

    // Sonsuz kaydırma listener'ı ekle
    window.addEventListener("scroll", handleInfiniteScroll);
  } catch (error) {
    console.error("Feed başlatma hatası:", error);
    feedContainer.innerHTML = `<div class="empty-state"><p>❌ Akış yüklenemedi: ${error.message}</p></div>`;
  }
}

/**
 * Sonsuz kaydırma - sayfanın sonuna gelinceyi yeni aktiviteler yükle
 */
function handleInfiniteScroll() {
  if (isLoading || !hasMore) return;

  // Sayfa sonuna 300px kala yükleyi başlat
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 300) {
    loadMoreActivities();
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

function promptLogin(message) {
  alert(`❌ ${message}`);
}

/**
 * İlk sayfadaki aktiviteleri yükle
 */
async function loadFeed() {
  try {
    feedContainer.innerHTML = '<div class="loading">📡 Akış yükleniyor...</div>';

    // İlk sayfayı getir (skip=0, limit=15). This endpoint is public.
    // user_id artık token'dan otomatik alınıyor
    const activities = await getFeed(0, pageSize);
    
    if (!activities || activities.length === 0) {
      feedContainer.innerHTML = '<div class="empty-state"><p>📭 Henüz aktivite yok. Kullanıcıları takip etmeye başlayın!</p></div>';
      loadMoreContainer.style.display = "none";
      return;
    }

    console.log(`✅ ${activities.length} aktivite yüklendi`);
    console.log("📊 Aktivite örneği (poster_url kontrolü):", activities[0]);

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

    currentPage++;
    const skip = currentPage * pageSize;

    // Sonraki sayfayı getir
    // user_id artık token'dan otomatik alınıyor
    const activities = await getFeed(skip, pageSize);

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
           item_id, title, item_type, poster_url, year, review_text, rating_score, review_rating,
           review_id, like_count = 0, comment_count = 0, is_liked_by_user = 0, is_item_liked_by_user = 0,
           review_owner_username = '', referenced_review_text = '', source_id = '' } = activity;

  const timestamp = formatRelativeTime(created_at);
  const displayName = username || `Kullanıcı #${user_id}`;
  const profileLink = `./profile.html?user=${user_id}`;
  
  // Title'ı güvenli hale getir - empty ise fallback göster
  const displayTitle = title && title.trim() !== '' ? title : 'İçerik';

  // Debug: Check if poster_url is missing (poster gerektiren türlerde)
  const posterRequiredTypes = ['rating', 'review', 'like_review', 'like_item'];
  if (posterRequiredTypes.includes(activity_type) && (!poster_url || poster_url.trim() === '')) {
    console.warn(`⚠️ POSTER EXSİK: "${displayTitle}" (activity_id: ${activity_id}, item_id: ${item_id}, type: ${activity_type})`);
  }

  // HTTP → HTTPS dönüşümü (Mixed Content önleme)
  const safePosterUrl = ensureHttps(poster_url);

  // Aksiyon metni
  let actionText = "";
  if (activity_type === "rating") {
    actionText = `<em>${displayTitle}</em> hakkında puan verdi`;
  } else if (activity_type === "review") {
    actionText = `<em>${displayTitle}</em> hakkında yorum yaptı`;
  } else if (activity_type === "like_review") {
    actionText = `<em>${displayTitle}</em> hakkında yapılan yorumu beğendi`;
  } else if (activity_type === "like_item") {
    actionText = `<em>${displayTitle}</em>'ı beğendi`;
  } else if (activity_type === "follow") {
    actionText = "birini takip etmeye başladı";
  } else if (activity_type === "comment_review") {
    const reviewOwner = review_owner_username ? `<strong>${review_owner_username}</strong>` : "birisinin";
    actionText = `${reviewOwner}'nin <em>${displayTitle}</em> hakkındaki yorumuna yorum yaptı`;
  } else if (activity_type === "list_add") {
    actionText = "bir liste oluşturdu";
  } else {
    actionText = "bir aktivite yaptı";
  }

  // Body bölümünü aktivite türüne göre render et
  let bodyHtml = "";
  if (activity_type === "rating" && item_id) {
    // Rating aktivitesi - rating_score kullan
    bodyHtml = renderRatingBody(displayTitle, item_type, safePosterUrl, year, rating_score, item_id);
  } else if (activity_type === "review" && item_id) {
    // Review aktivitesi - review_text ve review_rating'i birlikte göster
    bodyHtml = renderReviewBody(displayTitle, item_type, safePosterUrl, review_text, review_rating, review_id, item_id);
  } else if (activity_type === "like_review") {
    // Review beğenisi
    bodyHtml = renderReviewBody(displayTitle, item_type, safePosterUrl, review_text, review_rating, activity.review_id, item_id);
  } else if (activity_type === "like_item" && item_id) {
    // Item beğenisi
    bodyHtml = renderRatingBody(displayTitle, item_type, safePosterUrl, year, 0, item_id);
  } else if (activity_type === "comment_review") {
    // Yoruma yapılan yorum - referenced review'u göster
    bodyHtml = renderCommentReviewBody(referenced_review_text, review_owner_username, displayTitle);
  } else {
    bodyHtml = renderGenericBody(displayTitle || "Aktivite");
  }

  // Kart HTML'i
  return `
    <div class="card activity-card" data-activity-id="${activity_id}" data-activity-type="${activity_type}" data-item-id="${item_id}" data-review-id="${review_id || ''}" data-type="${item_type || ''}">
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
        ${(() => {
          // Beğeni state'ini belirle
          let isLiked = false;
          if (activity_type === "review" || activity_type === "like_review") {
            isLiked = is_liked_by_user === 1;
          } else if (activity_type === "rating" || activity_type === "like_item") {
            isLiked = is_item_liked_by_user === 1;
          }
          const likeIcon = isLiked ? "❤️" : "🤍";
          const activeClass = isLiked ? "active" : "";
          return `
            <button class="btn-action btn-like ${activeClass}" title="Beğen" data-review-id="${review_id || ''}" data-item-id="${item_id || ''}">
              <span class="like-icon">${likeIcon}</span>
              <span class="like-count" style="cursor: pointer;" title="Beğenenleri görmek için tıkla">${like_count}</span>
            </button>
          `;
        })()}
        <button class="btn-action btn-comment" title="Yorum Yap" ${!review_id ? 'disabled' : ''}>
          <span class="comment-icon">💬</span>
          <span class="comment-count">${comment_count}</span>
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
function renderRatingBody(title, itemType, posterUrl, year, ratingScore, itemId) {
  // Yıldız gösterimi (1-10 puanı 5 yıldıza çevir)
  const stars = Math.round((ratingScore / 10) * 5);
  let starDisplay = "★".repeat(stars) + "☆".repeat(5 - stars);

  // Placeholder poster - Check if posterUrl is valid (not empty string, null, or falsy)
  const displayPoster = (posterUrl && posterUrl.trim() !== '') ? posterUrl : `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='120'%3E%3Crect fill='%23f0f0f0' width='80' height='120'/%3E%3Ctext x='50%' y='50%' font-size='12' fill='%23999' text-anchor='middle' dominant-baseline='middle'%3E${itemType === 'movie' ? '🎬' : '📚'}%3C/text%3E%3C/svg%3E`;

  return `
    <div class="activity-body rating-type" data-item-id="${itemId}">
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
 * Gösterim: Poster + Excerpt (ilk 150-200 char) + Rating varsa yıldız + "daha fazlasını oku" linki
 */
function renderReviewBody(title, itemType, posterUrl, reviewText, reviewRating, reviewId, itemId) {
  // Review metni truncate et (150 karakter)
  const maxExcerptLength = 150;
  const excerpt = reviewText && reviewText.length > maxExcerptLength 
    ? reviewText.substring(0, maxExcerptLength).trim() + "..."
    : reviewText;

  // Placeholder poster - Check if posterUrl is valid (not empty string, null, or falsy)
  const displayPoster = (posterUrl && posterUrl.trim() !== '') ? posterUrl : `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='70' height='105'%3E%3Crect fill='%23f0f0f0' width='70' height='105'/%3E%3Ctext x='50%' y='50%' font-size='10' fill='%23999' text-anchor='middle' dominant-baseline='middle'%3E${itemType === 'movie' ? '🎬' : '📚'}%3C/text%3E%3C/svg%3E`;

  // Rating varsa yıldız göster
  let ratingHtml = "";
  if (reviewRating && reviewRating > 0) {
    const stars = Math.round((reviewRating / 10) * 5);
    const starDisplay = "★".repeat(stars) + "☆".repeat(5 - stars);
    ratingHtml = `<div style="font-size: 14px; color: #ffc107; margin: 4px 0;">${starDisplay} <span style="color: #666; font-size: 12px;">${reviewRating}/10</span></div>`;
  }

  // Detay sayfasına link oluştur
  const detailLink = itemId ? `./items.html?id=${itemId}` : "#";

  return `
    <div class="activity-body review-type" data-review-id="${reviewId}">
      <div class="review-poster">
        <img src="${displayPoster}" alt="${title}" />
      </div>
      <div class="review-content">
        <h4>${title || "Bilinmeyen Başlık"}</h4>
        ${ratingHtml}
        <p class="review-excerpt">"${excerpt}"</p>
        <a href="${detailLink}" class="review-read-more">...daha fazlasını oku</a>
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
 * Yoruma yapılan yorum aktivitesi body'si
 * Gösterim: Kimin yorumuna yorum yaptığını ve o yorumun özünü göster
 */
function renderCommentReviewBody(referencedReviewText, reviewOwnerUsername, itemTitle) {
  // Yorumu kısalt (ilk 200 karakter)
  const truncatedText = referencedReviewText && referencedReviewText.length > 200 
    ? referencedReviewText.substring(0, 200) + '...' 
    : referencedReviewText || 'Yorum metni bulunamadı';
    
  return `
    <div class="activity-body activity-comment-body" style="padding: 16px;">
      <div style="background: #f8f9fa; padding: 12px; border-left: 3px solid #667eea; border-radius: 6px; margin-bottom: 12px;">
        <div style="font-size: 12px; color: #999; margin-bottom: 6px;">
          💬 <strong>${reviewOwnerUsername || 'Birisinin'}</strong> yorumu:
        </div>
        <div style="font-size: 14px; color: #555; line-height: 1.5; word-break: break-word;">
          "${truncatedText}"
        </div>
      </div>
      <div style="font-size: 12px; color: #999;">
        📚 <em>${itemTitle}</em> hakkında
      </div>
    </div>
  `;
}

/**
 * Event listener'ları bağla (beğen, yorum, paylaş)
 */
function bindActivityEvents() {
  const currentUser = sessionManager.getCurrentUser();

  // Beğen butonları
  feedContainer.querySelectorAll(".btn-like").forEach(btn => {
    if (!btn.dataset.listenerAttached) {
      btn.addEventListener("click", handleLike);
      
      // Like count'a tıklanırsa beğenenleri göster
      const likeCount = btn.querySelector(".like-count");
      likeCount.addEventListener("click", (e) => {
        e.stopPropagation();
        const card = btn.closest(".activity-card");
        const reviewId = btn.getAttribute("data-review-id");
        const itemId = btn.getAttribute("data-item-id");
        showLikesModal(card, reviewId || null, itemId || null);
      });
      
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

  // Yorumları ve beğenileri otomatik yükle (refresh'de görmek için)
  feedContainer.querySelectorAll(".activity-card").forEach(card => {
    if (!card.dataset.dataLoaded) {
      const activityId = card.getAttribute("data-activity-id");
      const activityType = card.getAttribute("data-activity-type");
      const reviewId = card.getAttribute("data-review-id");
      
      if (currentUser) {
        // Review'lar için yorumları yükle
        if (activityType === "review" && reviewId) {
          displayComments(card, reviewId, currentUser.id);
        }
      }
      
      card.dataset.dataLoaded = "true";
    }
  });
}

/**
 * Like count'u API'den getir ve güncelle
 */
async function updateLikeCount(card, id, type) {
  try {
    let endpoint = "";
    if (type === "review") {
      endpoint = `/likes/review/${id}/likes`;
    } else if (type === "rating") {
      endpoint = `/likes/item/${id}/likes`;
    }

    if (!endpoint) return;

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Authorization": `Bearer ${sessionManager.getToken()}`
      }
    });

    if (!response.ok) return;

    const data = await response.json();
    
    // Count'u bul - API response formatını handle et
    let likeCount = 0;
    if (typeof data === 'object') {
      if (data.total_likes !== undefined) {
        likeCount = data.total_likes; // Backend döndürdüğü format
      } else if (data.count !== undefined) {
        likeCount = data.count;
      } else if (Array.isArray(data)) {
        likeCount = data.length;
      } else if (data.likes && Array.isArray(data.likes)) {
        likeCount = data.likes.length;
      }
    }

    // UI'da count'u güncelle
    const likeBtn = card.querySelector(".btn-like");
    if (likeBtn) {
      const likeCountEl = likeBtn.querySelector(".like-count");
      likeCountEl.textContent = likeCount;
    }
    
    console.log(`✅ Like count güncellendi: ${likeCount}`);
  } catch (error) {
    console.error("Like count güncelleme hatası:", error);
  }
}

/**
 * Beğen butonu tıklandı
 */
async function handleLike(e) {
  e.preventDefault();
  const btn = e.target.closest(".btn-like");
  const card = btn.closest(".activity-card");
  const activityId = card.getAttribute("data-activity-id");
  const activityType = card.getAttribute("data-activity-type");
  const itemId = card.getAttribute("data-item-id");
  const likeIcon = btn.querySelector(".like-icon");
  const likeCount = btn.querySelector(".like-count");
  const currentUser = sessionManager.getCurrentUser();

  if (!currentUser) {
    promptLogin("Beğenmek için giriş yapmalısınız");
    return;
  }

  try {
    let endpoint = "";
    const reviewId = card.getAttribute("data-review-id");

    if (activityType === "review" || activityType === "like_review") {
      // Review beğenisi - review_id kullan
      const targetReviewId = reviewId || activityId;
      if (!targetReviewId) {
        console.warn("Review ID bulunamadı");
        return;
      }
      endpoint = `/likes/review/${targetReviewId}/like`;
    } else if (activityType === "rating" || activityType === "like_item") {
      // Rating/Item beğenmesi (item like olarak)
      if (!itemId) {
        console.warn("Item ID bulunamadı");
        return;
      }
      endpoint = `/likes/item/${itemId}/like`;
    } else if (activityType === "comment_review") {
      // Yorum aktivitesi - review beğenisi olarak işle
      const targetReviewId = reviewId || activityId;
      if (!targetReviewId) {
        console.warn("Review ID bulunamadı (comment_review)");
        return;
      }
      endpoint = `/likes/review/${targetReviewId}/like`;
    }

    if (!endpoint) {
      console.warn("Endpoint belirlenemedi - desteklenmeyen aktivite türü:", activityType);
      return;
    }

    // API'ye beğeni isteğini gönder
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${sessionManager.getToken()}`
      },
      body: JSON.stringify({ user_id: currentUser.id })
    });

    if (!response.ok) {
      throw new Error(`API Hatası: ${response.statusText}`);
    }

    const result = await response.json();

    // UI güncelle
    if (result.action === "liked") {
      likeIcon.textContent = "❤️";
      btn.classList.add("active");
    } else if (result.action === "unliked") {
      likeIcon.textContent = "🤍";
      btn.classList.remove("active");
    }

    // Güncel like count'ı getir
    let getLikesEndpoint = "";
    if (activityType === "review" || activityType === "like_review") {
      getLikesEndpoint = `/likes/review/${activityId}/likes`;
    } else if (activityType === "rating" || activityType === "like_item") {
      getLikesEndpoint = `/likes/item/${itemId}/likes`;
    }

    if (getLikesEndpoint) {
      try {
        const likesResponse = await fetch(`${API_BASE_URL}${getLikesEndpoint}`, {
          headers: {
            "Authorization": `Bearer ${sessionManager.getToken()}`
          }
        });
        
        if (likesResponse.ok) {
          const likesData = await likesResponse.json();
          let newLikeCount = 0;
          
          if (typeof likesData === 'object') {
            if (likesData.total_likes !== undefined) {
              newLikeCount = likesData.total_likes;
            } else if (likesData.count !== undefined) {
              newLikeCount = likesData.count;
            } else if (Array.isArray(likesData)) {
              newLikeCount = likesData.length;
            } else if (likesData.likes && Array.isArray(likesData.likes)) {
              newLikeCount = likesData.likes.length;
            }
          }
          
          likeCount.textContent = newLikeCount;
        }
      } catch (err) {
        console.warn("Like count güncelleme hatası:", err);
      }
    }

    console.log(`✅ Beğeni işlemi: ${result.action}`);
  } catch (error) {
    console.error("❌ Beğeni hatası:", error);
    alert(`❌ Beğeni işlemi başarısız: ${error.message}`);
  }
}

/**
 * Yorum butonu tıklandı
 */
async function handleComment(e) {
  e.preventDefault();
  const currentUser = sessionManager.getCurrentUser();

  if (!currentUser) {
    promptLogin("Yorum yapmak için giriş yapmalısınız");
    return;
  }

  const commentText = prompt("💬 Yorum yazınız:");

  if (!commentText || !commentText.trim()) {
    return;
  }

  const btn = e.target.closest(".btn-comment");
  const card = btn.closest(".activity-card");
  const activityId = card.getAttribute("data-activity-id");
  const activityType = card.getAttribute("data-activity-type");
  const commentCount = btn.querySelector(".comment-count");
  const commentIcon = btn.querySelector(".comment-icon");
  try {
    let endpoint = "";
    let reviewId = card.getAttribute("data-review-id");
    
    if (activityType === "review" && reviewId) {
      endpoint = `/likes/review/${reviewId}/comments`;
    } else if (activityType === "like_review" && reviewId) {
      endpoint = `/likes/review/${reviewId}/comments`;
    } else {
      console.warn("Bu aktivite türü yoruma desteklenmiyor veya review_id bulunamadı");
      return;
    }

    // API'ye yorum isteğini gönder
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${sessionManager.getToken()}`
      },
      body: JSON.stringify({
        user_id: currentUser.id,
        comment_text: commentText.trim()
      })
    });

    if (!response.ok) {
      throw new Error(`API Hatası: ${response.statusText}`);
    }

    const result = await response.json();

    // UI güncelle
    commentCount.textContent = parseInt(commentCount.textContent) + 1;
    commentIcon.textContent = "💙";
    btn.classList.add("active");

    // Yorumları getir ve göster
    await displayComments(card, reviewId, currentUser.id);

    console.log(`✅ Yorum eklendi: ${result.comment_id}`);
  } catch (error) {
    console.error("❌ Yorum hatası:", error);
    alert(`❌ Yorum ekleme başarısız: ${error.message}`);
  }
}

/**
 * Aktivite kartında yorumları göster
 */
async function displayComments(card, reviewId, currentUserId) {
  try {
    // Mevcut yorumlar bölümünü kaldır
    const existingCommentsSection = card.querySelector(".comments-section");
    if (existingCommentsSection) {
      existingCommentsSection.remove();
    }

    // API'den yorumları getir
    const response = await fetch(`${API_BASE_URL}/likes/review/${reviewId}/comments`, {
      headers: {
        "Authorization": `Bearer ${sessionManager.getToken()}`
      }
    });

    if (!response.ok) throw new Error("Yorumlar yüklenemedi");

    const data = await response.json();
    const comments = data.comments || data; // Backend dönem formatını handle et

    // Comment count'u güncelle
    const commentBtn = card.querySelector(".btn-comment");
    if (commentBtn) {
      const commentCount = commentBtn.querySelector(".comment-count");
      commentCount.textContent = comments.length;
    }

    if (!comments || comments.length === 0) {
      return;
    }

    // Yorumları HTML olarak render et
    const commentsHtml = comments.map(comment => `
      <div class="comment-item" data-comment-id="${comment.comment_id}">
        <div class="comment-header">
          <div class="comment-user-info">
            ${comment.avatar_url ? `<img src="${comment.avatar_url}" alt="${comment.username}" class="comment-avatar">` : `<span class="comment-avatar-placeholder">👤</span>`}
            <div class="comment-user-details">
              <strong class="comment-username">${comment.username}</strong>
              <small class="comment-time">${formatRelativeTime(comment.created_at)}</small>
            </div>
          </div>
          ${comment.user_id === currentUserId ? `
            <button class="btn-delete-comment" onclick="deleteComment(${comment.comment_id}, ${reviewId})" title="Sil">🗑️</button>
          ` : ""}
        </div>
        <p class="comment-text">${comment.comment_text}</p>
      </div>
    `).join("");

    // Yorumlar bölümünü footer'ın üstüne ekle
    const footer = card.querySelector(".activity-footer");
    const commentsSection = document.createElement("div");
    commentsSection.className = "comments-section";
    commentsSection.innerHTML = `
      <div class="comments-header">💬 Yorumlar (${comments.length})</div>
      <div class="comments-list">
        ${commentsHtml}
      </div>
    `;
    footer.parentNode.insertBefore(commentsSection, footer);
  } catch (error) {
    console.error("Yorumları gösterme hatası:", error);
  }
}

/**
 * Yorum sil
 */
window.deleteComment = async function(commentId, reviewId) {
  if (!confirm("Yorum silinsin mi?")) return;

  const currentUser = sessionManager.getCurrentUser();

  try {
    const response = await fetch(`${API_BASE_URL}/likes/review-comments/${commentId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${sessionManager.getToken()}`
      },
      body: JSON.stringify({ user_id: currentUser.id })
    });

    if (!response.ok) {
      throw new Error(`API Hatası: ${response.statusText}`);
    }

    // Yorum öğesini DOM'dan kaldır
    const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
    if (commentElement) {
      commentElement.remove();
    }

    console.log("✅ Yorum silindi");
  } catch (error) {
    console.error("❌ Yorum silme hatası:", error);
    alert(`❌ Yorum silinme başarısız: ${error.message}`);
  }
};

/**
 * Paylaş butonu tıklandı
 */
function handleShare(e) {
  e.preventDefault();
  if (!sessionManager.isLoggedIn()) {
    promptLogin("Paylaşmak için giriş yapmalısınız");
    return;
  }

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

/**
 * Beğenenleri modal'da göster
 */
async function showLikesModal(cardElement, reviewId = null, itemId = null) {
  const modal = document.getElementById("likes-modal");
  const modalBody = document.getElementById("likes-modal-body");
  
  if (!reviewId && !itemId) {
    modalBody.innerHTML = '<p style="text-align: center; color: #999;">Beğeni bulunamadı</p>';
    modal.style.display = "flex";
    return;
  }

  try {
    modalBody.innerHTML = '<p style="text-align: center; color: #999;">Yükleniyor...</p>';
    modal.style.display = "flex";

    let endpoint = "";
    if (reviewId) {
      endpoint = `/likes/review/${reviewId}/likes`;
    } else if (itemId) {
      endpoint = `/likes/item/${itemId}/likes`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Authorization": `Bearer ${sessionManager.getToken()}`
      }
    });

    if (!response.ok) throw new Error("Beğenenler yüklenemedi");

    const data = await response.json();
    let likes = [];
    
    // API response formatını handle et
    if (Array.isArray(data)) {
      likes = data;
    } else if (data.likes && Array.isArray(data.likes)) {
      likes = data.likes;
    }

    if (likes.length === 0) {
      modalBody.innerHTML = '<p style="text-align: center; color: #999;">Henüz kimse beğenmedi</p>';
      return;
    }

    // Beğenenler listesini render et
    const likesHtml = likes.map(like => `
      <div class="like-item">
        <div class="like-item-avatar">
          ${like.avatar_url ? `<img src="${like.avatar_url}" alt="${like.username}">` : '👤'}
        </div>
        <div class="like-item-info">
          <a href="./profile.html?user=${like.user_id}" class="like-item-username">${like.username || `Kullanıcı #${like.user_id}`}</a>
        </div>
      </div>
    `).join("");

    modalBody.innerHTML = `<div class="likes-list">${likesHtml}</div>`;
  } catch (error) {
    console.error("Beğenenler yükleme hatası:", error);
    modalBody.innerHTML = `<p style="text-align: center; color: #999;">Hata: ${error.message}</p>`;
  }
}
