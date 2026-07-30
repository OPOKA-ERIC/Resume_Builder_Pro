// Resume Builder Pro - Enhanced JavaScript

// === Global Functions ===

// Password toggle (used across auth pages)
function togglePassword(button) {
    var wrap = button.closest('.input-group-icon') || button.closest('.afp-input-wrap');
    if (!wrap) return;
    var input = wrap.querySelector('input');
    if (!input) return;
    var svg = button.querySelector('svg');
    if (input.type === 'password') {
        input.type = 'text';
        if (svg) svg.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';
    } else {
        input.type = 'password';
        if (svg) svg.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
    }
}

// Templates Gallery: dynamically measure and scale iframe to fit container
function scaleTemplateIframe(iframe) {
    try {
        var doc = iframe.contentDocument || iframe.contentWindow.document;
        if (!doc) return false;
        var body = doc.body;
        var html = doc.documentElement;
        if (!body || !html) return false;

        var pageW = body.scrollWidth || html.scrollWidth || 794;
        var pageH = body.scrollHeight || html.scrollHeight || 1123;
        if (pageW === 0 || pageH === 0) return false;

        var container = iframe.closest('.template-paper');
        if (!container) return false;
        var cw = container.offsetWidth;
        var ch = container.offsetHeight;
        if (cw === 0 || ch === 0) return false;

        var scale = Math.min(cw / pageW, 1);

        // Keep iframe at fixed viewport (CSS: 794x1123) — only apply transform
        iframe.style.transform = 'scale(' + scale + ')';
        iframe.style.transformOrigin = 'top left';
        iframe.style.left = ((cw - pageW * scale) / 2) + 'px';
        iframe.style.top = ((ch - pageH * scale) / 2) + 'px';
        iframe.style.position = 'absolute';
        return true;
    } catch (e) {
        return false;
    }
}

function scaleTemplateIframes() {
    document.querySelectorAll('.template-iframe').forEach(function (iframe) {
        if (iframe.__scaled) return;
        if (scaleTemplateIframe(iframe)) {
            iframe.__scaled = true;
        }
    });
}

function setupIframeScaling() {
    document.querySelectorAll('.template-iframe').forEach(function (iframe) {
        if (iframe.__listening) return;
        iframe.__listening = true;
        if (iframe.contentDocument && iframe.contentDocument.readyState === 'complete') {
            scaleTemplateIframe(iframe);
            iframe.__scaled = true;
        } else {
            iframe.addEventListener('load', function onLoad() {
                scaleTemplateIframe(iframe);
                iframe.__scaled = true;
            });
        }
    });
}

// Templates Gallery: search & sort
function initGalleryControls() {
    var searchInput = document.getElementById('gallerySearch');
    var sortSelect = document.getElementById('gallerySort');
    var grid = document.getElementById('templateGrid');
    var countEl = document.getElementById('galleryCount');
    if (!grid) return;

    var cards = Array.from(grid.querySelectorAll('.template-card'));
    var originalOrder = cards.slice();

    function filterAndSort() {
        var query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        var sortVal = sortSelect ? sortSelect.value : 'default';

        cards.forEach(function (card) {
            var name = card.getAttribute('data-name') || '';
            var tags = card.getAttribute('data-tags') || '';
            card.style.display = (!query || name.indexOf(query) !== -1 || tags.indexOf(query) !== -1) ? '' : 'none';
        });

        var visible = cards.filter(function (c) { return c.style.display !== 'none'; });

        if (sortVal === 'name') {
            visible.sort(function (a, b) {
                return (a.getAttribute('data-name') || '').localeCompare(b.getAttribute('data-name') || '');
            });
        } else if (sortVal === 'name-desc') {
            visible.sort(function (a, b) {
                return (b.getAttribute('data-name') || '').localeCompare(a.getAttribute('data-name') || '');
            });
        } else {
            visible.sort(function (a, b) { return originalOrder.indexOf(a) - originalOrder.indexOf(b); });
        }

        visible.forEach(function (card) { grid.appendChild(card); });

        if (countEl) {
            var total = cards.length;
            var shown = visible.length;
            countEl.textContent = shown + ' template' + (shown !== 1 ? 's' : '') + (shown < total ? ' (' + total + ' total)' : '');
        }

        requestAnimationFrame(setupIframeScaling);
    }

    if (searchInput) searchInput.addEventListener('input', filterAndSort);
    if (sortSelect) sortSelect.addEventListener('change', filterAndSort);
}

// === DOM Ready ===
document.addEventListener('DOMContentLoaded', function () {

    // Auto-dismiss alerts
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (a) {
        setTimeout(function () {
            var bs = bootstrap.Alert.getOrCreateInstance(a);
            bs.close();
        }, 5000);
    });

    // Back to Top
    var backToTop = document.getElementById('backToTop');
    if (backToTop) {
        window.addEventListener('scroll', function () {
            backToTop.classList.toggle('visible', window.scrollY > 300);
        });
        backToTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
    }

    // Navbar scroll effect
    var mainNav = document.getElementById('mainNav');
    if (mainNav) {
        window.addEventListener('scroll', function () {
            mainNav.classList.toggle('scrolled', window.scrollY > 50);
        });
    }

    // Form field focus
    document.querySelectorAll('.form-control, .form-select').forEach(function (input) {
        input.addEventListener('focus', function () { this.parentElement.classList.add('field-focused'); });
        input.addEventListener('blur', function () { this.parentElement.classList.remove('field-focused'); });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Scroll reveal
    if ('IntersectionObserver' in window) {
        var revealObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });
        document.querySelectorAll('.reveal, .stat-reveal').forEach(function (el) { revealObserver.observe(el); });
    }

    // Counter animation
    var counters = document.querySelectorAll('.stat-counter');
    if (counters.length > 0 && 'IntersectionObserver' in window) {
        var counterObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var el = entry.target;
                    var target = parseInt(el.getAttribute('data-target'), 10);
                    var suffix = el.getAttribute('data-suffix') || '';
                    var duration = 2000;
                    var startTime = performance.now();
                    var useKFormat = target >= 1000;

                    function easeOutExpo(t) { return t === 1 ? 1 : 1 - Math.pow(2, -10 * t); }

                    function formatCount(v) {
                        return useKFormat ? (v / 1000).toFixed(v >= 10000 ? 0 : 1) + 'K+' : v + suffix;
                    }

                    function updateCounter(currentTime) {
                        var elapsed = currentTime - startTime;
                        var progress = Math.min(elapsed / duration, 1);
                        var current = Math.round(easeOutExpo(progress) * target);
                        el.textContent = formatCount(current);
                        if (progress < 1) requestAnimationFrame(updateCounter);
                    }

                    requestAnimationFrame(updateCounter);
                    counterObserver.unobserve(el);
                }
            });
        }, { threshold: 0.5 });
        counters.forEach(function (c) { counterObserver.observe(c); });
    }

    // Typewriter effect
    (function () {
        var el = document.querySelector('.typewriter-cursor');
        if (!el || !el.parentElement) return;
        var phrases = ['Minutes.', 'No Design Skills Needed.', 'For Free.', 'Like a Pro.'];
        var idx = 0, ci = 0, del = false;
        var target = el.parentElement;
        function tick() {
            var cur = phrases[idx];
            if (del) { ci--; if (ci < 0) { del = false; idx = (idx + 1) % phrases.length; setTimeout(tick, 400); return; } }
            else { ci++; if (ci > cur.length) { del = true; setTimeout(tick, 2000); return; } }
            var cursorHtml = el.outerHTML;
            target.innerHTML = cur.substring(0, ci) + cursorHtml;
            setTimeout(tick, del ? 50 : 100);
        }
        tick();
    })();

    // Wizard form validation
    (function () {
        var form = document.querySelector('.wizard-form');
        if (!form) return;
        form.addEventListener('submit', function (e) {
            var valid = true;
            form.querySelectorAll('[required]').forEach(function (f) {
                var err = f.parentNode.querySelector('.field-error');
                if (err) err.remove();
                if (!f.value.trim()) {
                    valid = false;
                    f.classList.add('is-invalid');
                    var d = document.createElement('div');
                    d.className = 'text-danger small field-error';
                    d.textContent = 'This field is required.';
                    f.parentNode.appendChild(d);
                } else { f.classList.remove('is-invalid'); }
            });
            if (!valid) e.preventDefault();
        });
    })();

    // Confirm before leaving wizard
    (function () {
        var changed = false;
        document.querySelectorAll('.wizard-form, .section-edit-form').forEach(function (f) {
            f.addEventListener('change', function () { changed = true; });
            f.addEventListener('submit', function () { changed = false; });
        });
        window.addEventListener('beforeunload', function (e) {
            if (changed) { e.preventDefault(); e.returnValue = ''; }
        });
    })();

    // Progress bar
    (function () {
        var pb = document.querySelector('.progress-bar');
        if (pb) { var w = pb.style.width; pb.style.width = '0%'; setTimeout(function () { pb.style.width = w; }, 100); }
    })();

    // Animate elements on scroll (legacy)
    if ('IntersectionObserver' in window) {
        var animEls = document.querySelectorAll('.animate-fade-in-up, .animate-fade-in, .animate-slide-right, .animate-slide-left');
        var animObs = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (e.isIntersecting) { e.target.style.animationPlayState = 'running'; animObs.unobserve(e.target); }
            });
        }, { threshold: 0.1 });
        animEls.forEach(function (el) { el.style.animationPlayState = 'paused'; animObs.observe(el); });
    }

    // Landing page navbar glass effect
    var landingNav = document.querySelector('.landing-page .navbar-main');
    if (landingNav) {
        function handleScroll() { landingNav.classList.toggle('scrolled', window.scrollY > 50); }
        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll();
    }

    // Templates Gallery init
    setupIframeScaling();
    initGalleryControls();
    window.addEventListener('resize', setupIframeScaling);

});
