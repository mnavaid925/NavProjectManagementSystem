/* ==========================================================================
   NavPMS — layout.js
   Owns the dashboard layout system driven by data-* attributes on <html>:
     - reads saved prefs from localStorage (falls back to the server-rendered
       data-* already on <html>), applies them,
     - wires the customizer controls, topbar dark-mode toggle, sidebar toggle,
       and fullscreen toggle,
     - persists every change to localStorage AND best-effort POSTs to the
       server via the customizer HTMX form,
     - hides the preloader on window load,
     - re-runs lucide.createIcons() after htmx swaps.
   ========================================================================== */
(function () {
  'use strict';

  var html = document.documentElement;
  var STORAGE_KEY = 'navpms.prefs';

  /* Pref name -> the data-* attribute it controls on <html>.
     'theme' and 'preloader' are handled specially (class / data-preloader). */
  var ATTR_MAP = {
    layout: 'data-layout',
    width: 'data-width',
    position: 'data-position',
    topbar: 'data-topbar',
    'sidebar-size': 'data-sidebar-size',
    'sidebar-color': 'data-sidebar-color',
    direction: 'dir'
  };

  var DEFAULTS = {
    theme: 'light',
    layout: 'vertical',
    width: 'fluid',
    position: 'fixed',
    topbar: 'light',
    'sidebar-size': 'default',
    'sidebar-color': 'light',
    direction: 'ltr',
    preloader: 'on'
  };

  /* ---------------------------------------------------------------------- */
  /* Storage helpers                                                        */
  /* ---------------------------------------------------------------------- */
  function loadStored() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) { return {}; }
  }

  function saveStored(prefs) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs)); } catch (e) {}
  }

  /* Build the active pref set: server-rendered data-* first, overridden by
     anything saved in localStorage. */
  function readServerPrefs() {
    return {
      theme: html.classList.contains('dark') ? 'dark' : 'light',
      layout: html.getAttribute('data-layout') || DEFAULTS.layout,
      width: html.getAttribute('data-width') || DEFAULTS.width,
      position: html.getAttribute('data-position') || DEFAULTS.position,
      topbar: html.getAttribute('data-topbar') || DEFAULTS.topbar,
      'sidebar-size': html.getAttribute('data-sidebar-size') || DEFAULTS['sidebar-size'],
      'sidebar-color': html.getAttribute('data-sidebar-color') || DEFAULTS['sidebar-color'],
      direction: html.getAttribute('dir') || DEFAULTS.direction,
      preloader: html.getAttribute('data-preloader') === 'disabled' ? 'off' : 'on'
    };
  }

  var prefs = Object.assign({}, DEFAULTS, readServerPrefs(), loadStored());

  /* ---------------------------------------------------------------------- */
  /* Apply prefs to the DOM                                                 */
  /* ---------------------------------------------------------------------- */
  function applyOne(key, value) {
    if (key === 'theme') {
      html.classList.toggle('dark', value === 'dark');
    } else if (key === 'preloader') {
      html.setAttribute('data-preloader', value === 'off' ? 'disabled' : 'enabled');
    } else if (ATTR_MAP[key]) {
      html.setAttribute(ATTR_MAP[key], value);
    }
  }

  function applyAll() {
    Object.keys(prefs).forEach(function (k) { applyOne(k, prefs[k]); });
    syncThemeIcon();
    syncCustomizerUI();
  }

  function syncThemeIcon() {
    var isDark = prefs.theme === 'dark';
    document.querySelectorAll('[data-theme-icon-dark]').forEach(function (el) {
      el.style.display = isDark ? 'none' : '';
    });
    document.querySelectorAll('[data-theme-icon-light]').forEach(function (el) {
      el.style.display = isDark ? '' : 'none';
    });
  }

  /* Reflect current prefs into customizer buttons + hidden inputs. */
  function syncCustomizerUI() {
    document.querySelectorAll('[data-pref]').forEach(function (btn) {
      var key = btn.getAttribute('data-pref');
      var val = btn.getAttribute('data-value');
      btn.classList.toggle('active', prefs[key] === val);
    });
    document.querySelectorAll('[data-pref-input]').forEach(function (input) {
      var key = input.getAttribute('data-pref-input');
      if (prefs[key] !== undefined) { input.value = prefs[key]; }
    });
  }

  /* ---------------------------------------------------------------------- */
  /* Change a preference (apply + persist + push to server)                 */
  /* ---------------------------------------------------------------------- */
  function setPref(key, value, push) {
    prefs[key] = value;
    applyOne(key, value);
    syncThemeIcon();
    syncCustomizerUI();
    saveStored(prefs);
    if (push !== false) { pushToServer(); }
  }

  /* Best-effort persist to the server via the customizer HTMX form. */
  function pushToServer() {
    var form = document.getElementById('customizer-form');
    if (!form) { return; }
    syncCustomizerUI();
    if (window.htmx && form.getAttribute('hx-post')) {
      // Fire the custom trigger HTMX is listening for.
      window.htmx.trigger(form, 'navpms:prefchange');
    }
  }

  /* ---------------------------------------------------------------------- */
  /* Wiring                                                                 */
  /* ---------------------------------------------------------------------- */
  function wireCustomizer() {
    document.querySelectorAll('[data-pref]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        setPref(btn.getAttribute('data-pref'), btn.getAttribute('data-value'));
      });
    });

    // Open / close customizer
    document.querySelectorAll('[data-customizer-open]').forEach(function (el) {
      el.addEventListener('click', function () {
        document.body.classList.add('customizer-open');
        closeAllDropdowns();
      });
    });
    document.querySelectorAll('[data-customizer-close]').forEach(function (el) {
      el.addEventListener('click', function () {
        document.body.classList.remove('customizer-open');
      });
    });

    // Reset to defaults
    document.querySelectorAll('[data-customizer-reset]').forEach(function (el) {
      el.addEventListener('click', function () {
        prefs = Object.assign({}, DEFAULTS);
        applyAll();
        saveStored(prefs);
        pushToServer();
      });
    });
  }

  function wireThemeToggle() {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        setPref('theme', prefs.theme === 'dark' ? 'light' : 'dark');
      });
    });
  }

  function isMobile() { return window.matchMedia('(max-width: 1023px)').matches; }

  function wireSidebarToggle() {
    document.querySelectorAll('[data-sidebar-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (isMobile()) {
          document.body.classList.toggle('sidebar-open');
        } else {
          document.body.classList.toggle('sidebar-collapsed');
        }
      });
    });
    document.querySelectorAll('[data-sidebar-close]').forEach(function (el) {
      el.addEventListener('click', function () {
        document.body.classList.remove('sidebar-open');
      });
    });
  }

  function wireFullscreen() {
    document.querySelectorAll('[data-fullscreen-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (!document.fullscreenElement) {
          (document.documentElement.requestFullscreen || function () {}).call(document.documentElement);
        } else if (document.exitFullscreen) {
          document.exitFullscreen();
        }
      });
    });
  }

  /* Dropdowns (topbar bell / apps / user) */
  function closeAllDropdowns() {
    document.querySelectorAll('.dropdown.open').forEach(function (d) { d.classList.remove('open'); });
  }
  function wireDropdowns() {
    document.querySelectorAll('[data-dropdown-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var dd = btn.closest('[data-dropdown]');
        var wasOpen = dd.classList.contains('open');
        closeAllDropdowns();
        if (!wasOpen) { dd.classList.add('open'); }
      });
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('[data-dropdown]')) { closeAllDropdowns(); }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        closeAllDropdowns();
        document.body.classList.remove('customizer-open', 'sidebar-open');
      }
    });
  }

  /* Collapsible module groups in the sidebar */
  function wireNavGroups() {
    document.querySelectorAll('[data-nav-group-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var group = btn.closest('[data-nav-group]');
        var submenu = group.querySelector('[data-nav-submenu]');
        var open = group.classList.toggle('open');
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (submenu) { submenu.classList.toggle('open', open); }
      });
    });
    // Auto-expand the group that contains the active sub-link.
    var activeSub = document.querySelector('.nav-sublink[data-active="true"]');
    if (activeSub) {
      var group = activeSub.closest('[data-nav-group]');
      if (group) {
        group.classList.add('open');
        var t = group.querySelector('[data-nav-group-toggle]');
        if (t) { t.setAttribute('aria-expanded', 'true'); }
        var sm = group.querySelector('[data-nav-submenu]');
        if (sm) { sm.classList.add('open'); }
      }
    }
  }

  /* Dismissible flash alerts */
  function wireAlerts() {
    document.querySelectorAll('[data-alert-close]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var alert = btn.closest('.alert');
        if (alert) { alert.remove(); }
      });
    });
  }

  /* Preloader */
  function hidePreloader() {
    var pre = document.getElementById('app-preloader');
    if (pre) { pre.classList.add('hidden'); }
  }

  /* ---------------------------------------------------------------------- */
  /* Boot                                                                   */
  /* ---------------------------------------------------------------------- */
  // Apply prefs ASAP (script is deferred, so DOM is parsed).
  applyAll();

  function init() {
    wireCustomizer();
    wireThemeToggle();
    wireSidebarToggle();
    wireFullscreen();
    wireDropdowns();
    wireNavGroups();
    wireAlerts();
    syncCustomizerUI();
    if (window.lucide) { lucide.createIcons(); }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Hide preloader once everything (images/fonts) has loaded.
  window.addEventListener('load', hidePreloader);
  // Safety net: never let the preloader trap the user.
  setTimeout(hidePreloader, 4000);

  // Re-init icons after HTMX swaps.
  document.addEventListener('htmx:afterSwap', function () {
    if (window.lucide) { lucide.createIcons(); }
  });

  // Expose a tiny API for debugging / page scripts.
  window.NavPMS = window.NavPMS || {};
  window.NavPMS.setPref = setPref;
  window.NavPMS.getPrefs = function () { return Object.assign({}, prefs); };
})();
