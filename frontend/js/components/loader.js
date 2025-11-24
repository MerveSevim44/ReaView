/**
 * Shared Loader Component
 */

export class Loader {
  static show(element, message = "Yükleniyor...") {
    if (!element) return;
    element.innerHTML = `<div class="loading">${message}</div>`;
  }

  static hide(element) {
    if (!element) return;
    element.innerHTML = "";
  }

  static showError(element, message) {
    if (!element) return;
    element.innerHTML = `
      <div class="error-message">
        <h3>❌ Hata</h3>
        <p>${message}</p>
      </div>
    `;
  }

  static showEmpty(element, message = "Veri bulunamadı") {
    if (!element) return;
    element.innerHTML = `
      <div class="empty-state">
        <p>${message}</p>
      </div>
    `;
  }
}

/**
 * Show toast notification
 */
export function showToast(message, type = "info", duration = 3000) {
  const toastId = `toast-${Date.now()}`;
  const typeClass = `toast-${type}`;

  const html = `
    <div id="${toastId}" class="toast ${typeClass}">
      <div class="toast-message">${message}</div>
      <button class="toast-close">&times;</button>
    </div>
  `;

  const container = document.getElementById("toastContainer") || createToastContainer();
  container.insertAdjacentHTML("beforeend", html);

  const toast = document.getElementById(toastId);
  const closeBtn = toast.querySelector(".toast-close");

  closeBtn?.addEventListener("click", () => {
    toast.remove();
  });

  if (duration > 0) {
    setTimeout(() => {
      toast.remove();
    }, duration);
  }
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
  const container = document.createElement("div");
  container.id = "toastContainer";
  container.className = "toast-container";
  document.body.appendChild(container);
  return container;
}

/**
 * Show success toast
 */
export function showSuccess(message, duration = 3000) {
  showToast(`✅ ${message}`, "success", duration);
}

/**
 * Show error toast
 */
export function showErrorToast(message, duration = 5000) {
  showToast(`❌ ${message}`, "error", duration);
}

/**
 * Show warning toast
 */
export function showWarning(message, duration = 4000) {
  showToast(`⚠️ ${message}`, "warning", duration);
}

/**
 * Show info toast
 */
export function showInfo(message, duration = 3000) {
  showToast(`ℹ️ ${message}`, "info", duration);
}
