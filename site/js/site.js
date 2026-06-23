/* site/js/site.js — shared utilities */

// ── Animate stat bars on scroll ──────────────────────────────
function initStatBars() {
  const fills = document.querySelectorAll('.stat-bar-fill[data-pct]');
  if (!fills.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        el.style.width = el.dataset.pct + '%';
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.3 });

  fills.forEach(el => observer.observe(el));
}

// ── Last-updated badge ────────────────────────────────────────
function initLastUpdated() {
  const el = document.getElementById('last-updated');
  if (!el) return;
  fetch('data/last_updated.json')
    .then(r => r.json())
    .then(d => {
      const date = new Date(d.updated).toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric'
      });
      el.textContent = 'Data last updated ' + date;
    })
    .catch(() => { el.textContent = ''; });
}

// ── Mark current page in nav ──────────────────────────────────
function initActiveNav() {
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === page) a.classList.add('active');
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initStatBars();
  initLastUpdated();
  initActiveNav();
});
