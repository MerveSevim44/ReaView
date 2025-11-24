/**
 * Formatter Utilities
 * Date, time, and other data formatting functions
 */

/**
 * Format date to locale string
 */
export function formatDate(dateString) {
  if (!dateString) return "—";
  try {
    return new Date(dateString).toLocaleDateString("tr-TR", {
      year: "numeric",
      month: "long",
      day: "numeric"
    });
  } catch (e) {
    console.warn("Date format error:", e);
    return dateString;
  }
}

/**
 * Format date and time to locale string
 */
export function formatDateTime(dateString) {
  if (!dateString) return "—";
  try {
    return new Date(dateString).toLocaleString("tr-TR", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch (e) {
    console.warn("DateTime format error:", e);
    return dateString;
  }
}

/**
 * Format relative time (e.g., "5 minutes ago")
 */
export function formatRelativeTime(dateString) {
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
    console.warn("Relative time format error:", e);
    return dateString;
  }
}

/**
 * Format rating value
 */
export function formatRating(rating) {
  if (rating === null || rating === undefined) return "—";
  return parseFloat(rating).toFixed(1);
}

/**
 * Generate user initials from username
 */
export function getUserInitials(username) {
  if (!username) return "?";
  return username
    .substring(0, 2)
    .toUpperCase();
}

/**
 * Truncate text to specified length
 */
export function truncateText(text, length = 100) {
  if (!text) return "";
  if (text.length <= length) return text;
  return text.substring(0, length) + "...";
}

/**
 * Capitalize first letter
 */
export function capitalize(text) {
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1);
}
