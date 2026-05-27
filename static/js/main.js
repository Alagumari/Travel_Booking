/* ===================================================
   TravelX Pro - Main JavaScript
   =================================================== */

'use strict';

// ===== PAGE LOADER =====
document.addEventListener('DOMContentLoaded', () => {
  const loader = document.getElementById('pageLoader');
  if (loader) {
    setTimeout(() => loader.classList.add('hidden'), 800);
  }
});

// ===== BACK TO TOP =====
(function initBackToTop() {
  const btn = document.createElement('button');
  btn.className = 'back-to-top';
  btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
  btn.setAttribute('aria-label', 'Back to top');
  document.body.appendChild(btn);

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

// ===== SCROLL REVEAL =====
(function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        const delay = entry.target.dataset.delay || (i * 80);
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, parseInt(delay));
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.fade-up, .fade-left, .fade-right').forEach(el => {
    observer.observe(el);
  });
})();

// ===== COUNTER ANIMATION =====
function animateCounter(el, target, duration = 1800) {
  const start = performance.now();
  const startVal = 0;

  function update(timestamp) {
    const elapsed = timestamp - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(startVal + (target - startVal) * ease);

    el.textContent = current.toLocaleString('en-IN');
    if (progress < 1) requestAnimationFrame(update);
    else el.textContent = target.toLocaleString('en-IN');
  }
  requestAnimationFrame(update);
}

(function initCounters() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseInt(el.dataset.count || el.textContent.replace(/\D/g, ''));
        if (target) animateCounter(el, target);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('[data-count], .counter-num').forEach(el => observer.observe(el));
})();

// ===== TOAST NOTIFICATIONS =====
const TXToast = {
  container: null,

  init() {
    if (!this.container) {
      this.container = document.querySelector('.toast-container-tx');
      if (!this.container) {
        this.container = document.createElement('div');
        this.container.className = 'toast-container-tx';
        document.body.appendChild(this.container);
      }
    }
  },

  show(message, type = 'info', duration = 4000) {
    this.init();
    const icons = {
      success: '<i class="bi bi-check-circle-fill" style="color:var(--tx-green);font-size:1.1rem;"></i>',
      error: '<i class="bi bi-x-circle-fill" style="color:var(--tx-coral);font-size:1.1rem;"></i>',
      warning: '<i class="bi bi-exclamation-triangle-fill" style="color:var(--tx-gold);font-size:1.1rem;"></i>',
      info: '<i class="bi bi-info-circle-fill" style="color:var(--tx-teal);font-size:1.1rem;"></i>',
    };

    const toast = document.createElement('div');
    toast.className = 'toast toast-tx show mb-2 animate__animated animate__fadeInRight';
    toast.innerHTML = `
      <div class="toast-body d-flex align-items-center gap-3 py-3 px-4">
        ${icons[type] || icons.info}
        <span style="font-size:0.9rem;flex:1;">${message}</span>
        <button type="button" class="btn-close btn-close-white btn-sm" onclick="this.closest('.toast').remove()"></button>
      </div>
    `;
    this.container.appendChild(toast);

    setTimeout(() => {
      toast.classList.replace('animate__fadeInRight', 'animate__fadeOutRight');
      setTimeout(() => toast.remove(), 400);
    }, duration);
  },

  success: (msg, d) => TXToast.show(msg, 'success', d),
  error: (msg, d) => TXToast.show(msg, 'error', d),
  warning: (msg, d) => TXToast.show(msg, 'warning', d),
  info: (msg, d) => TXToast.show(msg, 'info', d),
};

window.TXToast = TXToast;

// ===== WISHLIST TOGGLE =====
async function toggleWishlist(packageId, btn) {
  try {
    btn.style.transform = 'scale(1.3)';
    setTimeout(() => btn.style.transform = '', 200);

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
      document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';

    const res = await fetch(`/tours/wishlist/toggle/${packageId}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' }
    });

    if (!res.ok) throw new Error('Not logged in');
    const data = await res.json();

    const icon = btn.querySelector('i');
    if (data.status === 'added') {
      btn.classList.add('active');
      if (icon) icon.className = 'bi bi-heart-fill';
      TXToast.success('Added to wishlist ❤️');
    } else {
      btn.classList.remove('active');
      if (icon) icon.className = 'bi bi-heart';
      TXToast.info('Removed from wishlist');
    }
  } catch (e) {
    TXToast.error('Please login to use wishlist');
    setTimeout(() => window.location.href = '/accounts/login/', 1500);
  }
}

// ===== PRICE CALCULATOR =====
const PriceCalc = {
  calculate(adultPrice, childPrice, numAdults, numChildren) {
    return (adultPrice * numAdults) + (childPrice * numChildren);
  },

  format(amount) {
    return '₹' + Math.round(amount).toLocaleString('en-IN');
  }
};

window.PriceCalc = PriceCalc;

// ===== IMAGE LAZY LOADING =====
(function initLazyLoad() {
  if ('IntersectionObserver' in window) {
    const imgObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          imgObserver.unobserve(img);
        }
      });
    }, { rootMargin: '100px' });

    document.querySelectorAll('img[data-src]').forEach(img => imgObserver.observe(img));
  }
})();

// ===== NAVBAR SCROLL EFFECT =====
(function initNavbar() {
  const nav = document.querySelector('.navbar-tx');
  if (!nav) return;

  let lastScroll = 0;

  window.addEventListener('scroll', () => {
    const currentScroll = window.scrollY;
    nav.classList.toggle('scrolled', currentScroll > 50);
    lastScroll = currentScroll;
  }, { passive: true });
})();

// ===== SMOOTH ANCHOR LINKS =====
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ===== FORM VALIDATION HELPER =====
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return true;

  let valid = true;
  form.querySelectorAll('[required]').forEach(field => {
    if (!field.value.trim()) {
      field.style.borderColor = 'var(--tx-coral)';
      valid = false;
    } else {
      field.style.borderColor = '';
    }
  });

  if (!valid) TXToast.error('Please fill in all required fields');
  return valid;
}

// ===== COPY TO CLIPBOARD =====
async function copyToClipboard(text, label = 'Copied!') {
  try {
    await navigator.clipboard.writeText(text);
    TXToast.success(`${label} ✓`);
  } catch {
    TXToast.error('Copy failed');
  }
}

// ===== LOADING BUTTON =====
function setLoadingBtn(btn, loading = true, originalText = null) {
  if (loading) {
    btn.dataset.original = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    btn.disabled = true;
  } else {
    btn.innerHTML = originalText || btn.dataset.original || 'Submit';
    btn.disabled = false;
  }
}

// ===== DEBOUNCE =====
function debounce(fn, delay = 300) {
  let timer;
    return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// ===== AUTO DISMISS TOASTS =====
document.querySelectorAll('.toast').forEach(toastEl => {
  try {
    const bsToast = new bootstrap.Toast(toastEl, { autohide: true, delay: 4500 });
    bsToast.show();
  } catch (e) {}
});

// ===== PARTICLE BACKGROUND =====
function createParticles(containerId, count = 25) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const colors = [
    'rgba(232,160,32,0.4)',
    'rgba(0,180,216,0.35)',
    'rgba(255,255,255,0.15)',
    'rgba(6,214,160,0.3)',
  ];

  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    const size = Math.random() * 4 + 1;
    p.style.cssText = `
      position:absolute;
      width:${size}px;
      height:${size}px;
      border-radius:50%;
      left:${Math.random() * 100}%;
      background:${colors[Math.floor(Math.random() * colors.length)]};
      animation:particle-float ${Math.random() * 15 + 8}s linear ${Math.random() * 10}s infinite;
      opacity:0;
    `;
    container.appendChild(p);
  }
}

// ===== RATING WIDGET =====
function initRatingWidget(containerId, inputName = 'rating') {
  const container = document.getElementById(containerId);
  if (!container) return;

  let currentRating = 0;

  const stars = container.querySelectorAll('label');
  stars.forEach((star, idx) => {
    star.addEventListener('mouseover', () => highlightStars(stars, stars.length - idx));
    star.addEventListener('mouseout', () => highlightStars(stars, currentRating));
    star.addEventListener('click', () => {
      currentRating = stars.length - idx;
      const input = container.querySelector(`input[value="${currentRating}"]`);
      if (input) input.checked = true;
    });
  });

  function highlightStars(stars, count) {
    stars.forEach((s, i) => {
      s.style.color = (stars.length - i) <= count ? 'var(--tx-gold)' : 'rgba(255,255,255,0.2)';
    });
  }
}

// ===== IMAGE GALLERY =====
function initGallery(mainId, thumbClass) {
  const main = document.getElementById(mainId);
  if (!main) return;

  document.querySelectorAll(`.${thumbClass}`).forEach(thumb => {
    thumb.addEventListener('click', function() {
      const imgSrc = this.querySelector('img')?.src;
      if (imgSrc && main.querySelector('img')) {
        main.querySelector('img').src = imgSrc;
        document.querySelectorAll(`.${thumbClass}`).forEach(t => t.classList.remove('active'));
        this.classList.add('active');
      }
    });
  });
}

// Export utilities
window.TXUtils = {
  toggleWishlist,
  copyToClipboard,
  setLoadingBtn,
  debounce,
  createParticles,
  initRatingWidget,
  initGallery,
  validateForm,
  PriceCalc,
};

console.log('%c✈️ TravelX Pro', 'color:#e8a020;font-size:20px;font-weight:bold;');
console.log('%cPowered by Django + Bootstrap 5', 'color:#00b4d8;font-size:12px;');
