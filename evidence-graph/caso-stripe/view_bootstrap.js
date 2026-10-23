'use strict';
(() => {
  const select = document.getElementById('workspaceSource');
  if (window.EG_BOOT_STARTED) return;
  window.EG_BOOT_STARTED = true;
  window.EG_WORKSPACE_READY = false;
  document.addEventListener('eg:ready', () => {
    // This handler was registered last, after graph, investigation and source UI.
    window.EG_WORKSPACE_READY = true;
    if (select) { select.disabled = false; select.removeAttribute('aria-busy'); }
    document.dispatchEvent(new CustomEvent('eg:workspace-ready'));
  }, {once:true});
  if (typeof window.EGStart !== 'function') throw new Error('Inicialização incompleta');
  window.EGStart();
})();
