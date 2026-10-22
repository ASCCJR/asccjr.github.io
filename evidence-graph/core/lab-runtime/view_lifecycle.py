"""Bootstrap generated viewers after their deferred listeners; never patch published M3.

All generated entry scripts are parser-inserted, ordered defer scripts. A last
script starts the core only after every extension has registered eg:ready.
"""
BOOTSTRAP = ''''use strict';
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
'''


def prepare(texts: dict[str, str]) -> None:
    """Mutate only an in-memory build; refuse an unexpected source layout."""
    if texts['app.js'].count('\nboot();') != 1:
        raise ValueError('Unexpected core bootstrap; review lifecycle patch')
    if texts['index.html'].count('id="workspaceSource"') != 1:
        raise ValueError('Expected a single source selector')
    texts['app.js'] = texts['app.js'].replace('\nboot();', '\nwindow.EGStart = boot;')
    texts['index.html'] = texts['index.html'].replace(
        'id="workspaceSource"', 'id="workspaceSource" disabled aria-busy="true"')
    texts['index.html'] = texts['index.html'].replace(
        '</head>', '<script src="view_bootstrap.js" defer></script></head>')
    texts['view_bootstrap.js'] = BOOTSTRAP
