'use strict';

/* ============================================================
   BADOING BADOING BADOING — main.js
   Shared JS for index.html, about.html, characters.html
   ============================================================ */

const REDUCED_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initActiveNavLink();
  initSmoothScroll();
  initScrollReveal();
  initGlassTilt();
  initParallax();
  initParticleCanvas();
  initBaDoingSounds();
  initBadoingTriggers();
});

/* ============================================================
   1. NAVIGATION — hamburger + mobile drawer
   ============================================================ */

function initNav() {
  const hamburger = (
    document.querySelector('.nav-toggle') ||
    document.querySelector('.nav-hamburger')
  );
  const drawer = (
    document.querySelector('.nav-mobile') ||
    document.querySelector('.nav-links-mobile') ||
    document.querySelector('.nav-menu')
  );
  if (!hamburger || !drawer) return;

  hamburger.setAttribute('aria-expanded', 'false');
  hamburger.setAttribute('aria-controls', 'nav-drawer');
  drawer.id = 'nav-drawer';
  drawer.setAttribute('role', 'navigation');
  drawer.setAttribute('aria-label', 'Mobile navigation');

  function openMenu() {
    hamburger.classList.add('open');
    drawer.classList.add('open');
    hamburger.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  function closeMenu() {
    hamburger.classList.remove('open');
    drawer.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  hamburger.addEventListener('click', () => {
    drawer.classList.contains('open') ? closeMenu() : openMenu();
  });

  drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));

  document.addEventListener('click', e => {
    if (
      drawer.classList.contains('open') &&
      !drawer.contains(e.target) &&
      !hamburger.contains(e.target)
    ) closeMenu();
  }, { passive: true });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && drawer.classList.contains('open')) {
      closeMenu();
      hamburger.focus();
    }
  });

  window.matchMedia('(min-width: 769px)').addEventListener('change', e => {
    if (e.matches) closeMenu();
  });
}

/* ============================================================
   2. ACTIVE NAV LINK — highlight current page
   ============================================================ */

function initActiveNavLink() {
  const filename = window.location.pathname.split('/').pop() || 'index.html';

  document.querySelectorAll('.nav-links a, .nav-links-mobile a, .nav-mobile a').forEach(a => {
    const href     = a.getAttribute('href') || '';
    const linkFile = href.split('/').pop() || 'index.html';
    if (linkFile === filename) {
      a.classList.add('active');
      a.setAttribute('aria-current', 'page');
    }
  });
}

/* ============================================================
   3. SMOOTH SCROLL — in-page anchor links
   ============================================================ */

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href').slice(1);
      if (!id) return;

      const target = document.getElementById(id);
      if (!target) return;

      e.preventDefault();

      const navH = parseFloat(
        getComputedStyle(document.documentElement).getPropertyValue('--nav-h')
      ) || 68;

      window.scrollTo({
        top: target.getBoundingClientRect().top + window.scrollY - navH - 16,
        behavior: 'smooth',
      });
    });
  });
}

/* ============================================================
   4. SCROLL REVEAL — IntersectionObserver adds .visible
   ============================================================ */

function initScrollReveal() {
  const items = document.querySelectorAll('[data-animate], .animate-in');
  if (!items.length) return;

  if (REDUCED_MOTION) {
    items.forEach(el => el.classList.add('visible'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('visible');
        obs.unobserve(entry.target);
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );

  items.forEach(el => observer.observe(el));
}

/* ============================================================
   5. GLASS TILT — mousemove rotateX/Y on .glass-panel
   ============================================================ */

function initGlassTilt() {
  if (REDUCED_MOTION) return;

  document.querySelectorAll('.glass-panel').forEach(panel => {
    panel.addEventListener('mousemove', e => {
      const rect = panel.getBoundingClientRect();
      const dx   = (e.clientX - rect.left - rect.width  / 2) / (rect.width  / 2);
      const dy   = (e.clientY - rect.top  - rect.height / 2) / (rect.height / 2);
      panel.style.transform =
        `perspective(600px) rotateX(${(-(dy * 8)).toFixed(2)}deg) rotateY(${(dx * 8).toFixed(2)}deg) translateY(-4px)`;
    });

    panel.addEventListener('mouseleave', () => {
      panel.style.transform = '';
    });
  });
}

/* ============================================================
   6. PARALLAX — hero layers shift on scroll
   ============================================================ */

function initParallax() {
  if (REDUCED_MOTION) return;

  const heroes = document.querySelectorAll('.hero, .hero-sub');
  if (!heroes.length) return;

  let ticking = false;

  function onScroll() {
    if (ticking) return;
    ticking = true;

    requestAnimationFrame(() => {
      const y = window.scrollY;

      heroes.forEach(hero => {
        const speed  = hero.classList.contains('hero-sub') ? 0.22 : 0.32;
        const offset = y * speed;

        const heroCanvas = hero.querySelector('.hero-canvas');
        if (heroCanvas) heroCanvas.style.transform = `translateY(${offset * 0.45}px)`;

        const content = hero.querySelector('.hero-content');
        if (content) content.style.transform = `translateY(${-offset * 0.1}px)`;
      });

      ticking = false;
    });
  }

  window.addEventListener('scroll', onScroll, { passive: true });
}

/* ============================================================
   7. PARTICLE CANVAS — drifting neon orbs on #particles
   ============================================================ */

function initParticleCanvas() {
  const canvas = document.getElementById('particles');
  if (!canvas || REDUCED_MOTION) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const COLORS = [
    '#bf00ff', // neon purple
    '#ff0090', // neon pink
    '#00cfff', // electric blue
    '#39ff14', // acid green
    '#ffe600', // yellow
    '#ff6a00', // orange
  ];

  const COUNT = 60;
  let W = 0, H = 0;
  let particles = [];
  let animId = null;

  const mouse = { x: -9999, y: -9999 };
  window.addEventListener('mousemove', e => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  }, { passive: true });
  window.addEventListener('mouseleave', () => {
    mouse.x = -9999;
    mouse.y = -9999;
  });

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function hexAlpha(hex, a) {
    const full = hex.replace(
      /^#([a-f\d])([a-f\d])([a-f\d])$/i,
      (_, r, g, b) => `#${r}${r}${g}${g}${b}${b}`
    );
    const n = parseInt(full.slice(1), 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a.toFixed(3)})`;
  }

  function makeParticle(scatterY = true) {
    const color  = COLORS[Math.floor(Math.random() * COLORS.length)];
    const radius = 2 + Math.random() * 5;
    return {
      x:          Math.random() * (W || window.innerWidth),
      y:          scatterY
                    ? Math.random() * (H || window.innerHeight)
                    : (H || window.innerHeight) + radius + Math.random() * 60,
      vx:         (Math.random() - 0.5) * 0.4,
      vy:         -(0.4 + Math.random() * 0.7),
      radius,
      color,
      alpha:      0.15 + Math.random() * 0.45,
      alphaDir:   Math.random() < 0.5 ? 1 : -1,
      alphaSpeed: 0.002 + Math.random() * 0.004,
      glowSize:   radius * (2.5 + Math.random() * 2),
      pulseSpeed: 0.006 + Math.random() * 0.014,
      pulsePhase: Math.random() * Math.PI * 2,
    };
  }

  function drawParticle(p, t) {
    const pulse = 1 + 0.18 * Math.sin(t * p.pulseSpeed + p.pulsePhase);
    const r     = p.radius   * pulse;
    const gR    = p.glowSize * pulse;

    ctx.save();

    const halo = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, gR);
    halo.addColorStop(0,    hexAlpha(p.color, p.alpha * 0.55));
    halo.addColorStop(0.45, hexAlpha(p.color, p.alpha * 0.18));
    halo.addColorStop(1,    hexAlpha(p.color, 0));
    ctx.beginPath();
    ctx.arc(p.x, p.y, gR, 0, Math.PI * 2);
    ctx.fillStyle = halo;
    ctx.fill();

    const core = ctx.createRadialGradient(
      p.x - r * 0.3, p.y - r * 0.3, r * 0.05,
      p.x,           p.y,           r
    );
    core.addColorStop(0,   hexAlpha('#ffffff', p.alpha * 0.85));
    core.addColorStop(0.4, hexAlpha(p.color,   p.alpha * 0.8));
    core.addColorStop(1,   hexAlpha(p.color,   p.alpha * 0.06));
    ctx.beginPath();
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.fillStyle = core;
    ctx.fill();

    ctx.restore();
  }

  function updateParticle(p) {
    p.x += p.vx;
    p.y += p.vy;

    p.alpha += p.alphaDir * p.alphaSpeed;
    if (p.alpha > 0.65 || p.alpha < 0.08) p.alphaDir *= -1;

    const dx    = p.x - mouse.x;
    const dy    = p.y - mouse.y;
    const dist2 = dx * dx + dy * dy;
    const REPEL = 110;
    if (dist2 < REPEL * REPEL && dist2 > 0) {
      const dist  = Math.sqrt(dist2);
      const force = ((REPEL - dist) / REPEL) * 0.75;
      p.x += (dx / dist) * force;
      p.y += (dy / dist) * force;
    }

    const buf = p.glowSize;
    if (p.x < -buf)    p.x = W + buf;
    if (p.x > W + buf) p.x = -buf;
    if (p.y < -buf * 2) return true; // signal: respawn at bottom
    return false;
  }

  function loop(t) {
    ctx.clearRect(0, 0, W, H);
    for (let i = 0; i < particles.length; i++) {
      if (updateParticle(particles[i])) particles[i] = makeParticle(false);
      drawParticle(particles[i], t);
    }
    animId = requestAnimationFrame(loop);
  }

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      cancelAnimationFrame(animId);
      animId = null;
    } else if (animId === null) {
      animId = requestAnimationFrame(loop);
    }
  });

  if (typeof ResizeObserver !== 'undefined') {
    new ResizeObserver(() => resize()).observe(canvas);
  } else {
    window.addEventListener('resize', resize, { passive: true });
  }

  resize();
  particles = Array.from({ length: COUNT }, () => makeParticle(true));
  animId = requestAnimationFrame(loop);
}

/* ============================================================
   8. BADOING SOUNDS — Web Audio boing on .badoing-trigger click
   ============================================================ */

function initBaDoingSounds() {
  let audioCtx = null;

  function getCtx() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    return audioCtx;
  }

  function playBoing() {
    const ctx = getCtx();
    const now = ctx.currentTime;

    // Primary sine: 400 → 100 Hz over 0.3 s
    const osc  = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(400, now);
    osc.frequency.exponentialRampToValueAtTime(100, now + 0.3);
    gain.gain.setValueAtTime(0.5, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.35);

    // Triangle harmonic: 800 → 200 Hz over 0.2 s (adds body/warmth)
    const osc2  = ctx.createOscillator();
    const gain2 = ctx.createGain();
    osc2.type = 'triangle';
    osc2.frequency.setValueAtTime(800, now);
    osc2.frequency.exponentialRampToValueAtTime(200, now + 0.2);
    gain2.gain.setValueAtTime(0.12, now);
    gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
    osc2.connect(gain2);
    gain2.connect(ctx.destination);
    osc2.start(now);
    osc2.stop(now + 0.22);
  }

  // Delegated — catches dynamically-added triggers too
  document.body.addEventListener('click', e => {
    if (e.target.closest('.badoing-trigger')) {
      try { playBoing(); } catch (_) {}
    }
  });
}

/* ============================================================
   9. BADOING TRIGGERS — random springy visual animation bursts
   ============================================================ */

function initBadoingTriggers() {
  if (REDUCED_MOTION) return;

  const triggers = Array.from(document.querySelectorAll('.badoing-trigger'));
  if (!triggers.length) return;

  let timeoutId = null;

  function fireBadoing() {
    const el = triggers[Math.floor(Math.random() * triggers.length)];
    el.classList.remove('doing');
    void el.offsetWidth; // force reflow to restart animation
    el.classList.add('doing');
    el.addEventListener('animationend', () => el.classList.remove('doing'), { once: true });
    timeoutId = setTimeout(fireBadoing, 2500 + Math.random() * 3500);
  }

  timeoutId = setTimeout(fireBadoing, 1800);

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      clearTimeout(timeoutId);
      timeoutId = null;
    } else {
      timeoutId = setTimeout(fireBadoing, 1000);
    }
  });
}
