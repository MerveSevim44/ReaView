// frontend/js/items.js
import { API_URL, getItemById, getReviews, postReview } from './api.js';

let currentItemId = null;

// Get item ID from URL query parameter
function getItemIdFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get('id') || 1;
}

// Load item details
export async function loadItemDetails() {
  try {
    currentItemId = getItemIdFromURL();
    
    console.log(`Fetching item ${currentItemId} from ${API_URL}/items/${currentItemId}`);
    const item = await getItemById(currentItemId);
    
    console.log('Item loaded:', item);
    displayItemDetails(item);
    
    // Load reviews after item is loaded
    loadReviews(currentItemId);
  } catch (error) {
    console.error('Error loading item:', error);
    document.getElementById('itemBox').innerHTML = `<div class="loading">❌ Hata: ${error.message}</div>`;
  }
}

// Display item details on page
function displayItemDetails(item) {
  if (!item) {
    document.getElementById('itemBox').innerHTML = '<div class="loading">❌ İçerik bulunamadı</div>';
    return;
  }

  document.title = `${item.title || 'İçerik'} • BiblioNet`;
  document.getElementById('itemTitle').textContent = item.title || 'Başlık Yok';
  document.getElementById('itemType').textContent = item.item_type || 'İçerik';
  document.getElementById('itemYear').textContent = item.year || '—';
  
  // Ratings will be calculated from reviews when they load
  document.getElementById('itemRating').textContent = `⭐ —`;
  
  document.getElementById('itemDesc').textContent = item.description || 'Açıklama bulunmamaktadır.';
  
  console.log('Item details displayed');
}

// Load reviews for item
export async function loadReviews(itemId) {
  try {
    console.log(`Fetching reviews for item ${itemId}...`);
    const reviews = await getReviews(itemId);
    
    console.log('Reviews received:', reviews);
    
    const reviewsList = document.getElementById('reviewsList');
    if (!reviews || reviews.length === 0) {
      reviewsList.innerHTML = '<p style="text-align: center; color: #999;">Henüz yorum yok</p>';
      return;
    }

    reviewsList.innerHTML = reviews.map(r => {
      console.log('Rendering review:', r);
      return `
      <div class="review-item">
        <div class="review-author">${r.username || `Kullanıcı #${r.user_id}`}</div>
        <div class="review-text">${r.review_text || 'Yorum metni yok'}</div>
        <div class="review-date">${r.created_at ? new Date(r.created_at).toLocaleDateString('tr-TR') : '—'}</div>
      </div>
    `;
    }).join('');
  } catch (error) {
    console.error('Yorumlar yüklenemedi:', error);
    document.getElementById('reviewsList').innerHTML = `<p style="color: #e74c3c;">Yorumlar yüklenemedi: ${error.message}</p>`;
  }
}

// Submit new review
export async function submitReview() {
  const reviewText = document.getElementById('reviewText').value.trim();
  
  if (!reviewText) {
    alert('Lütfen bir yorum yazınız');
    return;
  }

  const userId = localStorage.getItem('userId') || 1; // Get from localStorage or use default

  try {
    console.log('Submitting review:', { user_id: userId, item_id: currentItemId, review_text: reviewText });
    
    await postReview({
      user_id: parseInt(userId),
      item_id: currentItemId,
      review_text: reviewText
    });

    // Clear textarea
    document.getElementById('reviewText').value = '';
    
    // Reload reviews
    await loadReviews(currentItemId);
    
    alert('✅ Yorum başarıyla gönderildi!');
  } catch (error) {
    console.error('Error submitting review:', error);
    alert('Hata: ' + error.message);
  }
}

// Add item to user's list
export async function addToList() {
  const userId = localStorage.getItem('userId') || 1;

  try {
    console.log(`Adding item ${currentItemId} to user ${userId}'s list...`);
    const response = await fetch(`${API_URL}/items/${currentItemId}/add-to-list`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'İçerik listeme eklenemedi');
    }

    alert('✅ İçerik listeme eklendi!');
  } catch (error) {
    console.error('Error adding to list:', error);
    alert('Listeme eklenemedi: ' + error.message);
  }
}

// Add item to favorites
export async function toggleFavorite() {
  const userId = localStorage.getItem('userId') || 1;
  const btn = document.getElementById('favoriteBtn');

  try {
    console.log(`Toggling favorite for item ${currentItemId}...`);
    const response = await fetch(`${API_URL}/items/${currentItemId}/favorite`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Favorilere eklenemedi');
    }

    // Toggle button style
    btn.classList.toggle('favorited');
    if (btn.classList.contains('favorited')) {
      alert('❤️ İçerik favorilerinize eklendi!');
    } else {
      alert('Favorilerden kaldırıldı');
    }
  } catch (error) {
    console.error('Error toggling favorite:', error);
    alert('Hata: ' + error.message);
  }
}

// Initialize event listeners
export function initEventListeners() {
  const submitBtn = document.getElementById('submitReviewBtn');
  if (submitBtn) {
    submitBtn.addEventListener('click', submitReview);
  }

  const addListBtn = document.getElementById('addToListBtn');
  if (addListBtn) {
    addListBtn.addEventListener('click', addToList);
  }

  const favoriteBtn = document.getElementById('favoriteBtn');
  if (favoriteBtn) {
    favoriteBtn.addEventListener('click', toggleFavorite);
  }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM Content Loaded - Initializing items page');
  initEventListeners();
  loadItemDetails();
});
