/**
 * Validator Utilities
 * Form validation and data validation functions
 */

import { VALIDATION, MESSAGES } from "./constants.js";

/**
 * Validate email format
 */
export function isValidEmail(email) {
  if (!email) return false;
  return VALIDATION.EMAIL_PATTERN.test(email);
}

/**
 * Validate username
 */
export function isValidUsername(username) {
  if (!username) return false;
  return username.trim().length >= VALIDATION.USERNAME_MIN_LENGTH;
}

/**
 * Validate password
 */
export function isValidPassword(password) {
  if (!password) return false;
  return password.length >= VALIDATION.PASSWORD_MIN_LENGTH;
}

/**
 * Validate login form
 */
export function validateLoginForm(email, password) {
  const errors = [];

  if (!email) {
    errors.push(MESSAGES.VALIDATION.REQUIRED_FIELD + " (E-posta)");
  } else if (!isValidEmail(email)) {
    errors.push(MESSAGES.VALIDATION.INVALID_EMAIL);
  }

  if (!password) {
    errors.push(MESSAGES.VALIDATION.REQUIRED_FIELD + " (Şifre)");
  } else if (!isValidPassword(password)) {
    errors.push(MESSAGES.VALIDATION.PASSWORD_TOO_SHORT);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validate registration form
 */
export function validateRegisterForm(username, email, password) {
  const errors = [];

  if (!username) {
    errors.push(MESSAGES.VALIDATION.REQUIRED_FIELD + " (Kullanıcı Adı)");
  } else if (!isValidUsername(username)) {
    errors.push(MESSAGES.VALIDATION.USERNAME_TOO_SHORT);
  }

  if (!email) {
    errors.push(MESSAGES.VALIDATION.REQUIRED_FIELD + " (E-posta)");
  } else if (!isValidEmail(email)) {
    errors.push(MESSAGES.VALIDATION.INVALID_EMAIL);
  }

  if (!password) {
    errors.push(MESSAGES.VALIDATION.REQUIRED_FIELD + " (Şifre)");
  } else if (!isValidPassword(password)) {
    errors.push(MESSAGES.VALIDATION.PASSWORD_TOO_SHORT);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validate review text
 */
export function isValidReview(reviewText) {
  if (!reviewText) return false;
  return reviewText.trim().length > 0 && reviewText.trim().length <= 2000;
}

/**
 * Validate rating value (0-10)
 */
export function isValidRating(rating) {
  const num = parseFloat(rating);
  return !isNaN(num) && num >= 0 && num <= 10;
}

/**
 * Validate search query
 */
export function isValidSearchQuery(query) {
  if (!query) return false;
  return query.trim().length > 0;
}
