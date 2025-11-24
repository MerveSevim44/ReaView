/**
 * General Helper Utilities
 */

/**
 * Deep clone an object
 */
export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Check if object is empty
 */
export function isEmpty(obj) {
  if (!obj) return true;
  if (Array.isArray(obj)) return obj.length === 0;
  if (typeof obj === "object") return Object.keys(obj).length === 0;
  if (typeof obj === "string") return obj.trim().length === 0;
  return false;
}

/**
 * Get query parameter from URL
 */
export function getQueryParam(param) {
  const params = new URLSearchParams(window.location.search);
  return params.get(param);
}

/**
 * Get all query parameters
 */
export function getAllQueryParams() {
  const params = new URLSearchParams(window.location.search);
  const result = {};
  params.forEach((value, key) => {
    result[key] = value;
  });
  return result;
}

/**
 * Build query string from object
 */
export function buildQueryString(params) {
  if (isEmpty(params)) return "";
  const queryParams = new URLSearchParams();
  Object.keys(params).forEach(key => {
    if (params[key] !== null && params[key] !== undefined) {
      queryParams.append(key, params[key]);
    }
  });
  return queryParams.toString();
}

/**
 * Debounce function
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function
 */
export function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Retry promise with exponential backoff
 */
export async function retryWithBackoff(fn, maxRetries = 3, delay = 1000) {
  let lastError;
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }
  throw lastError;
}

/**
 * Copy to clipboard
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error("Failed to copy to clipboard:", err);
    return false;
  }
}

/**
 * Open share dialog
 */
export async function shareContent(data) {
  if (navigator.share) {
    try {
      await navigator.share(data);
      return true;
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error("Share failed:", err);
      }
      return false;
    }
  }
  return false;
}

/**
 * Log with context
 */
export function log(context, message, data = null) {
  const timestamp = new Date().toLocaleTimeString("tr-TR");
  const prefix = `[${timestamp}] ${context}`;
  if (data) {
    console.log(prefix, message, data);
  } else {
    console.log(prefix, message);
  }
}

/**
 * Log error with context
 */
export function logError(context, message, error = null) {
  const timestamp = new Date().toLocaleTimeString("tr-TR");
  const prefix = `[${timestamp}] ${context}`;
  if (error) {
    console.error(prefix, message, error);
  } else {
    console.error(prefix, message);
  }
}
