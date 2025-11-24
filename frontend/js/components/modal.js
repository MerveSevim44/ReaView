/**
 * Shared Modal Component
 */

export class Modal {
  constructor(id, title = "") {
    this.id = id;
    this.title = title;
    this.element = document.getElementById(id);
  }

  open() {
    if (this.element) {
      this.element.classList.add("show");
      this.element.style.display = "block";
    }
  }

  close() {
    if (this.element) {
      this.element.classList.remove("show");
      this.element.style.display = "none";
    }
  }

  toggle() {
    if (this.element) {
      if (this.element.style.display === "none") {
        this.open();
      } else {
        this.close();
      }
    }
  }

  setContent(html) {
    const content = this.element?.querySelector(".modal-content");
    if (content) {
      content.innerHTML = html;
    }
  }

  onClose(callback) {
    const closeBtn = this.element?.querySelector(".modal-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        this.close();
        callback?.();
      });
    }
  }

  destroy() {
    this.close();
    this.element?.remove();
  }
}

/**
 * Create modal element
 */
export function createModal(id, title, content = "") {
  const html = `
    <div id="${id}" class="modal-overlay">
      <div class="modal-dialog">
        <div class="modal-header">
          <h2>${title}</h2>
          <button class="modal-close">&times;</button>
        </div>
        <div class="modal-content">
          ${content}
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML("beforeend", html);
  return new Modal(id);
}
