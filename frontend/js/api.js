// frontend/js/api.js

const API_URL = "http://127.0.0.1:8000";

// Tüm içerikleri getir
export async function getItems() {
  const res = await fetch(`${API_URL}/items`);
  if (!res.ok) throw new Error("Sunucu hatası");
  return await res.json();
}

// Tek içerik detayı
export async function getItemById(id) {
  const res = await fetch(`${API_URL}/items/${id}`);
  if (!res.ok) throw new Error("İçerik bulunamadı");
  return await res.json();
}

// Yeni yorum ekle
export async function postReview(data) {
  const res = await fetch(`${API_URL}/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return await res.json();
}

// Bir içeriğe ait yorumları getir
export async function getReviews(itemId) {
  const res = await fetch(`${API_URL}/reviews/item/${itemId}`);
  return await res.json();
}
