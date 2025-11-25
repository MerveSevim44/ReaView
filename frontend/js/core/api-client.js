/**
 * API Client
 * Centralized API communication
 */

import { sessionManager } from "./session-manager.js";
import { API_CONFIG, ROUTES } from "../utils/constants.js";

class ApiClient {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
  }

  /**
   * Get authorization headers
   */
  getHeaders() {
    const headers = { ...API_CONFIG.HEADERS };
    const token = sessionManager.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  /**
   * Make HTTP request
   */
  async request(method, endpoint, data = null) {
    const url = `${this.baseURL}${endpoint}`;
    const options = {
      method,
      headers: this.getHeaders()
    };

    if (data && (method === "POST" || method === "PUT")) {
      options.body = JSON.stringify(data);
    }

    try {
      console.log(`📡 [${method}] ${url}`, data || '');
      
      const response = await fetch(url, options);

      if (!response.ok) {
        const error = await response.json();
        const errorMsg = error.detail || `HTTP ${response.status}`;
        console.error(`❌ [${method}] ${url} - ${errorMsg}`, error);
        throw new Error(errorMsg);
      }

      const result = await response.json();
      console.log(`✅ [${method}] ${url}`, result);
      return result;
    } catch (err) {
      console.error(`🔴 API ERROR [${method}] ${url}:`, err.message);
      throw err;
    }
  }

  /**
   * GET request
   */
  get(endpoint) {
    return this.request("GET", endpoint);
  }

  /**
   * POST request
   */
  post(endpoint, data) {
    return this.request("POST", endpoint, data);
  }

  /**
   * PUT request
   */
  put(endpoint, data) {
    return this.request("PUT", endpoint, data);
  }

  /**
   * DELETE request
   */
  delete(endpoint) {
    return this.request("DELETE", endpoint);
  }
}

// ============= AUTH ENDPOINTS =============

export async function loginUser(email, password) {
  const client = new ApiClient();
  return client.post(ROUTES.AUTH.LOGIN, { email, password });
}

export async function registerUser(username, email, password) {
  const client = new ApiClient();
  return client.post(ROUTES.AUTH.REGISTER, { username, email, password });
}

export async function getCurrentUser() {
  const client = new ApiClient();
  return client.get(ROUTES.AUTH.CURRENT_USER);
}

// ============= ITEMS ENDPOINTS =============

export async function getItems() {
  const client = new ApiClient();
  return client.get(ROUTES.ITEMS.LIST);
}

export async function getItemById(id) {
  const client = new ApiClient();
  return client.get(ROUTES.ITEMS.DETAIL.replace(":id", id));
}

export async function searchItems(query, itemType = null) {
  const client = new ApiClient();
  let endpoint = `${ROUTES.ITEMS.SEARCH}?q=${encodeURIComponent(query)}`;
  if (itemType) {
    endpoint += `&item_type=${itemType}`;
  }
  return client.get(endpoint);
}

export async function getItemRating(itemId) {
  const client = new ApiClient();
  return client.get(ROUTES.ITEMS.RATING.replace(":id", itemId));
}

export async function addToFavorite(itemId) {
  const client = new ApiClient();
  const currentUser = sessionManager.getCurrentUser();
  if (!currentUser) throw new Error("Login required");
  return client.post(
    `${ROUTES.ITEMS.FAVORITE.replace(":id", itemId)}?user_id=${currentUser.user_id}`,
    {}
  );
}

export async function addToList(itemId) {
  const client = new ApiClient();
  const currentUser = sessionManager.getCurrentUser();
  if (!currentUser) throw new Error("Login required");
  return client.post(
    `${ROUTES.ITEMS.ADD_TO_LIST.replace(":id", itemId)}?user_id=${currentUser.user_id}`,
    {}
  );
}

export async function updateItem(itemId, data) {
  const client = new ApiClient();
  return client.put(ROUTES.ITEMS.DETAIL.replace(":id", itemId), data);
}

export async function deleteItem(itemId) {
  const client = new ApiClient();
  return client.delete(ROUTES.ITEMS.DETAIL.replace(":id", itemId));
}

// ============= REVIEWS ENDPOINTS =============

export async function postReview(data) {
  const client = new ApiClient();
  return client.post(ROUTES.REVIEWS.LIST, data);
}

export async function getReviews(itemId) {
  const client = new ApiClient();
  return client.get(ROUTES.REVIEWS.BY_ITEM.replace(":id", itemId));
}

export async function updateReview(reviewId, reviewText, rating) {
  const client = new ApiClient();
  return client.put(
    `${ROUTES.REVIEWS.UPDATE.replace(":id", reviewId)}?review_text=${encodeURIComponent(
      reviewText
    )}&rating=${rating}`,
    {}
  );
}

export async function deleteReview(reviewId) {
  const client = new ApiClient();
  return client.delete(ROUTES.REVIEWS.DETAIL.replace(":id", reviewId));
}

// ============= USERS ENDPOINTS =============

export async function getUser(userId) {
  const client = new ApiClient();
  return client.get(ROUTES.USERS.DETAIL.replace(":id", userId));
}

export async function getUserReviews(userId) {
  const client = new ApiClient();
  return client.get(ROUTES.USERS.REVIEWS.replace(":id", userId));
}

export async function getUserActivities(userId) {
  const client = new ApiClient();
  return client.get(ROUTES.USERS.ACTIVITIES.replace(":id", userId));
}

export async function getFollowing(userId) {
  const client = new ApiClient();
  return client.get(ROUTES.USERS.FOLLOWING.replace(":id", userId));
}

export async function getFollowers(userId) {
  const client = new ApiClient();
  return client.get(ROUTES.USERS.FOLLOWERS.replace(":id", userId));
}

// ============= FOLLOWS ENDPOINTS =============

export async function followUser(userId) {
  const client = new ApiClient();
  const currentUser = sessionManager.getCurrentUser();
  if (!currentUser) throw new Error("Login required");
  return client.post(
    `${ROUTES.FOLLOWS.FOLLOW.replace(":id", userId)}?follower_id=${currentUser.user_id}`,
    {}
  );
}

export async function unfollowUser(userId) {
  const client = new ApiClient();
  const currentUser = sessionManager.getCurrentUser();
  if (!currentUser) throw new Error("Login required");
  return client.delete(
    `${ROUTES.FOLLOWS.UNFOLLOW.replace(":id", userId)}?follower_id=${currentUser.user_id}`
  );
}

// ============= FEED ENDPOINTS =============

export async function getFeed(userId = null) {
  const client = new ApiClient();
  let endpoint = ROUTES.FEED;
  if (userId) {
    endpoint += `?user_id=${userId}`;
  }
  return client.get(endpoint);
}

// ============= EXTERNAL API ENDPOINTS =============

export async function searchExternal(type, query) {
  const client = new ApiClient();
  return client.get(`${ROUTES.EXTERNAL.SEARCH}?type=${type}&query=${encodeURIComponent(query)}`);
}

export async function importItemFromExternal(type, query) {
  const client = new ApiClient();
  return client.post(`${ROUTES.EXTERNAL.IMPORT}?type=${type}&query=${encodeURIComponent(query)}`, {});
}

// Export API client for custom requests
export { ApiClient };
