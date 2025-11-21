// frontend/js/api.js
import { sessionManager } from "./session.js";

export const API_URL = "http://127.0.0.1:8000";

/**
 * Header'lara gerekli kimlik bilgilerini ekle
 */
function getHeaders() {
  const headers = { "Content-Type": "application/json" };
  const token = sessionManager.getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Kullanıcı giriş işlemi
 * @param {string} email - E-posta
 * @param {string} password - Şifre
 */
export async function loginUser(email, password) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Giriş başarısız");
  }
  
  return await res.json();
}

/**
 * Kullanıcı kayıt işlemi
 * @param {string} username - Kullanıcı adı
 * @param {string} email - E-posta
 * @param {string} password - Şifre
 */
export async function registerUser(username, email, password) {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password })
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Kayıt başarısız");
  }
  
  return await res.json();
}

/**
 * Tüm içerikleri getir
 */
export async function getItems() {
  const res = await fetch(`${API_URL}/items`, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Sunucu hatası");
  return await res.json();
}

/**
 * Tek içerik detayı
 */
export async function getItemById(id) {
  const res = await fetch(`${API_URL}/items/${id}`, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("İçerik bulunamadı");
  return await res.json();
}

/**
 * Yeni yorum ekle
 */
export async function postReview(data) {
  const res = await fetch(`${API_URL}/reviews`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data)
  });
  return await res.json();
}

/**
 * Bir içeriğe ait yorumları getir
 */
export async function getReviews(itemId) {
  const res = await fetch(`${API_URL}/reviews/item/${itemId}`, {
    headers: getHeaders()
  });
  return await res.json();
}

/**
 * Kullanıcı bilgilerini getir
 */
export async function getUser(userId) {
  const r = await fetch(`${API_URL}/users/${userId}`, {
    headers: getHeaders()
  });
  if (!r.ok) throw new Error("Kullanıcı bulunamadı");
  return r.json();
}

/**
 * Kullanıcı yorumlarını getir
 */
export async function getUserReviews(userId) {
  const r = await fetch(`${API_URL}/users/${userId}/reviews`, {
    headers: getHeaders()
  });
  if (!r.ok) throw new Error("Yorumlar alınamadı");
  return r.json();
}

/**
 * Kullanıcı aktivitelerini getir
 */
export async function getUserActivities(userId) {
  const r = await fetch(`${API_URL}/users/${userId}/activities`, {
    headers: getHeaders()
  });
  if (!r.ok) throw new Error("Aktiviteler alınamadı");
  return r.json();
}

/**
 * Feed'i getir (isteğe bağlı user_id ile takip edilen kişilerin aktiviteleri)
 */
export async function getFeed(userId = null) {
  let url = `${API_URL}/feed`;
  if (userId) {
    url += `?user_id=${userId}`;
  }
  const res = await fetch(url, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Feed alınamadı");
  return await res.json();
}

/**
 * İçerik arama
 */
export async function searchItems(query, itemType = null) {
  let url = `${API_URL}/items/search?q=${encodeURIComponent(query)}`;
  if (itemType) {
    url += `&item_type=${itemType}`;
  }
  const res = await fetch(url, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Arama başarısız");
  return await res.json();
}

/**
 * İçerik ortalama puanını getir
 */
export async function getItemRating(itemId) {
  const res = await fetch(`${API_URL}/items/${itemId}/rating`, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Puan alınamadı");
  return await res.json();
}

/**
 * Harici API'dan arama (TMDB/Google Books)
 */
export async function searchExternal(type, query) {
  const url = `${API_URL}/external/search?type=${type}&query=${encodeURIComponent(query)}`;
  const res = await fetch(url, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Harici arama başarısız");
  return await res.json();
}

/**
 * Harici API'dan veri içe aktar
 */
export async function importItemFromExternal(type, query) {
  const url = `${API_URL}/external/import?type=${type}&query=${encodeURIComponent(query)}`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("İçe aktar başarısız");
  return await res.json();
}

/**
 * Kullanıcıyı takip et
 */
export async function followUser(userId) {
  const currentUser = sessionManager.getCurrentUser();
  if (!currentUser) throw new Error("Giriş yapmalısın");
  
  const res = await fetch(`${API_URL}/follows/${userId}/follow?follower_id=${currentUser.user_id}`, {
    method: "POST",
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Takip işlemi başarısız");
  return await res.json();
}

/**
 * Kullanıcıyı takip etmeyi bırak
 */
export async function unfollowUser(userId) {
  const currentUser = sessionManager.getCurrentUser();
  if (!currentUser) throw new Error("Giriş yapmalısın");
  
  const res = await fetch(`${API_URL}/follows/${userId}/unfollow?follower_id=${currentUser.user_id}`, {
    method: "DELETE",
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Takip etmeyi bırakma işlemi başarısız");
  return await res.json();
}

/**
 * Kullanıcının takip ettiğini kişileri getir
 */
export async function getFollowing(userId) {
  const res = await fetch(`${API_URL}/follows/${userId}/following`, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Takip listesi alınamadı");
  return await res.json();
}

/**
 * Kullanıcının takipçilerini getir
 */
export async function getFollowers(userId) {
  const res = await fetch(`${API_URL}/follows/${userId}/followers`, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Takipçiler alınamadı");
  return await res.json();
}

/**
 * Favorilere ekle
 */
export async function addToFavorite(itemId) {
  const currentUser = sessionManager.getCurrentUser();
  if (!currentUser) throw new Error("Giriş yapmalısın");
  
  const res = await fetch(`${API_URL}/items/${itemId}/favorite?user_id=${currentUser.user_id}`, {
    method: "POST",
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Favorilere ekleme başarısız");
  return await res.json();
}

/**
 * Listeye ekle
 */
export async function addToList(itemId) {
  const currentUser = sessionManager.getCurrentUser();
  if (!currentUser) throw new Error("Giriş yapmalısın");
  
  const res = await fetch(`${API_URL}/items/${itemId}/add-to-list?user_id=${currentUser.user_id}`, {
    method: "POST",
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Listeye ekleme başarısız");
  return await res.json();
}

/**
 * Yorum sil
 */
export async function deleteReview(reviewId) {
  const res = await fetch(`${API_URL}/reviews/${reviewId}`, {
    method: "DELETE",
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Yorum silme başarısız");
  return await res.json();
}

/**
 * Yorum güncelle
 */
export async function updateReview(reviewId, reviewText, rating) {
  const res = await fetch(`${API_URL}/reviews/${reviewId}?review_text=${encodeURIComponent(reviewText)}&rating=${rating}`, {
    method: "PUT",
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Yorum güncelleme başarısız");
  return await res.json();
}

/**
 * İçerik güncelle
 */
export async function updateItem(itemId, data) {
  const res = await fetch(`${API_URL}/items/${itemId}`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error("İçerik güncelleme başarısız");
  return await res.json();
}

/**
 * İçerik sil
 */
export async function deleteItem(itemId) {
  const res = await fetch(`${API_URL}/items/${itemId}`, {
    method: "DELETE",
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("İçerik silme başarısız");
  return await res.json();
}

/**
 * Hali hazırdaki kullanıcıyı getir
 */
export async function getCurrentUser() {
  const res = await fetch(`${API_URL}/auth/current-user`, {
    headers: getHeaders()
  });
  if (!res.ok) throw new Error("Kullanıcı bilgisi alınamadı");
  return await res.json();
}
