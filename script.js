/* ============================================================
   SUGAR DREAM – JAVASCRIPT
   ============================================================ */

/* ---- Loader ---- */
window.addEventListener('load', () => {
  setTimeout(() => {
    document.getElementById('loader').classList.add('hidden');
    startCounters();
    revealVisible();
  }, 1600);
});

/* ---- Navbar scroll ---- */
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
  updateActiveNav();
});

/* ---- Hamburger ---- */
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');
hamburger.addEventListener('click', () => {
  navLinks.classList.toggle('open');
});
navLinks.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', () => navLinks.classList.remove('open'));
});

/* ---- Active Nav on scroll ---- */
function updateActiveNav() {
  const sections = ['home','sweets','specials','about','testimonials','contact'];
  let current = 'home';
  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      const rect = el.getBoundingClientRect();
      if (rect.top <= 120) current = id;
    }
  });
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.toggle('active', link.getAttribute('href') === '#' + current);
  });
}

/* ---- Hero word cycle ---- */
const words = ['Sweet','Magical','Blissful','Joyful','Dreamy','Delicious'];
let wordIdx = 0;
const cycleEl = document.getElementById('cycleWord');
setInterval(() => {
  wordIdx = (wordIdx + 1) % words.length;
  cycleEl.style.opacity = '0';
  cycleEl.style.transform = 'translateY(-10px)';
  setTimeout(() => {
    cycleEl.textContent = words[wordIdx];
    cycleEl.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    cycleEl.style.opacity   = '1';
    cycleEl.style.transform = 'translateY(0)';
  }, 400);
}, 2200);

/* ---- Reveal on scroll ---- */
function revealVisible() {
  const elements = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right, .reveal-card');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, entry.target.classList.contains('reveal-card') ? (i % 4) * 100 : 0);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });
  elements.forEach(el => observer.observe(el));
}

/* ---- Animated counters ---- */
function startCounters() {
  document.querySelectorAll('.stat-num').forEach(el => {
    const target = parseInt(el.dataset.target, 10);
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = Math.floor(current).toLocaleString();
    }, 16);
  });
}

/* ---- Filter tabs ---- */
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.dataset.filter;
    document.querySelectorAll('.sweet-card').forEach(card => {
      const match = filter === 'all' || card.dataset.category === filter;
      card.classList.toggle('hidden', !match);
      if (match) {
        card.style.animation = 'none';
        card.offsetHeight; // reflow
        card.style.animation = 'filterReveal 0.4s ease forwards';
      }
    });
  });
});

// Add filter animation keyframe dynamically
const filterStyle = document.createElement('style');
filterStyle.textContent = `
  @keyframes filterReveal {
    from { opacity: 0; transform: scale(0.9) translateY(10px); }
    to   { opacity: 1; transform: scale(1)   translateY(0); }
  }
`;
document.head.appendChild(filterStyle);

/* ---- Add to cart ---- */
const cartToast = document.getElementById('cartToast');
const cartToastMsg = document.getElementById('cartToastMsg');
let cartTimeout;
document.querySelectorAll('.card-add').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    const card = btn.closest('.sweet-card');
    const name = card.querySelector('h3').textContent;
    cartToastMsg.textContent = `"${name}" added to cart!`;
    cartToast.classList.add('show');
    clearTimeout(cartTimeout);
    cartTimeout = setTimeout(() => cartToast.classList.remove('show'), 3000);
    // Burst animation on button
    btn.textContent = '✓';
    btn.style.background = '#22c55e';
    setTimeout(() => { btn.textContent = '+'; btn.style.background = ''; }, 1200);
  });
});

/* ---- Testimonial auto-scroll ---- */
const track = document.getElementById('testimonialsTrack');
const dotsContainer = document.getElementById('testimonialDots');
const cards = track.querySelectorAll('.testimonial-card');
let activeCardIdx = 0;

cards.forEach((_, i) => {
  const dot = document.createElement('button');
  dot.className = 'tdot' + (i === 0 ? ' active' : '');
  dot.setAttribute('aria-label', `Go to testimonial ${i + 1}`);
  dot.addEventListener('click', () => scrollToCard(i));
  dotsContainer.appendChild(dot);
});

function scrollToCard(idx) {
  activeCardIdx = idx;
  const card = cards[idx];
  track.scrollTo({ left: card.offsetLeft - 24, behavior: 'smooth' });
  dotsContainer.querySelectorAll('.tdot').forEach((d, i) => d.classList.toggle('active', i === idx));
}

// Auto-advance
let autoTestimonial = setInterval(() => {
  activeCardIdx = (activeCardIdx + 1) % cards.length;
  scrollToCard(activeCardIdx);
}, 4000);
track.addEventListener('mouseenter', () => clearInterval(autoTestimonial));
track.addEventListener('mouseleave', () => {
  autoTestimonial = setInterval(() => {
    activeCardIdx = (activeCardIdx + 1) % cards.length;
    scrollToCard(activeCardIdx);
  }, 4000);
});

/* ---- Order form ---- */
document.getElementById('orderForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const btn = document.getElementById('orderSubmitBtn');
  btn.querySelector('span').textContent = 'Sending…';
  btn.disabled = true;
  setTimeout(() => {
    document.getElementById('formSuccess').classList.add('show');
    btn.querySelector('span').textContent = 'Order Sent! 🎉';
    btn.style.background = '#22c55e';
    document.getElementById('orderForm').reset();
    setTimeout(() => {
      btn.querySelector('span').textContent = 'Send Sweet Order 🍬';
      btn.disabled = false;
      btn.style.background = '';
      document.getElementById('formSuccess').classList.remove('show');
    }, 5000);
  }, 1500);
});

/* ---- Newsletter form ---- */
document.getElementById('newsletterForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const btn = document.getElementById('newsletterBtn');
  btn.textContent = '✓';
  btn.style.background = '#22c55e';
  document.getElementById('newsletterEmail').value = '';
  setTimeout(() => {
    btn.textContent = '🍬';
    btn.style.background = '';
  }, 2000);
});

/* ---- Candy Canvas Particle Rain ---- */
const canvas = document.getElementById('candyCanvas');
const ctx    = canvas.getContext('2d');
const EMOJIS = ['🍬','🍫','🍭','🍩','🧁','🍮','🍪','⭐','🌟','✨'];
let W, H, particles = [];

function resizeCanvas() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

class Candy {
  constructor() { this.reset(true); }
  reset(initial = false) {
    this.x     = Math.random() * W;
    this.y     = initial ? Math.random() * H : -60;
    this.size  = Math.random() * 18 + 14;
    this.speed = Math.random() * 1.2 + 0.4;
    this.drift = (Math.random() - 0.5) * 0.8;
    this.rot   = Math.random() * Math.PI * 2;
    this.rotV  = (Math.random() - 0.5) * 0.04;
    this.emoji = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
    this.alpha = Math.random() * 0.5 + 0.2;
  }
  update() {
    this.y   += this.speed;
    this.x   += this.drift;
    this.rot += this.rotV;
    if (this.y > H + 60) this.reset();
  }
  draw() {
    ctx.save();
    ctx.globalAlpha = this.alpha;
    ctx.translate(this.x, this.y);
    ctx.rotate(this.rot);
    ctx.font = `${this.size}px serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(this.emoji, 0, 0);
    ctx.restore();
  }
}

for (let i = 0; i < 60; i++) particles.push(new Candy());

function animateCanvas() {
  ctx.clearRect(0, 0, W, H);
  particles.forEach(p => { p.update(); p.draw(); });
  requestAnimationFrame(animateCanvas);
}
animateCanvas();

/* ---- Parallax hero decoration ---- */
document.addEventListener('mousemove', (e) => {
  const { clientX: x, clientY: y } = e;
  const cx = W / 2, cy = H / 2;
  const dx = (x - cx) / cx;
  const dy = (y - cy) / cy;
  document.querySelectorAll('.fs').forEach((el, i) => {
    const depth = (i % 3 + 1) * 6;
    el.style.transform = `translate(${dx * depth}px, ${dy * depth}px)`;
  });
});

/* ---- Smooth scroll for anchor links ---- */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = 80;
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

/* ---- Card tilt effect ---- */
document.querySelectorAll('.sweet-card, .special-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width  / 2;
    const y = e.clientY - rect.top  - rect.height / 2;
    card.style.transform = `translateY(-8px) rotateX(${-y / 20}deg) rotateY(${x / 20}deg)`;
    card.style.transition = 'transform 0.1s';
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
    card.style.transition = 'all 0.4s cubic-bezier(0.25,0.8,0.25,1)';
  });
});
