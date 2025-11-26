/**
 * Global Constants and Configuration
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: "http://127.0.0.1:8000",
  TIMEOUT: 30000,
  HEADERS: {
    "Content-Type": "application/json"
  }
};

// Storage Keys
export const STORAGE_KEYS = {
  CURRENT_USER: "currentUser",
  AUTH_TOKEN: "authToken",
  SEARCH_STATE: "searchState",
  SEARCH_ITEMS: "searchItems"
};

// Activity Types
export const ACTIVITY_TYPES = {
  REVIEW: "review",
  RATING: "rating",
  LIST_ADD: "list_add",
  FOLLOW: "follow",
  COMMENT: "comment",
  RATED: "rated",
  ADDED_TO_LIST: "added_to_list",
  FAVORITED: "favorited"
};

// Activity Descriptions
export const ACTIVITY_DESCRIPTIONS = {
  review: "yorum yaptı",
  rating: "puan verdi",
  list_add: "listeye ekledi",
  follow: "kullanıcıyı takip etti",
  comment: "yorum yaptı",
  rated: "puan verdi",
  added_to_list: "listesine ekledi",
  favorited: "favorilerine ekledi"
};

// Validation Rules
export const VALIDATION = {
  USERNAME_MIN_LENGTH: 3,
  PASSWORD_MIN_LENGTH: 6,
  EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
};

// Messages
export const MESSAGES = {
  AUTH: {
    LOGIN_SUCCESS: "✅ Giriş başarılı! Yönlendiriliyorsunuz...",
    LOGIN_FAILED: "❌ Giriş başarısız. Lütfen bilgilerinizi kontrol edin.",
    REGISTER_SUCCESS: "✅ Kayıt başarılı! Yönlendiriliyorsunuz...",
    REGISTER_FAILED: "❌ Kayıt başarısız. Lütfen bilgilerinizi kontrol edin.",
    LOGOUT_SUCCESS: "✅ Çıkış işlemi tamamlandı"
  },
  VALIDATION: {
    INVALID_EMAIL: "Geçerli bir e-posta girin",
    USERNAME_TOO_SHORT: "Kullanıcı adı en az 3 karakter olmalı",
    PASSWORD_TOO_SHORT: "Şifre en az 6 karakter olmalı",
    REQUIRED_FIELD: "Bu alan zorunludur"
  },
  ERRORS: {
    SERVER_ERROR: "Sunucu hatası oluştu",
    NETWORK_ERROR: "Ağ bağlantısı başarısız",
    UNAUTHORIZED: "Giriş gerekli",
    FORBIDDEN: "Bu işlemi yapmak için yetkiniz yok",
    NOT_FOUND: "İçerik bulunamadı"
  }
};

// Routes
export const ROUTES = {
  AUTH: {
    LOGIN: "/auth/login",
    REGISTER: "/auth/register",
    CURRENT_USER: "/auth/current-user"
  },
  ITEMS: {
    LIST: "/items",
    DETAIL: "/items/:id",
    SEARCH: "/items/search",
    RATING: "/items/:id/rating",
    FAVORITE: "/items/:id/favorite",
    ADD_TO_LIST: "/items/:id/add-to-list"
  },
  REVIEWS: {
    LIST: "/reviews",
    BY_ITEM: "/reviews/item/:id",
    DETAIL: "/reviews/:id",
    DELETE: "/reviews/:id",
    UPDATE: "/reviews/:id"
  },
  USERS: {
    DETAIL: "/users/:id",
    REVIEWS: "/users/:id/reviews",
    ACTIVITIES: "/users/:id/activities",
    FOLLOWING: "/users/:id/following",
    FOLLOWERS: "/users/:id/followers"
  },
  FOLLOWS: {
    FOLLOW: "/users/:id/follow",
    UNFOLLOW: "/users/:id/unfollow",
    FOLLOWING: "/users/:id/following",
    FOLLOWERS: "/users/:id/followers"
  },
  FEED: "/feed",
  EXTERNAL: {
    SEARCH: "/external/search",
    IMPORT: "/external/import"
  }
};

// Pagination
export const PAGINATION = {
  PAGE_SIZE: 20,
  DEFAULT_PAGE: 1
};
