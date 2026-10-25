"""Minimal responsive dashboard styles and touch-friendly detail interactions."""

CSS = r"""
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: #111827; color: #f9fafb; font-family: system-ui, sans-serif; }
main { max-width: 1100px; padding: clamp(.65rem, 2vw, 1.5rem); margin: auto; }
h1 { margin: .2rem 0 1rem; }
h2 { font-size: 1.1rem; }
.grid { display: grid; grid-template-columns: repeat(var(--cols), minmax(0, 1fr)); gap: .7rem; }
article { min-width: 0; min-height: 112px; padding: 12px; display: flex;
          flex-direction: column; gap: 12px; border: 1px solid #374151;
          border-radius: 12px; background: #1f2937; }
.bin-heading { display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
               justify-content: space-between; }
.dots { display: flex; flex-wrap: wrap; gap: 8px; }
.dot { appearance: none; display: inline-block; width: 44px; height: 44px;
       flex: none; border: 2px solid #9ca3af; border-radius: 50%;
       cursor: pointer; padding: 0; }
.dot:focus-visible { outline: 3px solid #7dd3fc; outline-offset: 3px; }
.dot:hover { border-color: #f9fafb; }
.error { color: #fca5a5; }

dialog { width: min(420px, calc(100vw - 24px)); max-width: 100%; padding: 0;
         color: #f9fafb; background: #1f2937; border: 1px solid #6b7280;
         border-radius: 16px; box-shadow: 0 20px 60px #000a; }
dialog::backdrop { background: rgba(0,0,0,.65); }
.details-panel { padding: 18px; }
.details-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.details-header h2 { margin: 0; }
.details-close { min-width: 44px; min-height: 44px; border-radius: 10px;
                 border: 1px solid #6b7280; color: inherit; background: #374151;
                 cursor: pointer; font-size: 1.5rem; }
.detail-swatch { display: block; width: 60px; height: 60px; margin: 12px 0;
                 border: 2px solid #9ca3af; border-radius: 50%; }
.details-list { margin: 0; display: grid; gap: 12px; }
.details-list div { min-width: 0; }
.details-list dt { color: #d1d5db; font-size: .85rem; }
.details-list dd { margin: 3px 0 0; font-weight: 600; overflow-wrap: anywhere; }
@media (max-width: 599px) {
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .55rem; }
  article { padding: 10px; }
}
@media (max-width: 359px) {
  .grid { grid-template-columns: minmax(0, 1fr); }
}
@media (hover: hover) and (pointer: fine) {
  .dot { width: 32px; height: 32px; }
}
"""

SCRIPT = r"""
(() => {
  const dialog = document.getElementById("filament-details");
  const manufacturer = document.getElementById("detail-manufacturer");
  const name = document.getElementById("detail-name");
  const colors = document.getElementById("detail-colors");
  const preview = document.getElementById("detail-swatch");
  const close = document.getElementById("filament-details-close");
  let selectedButton = null;

  function closeDetails() {
    if (typeof dialog.close === "function") dialog.close();
    else {
      dialog.removeAttribute("open");
      selectedButton?.focus({ preventScroll: true });
      selectedButton = null;
    }
  }

  document.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-filament]");
    if (!button) return;
    selectedButton = button;
    // textContent never interprets filament details as HTML.
    manufacturer.textContent = button.dataset.manufacturer;
    name.textContent = button.dataset.name;
    colors.textContent = button.dataset.colors;
    preview.style.background = button.style.background;
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
    close.focus({ preventScroll: true });
  });

  close.addEventListener("click", closeDetails);
  dialog.addEventListener("close", () => {
    selectedButton?.focus({ preventScroll: true });
    selectedButton = null;
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) closeDetails();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && dialog.open) {
      event.preventDefault();
      closeDetails();
    }
  });
  // Don't interrupt a user inspecting a filament with the periodic refresh.
  window.setInterval(() => {
    if (!dialog.open && !document.hidden) window.location.reload();
  }, 30000);
})();
"""
