/* ==========================================================================
   NavPMS — charts.js
   Reads the CHART DATA CONTRACT that the dashboard template writes:

     1. Projects overview (doughnut, brand-blue palette)
        <canvas id="chart-projects-overview"></canvas>
        <script id="data-projects-overview" type="application/json">
          {"labels": [...], "data": [...]}
        </script>

     2. Income vs Expense (smooth area/line; income = brand blue, expense = amber)
        <canvas id="chart-income-expense"></canvas>
        <script id="data-income-expense" type="application/json">
          {"labels": [...], "income": [...], "expense": [...]}
        </script>

   For each chart: if BOTH the <script> data tag and the <canvas> exist, parse
   the JSON and init Chart.js; otherwise no-op. Safe to call once on
   DOMContentLoaded (guards against double-init).
   ========================================================================== */
(function () {
  'use strict';

  var initialized = false;

  /* Read theme-aware colors from CSS variables so charts match light/dark. */
  function cssVar(name, fallback) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(name);
    return (v && v.trim()) || fallback;
  }

  function isDark() { return document.documentElement.classList.contains('dark'); }

  function readJSON(id) {
    var tag = document.getElementById(id);
    if (!tag) { return null; }
    try { return JSON.parse(tag.textContent || tag.innerText || 'null'); }
    catch (e) { return null; }
  }

  function gridColor() { return isDark() ? 'rgba(148,163,184,0.15)' : 'rgba(15,23,42,0.07)'; }
  function tickColor() { return isDark() ? '#94a3b8' : '#64748b'; }

  /* Keep references so we can destroy + rebuild on theme change. */
  var charts = {};

  function destroyAll() {
    Object.keys(charts).forEach(function (k) {
      if (charts[k]) { charts[k].destroy(); charts[k] = null; }
    });
  }

  /* ---- 1. Projects overview (doughnut) ---- */
  function initProjectsOverview() {
    var canvas = document.getElementById('chart-projects-overview');
    var data = readJSON('data-projects-overview');
    if (!canvas || !data || !Array.isArray(data.labels)) { return; }

    var palette = [
      cssVar('--brand-600', '#2563eb'),
      cssVar('--brand-400', '#60a5fa'),
      cssVar('--brand-800', '#1e40af'),
      cssVar('--brand-300', '#93c5fd'),
      cssVar('--brand-200', '#bfdbfe'),
      '#64748b'
    ];

    charts.projects = new Chart(canvas.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.data || [],
          backgroundColor: palette,
          borderColor: isDark() ? '#0f172a' : '#ffffff',
          borderWidth: 2,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '64%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: tickColor(), usePointStyle: true, pointStyle: 'circle', padding: 16, boxWidth: 8 }
          },
          tooltip: { padding: 10, cornerRadius: 8 }
        }
      }
    });
  }

  /* ---- 2. Income vs Expense (smooth area/line) ---- */
  function initIncomeExpense() {
    var canvas = document.getElementById('chart-income-expense');
    var data = readJSON('data-income-expense');
    if (!canvas || !data || !Array.isArray(data.labels)) { return; }

    var ctx = canvas.getContext('2d');
    var brand = cssVar('--brand-600', '#2563eb');
    var amber = '#f59e0b';

    var incomeFill = ctx.createLinearGradient(0, 0, 0, canvas.height || 300);
    incomeFill.addColorStop(0, 'rgba(37,99,235,0.28)');
    incomeFill.addColorStop(1, 'rgba(37,99,235,0.0)');

    var expenseFill = ctx.createLinearGradient(0, 0, 0, canvas.height || 300);
    expenseFill.addColorStop(0, 'rgba(245,158,11,0.22)');
    expenseFill.addColorStop(1, 'rgba(245,158,11,0.0)');

    charts.incomeExpense = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Income',
            data: data.income || [],
            borderColor: brand,
            backgroundColor: incomeFill,
            fill: true, tension: 0.4, borderWidth: 2,
            pointRadius: 0, pointHoverRadius: 5, pointBackgroundColor: brand
          },
          {
            label: 'Expense',
            data: data.expense || [],
            borderColor: amber,
            backgroundColor: expenseFill,
            fill: true, tension: 0.4, borderWidth: 2,
            pointRadius: 0, pointHoverRadius: 5, pointBackgroundColor: amber
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { position: 'top', align: 'end', labels: { color: tickColor(), usePointStyle: true, pointStyle: 'circle', boxWidth: 8, padding: 14 } },
          tooltip: { padding: 10, cornerRadius: 8 }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: tickColor() }, border: { display: false } },
          y: { grid: { color: gridColor() }, ticks: { color: tickColor() }, border: { display: false }, beginAtZero: true }
        }
      }
    });
  }

  function initAll() {
    if (typeof Chart === 'undefined') { return; }
    destroyAll();
    initProjectsOverview();
    initIncomeExpense();
    initialized = true;
  }

  function boot() {
    if (initialized) { return; }
    initAll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  // Rebuild charts after HTMX swaps the dashboard content in.
  document.addEventListener('htmx:afterSwap', function () { initAll(); });

  // Rebuild on theme change so colors stay correct (layout.js toggles .dark).
  var themeObserver = new MutationObserver(function (mutations) {
    for (var i = 0; i < mutations.length; i++) {
      if (mutations[i].attributeName === 'class') { initAll(); break; }
    }
  });
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });

  // Expose for the dashboard page to re-init manually if needed.
  window.NavPMSCharts = { init: initAll };
})();
