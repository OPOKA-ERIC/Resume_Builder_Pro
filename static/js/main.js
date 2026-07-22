// Resume Builder Pro - Enhanced JavaScript

document.addEventListener('DOMContentLoaded', function () {

    // === Auto-dismiss alerts after 5 seconds ===
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // === Back to Top button ===
    const backToTop = document.getElementById('backToTop');
    if (backToTop) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });
        backToTop.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // === Navbar scroll effect ===
    const mainNav = document.getElementById('mainNav');
    if (mainNav) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                mainNav.classList.add('scrolled');
            } else {
                mainNav.classList.remove('scrolled');
            }
        });
    }

    // === Form field focus animations ===
    const formControls = document.querySelectorAll('.form-control, .form-select');
    formControls.forEach(function (input) {
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('field-focused');
        });
        input.addEventListener('blur', function () {
            this.parentElement.classList.remove('field-focused');
        });
    });

    // === Smooth scroll for anchor links ===
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // === Animate elements on scroll (IntersectionObserver) ===
    const animateElements = document.querySelectorAll('.animate-fade-in-up, .animate-fade-in, .animate-slide-right, .animate-slide-left');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animateElements.forEach(function (el) {
            el.style.animationPlayState = 'paused';
            observer.observe(el);
        });
    }

    // === Typewriter effect for hero subtitle ===
    const typewriterEl = document.querySelector('.typewriter-cursor');
    if (typewriterEl && typewriterEl.parentElement) {
        const phrases = [
            'Minutes.',
            'No Design Skills Needed.',
            'For Free.',
            'Like a Pro.'
        ];
        let phraseIdx = 0;
        let charIdx = 0;
        let isDeleting = false;
        const typeTarget = typewriterEl.parentElement;

        function typeEffect() {
            const current = phrases[phraseIdx];
            if (isDeleting) {
                charIdx--;
                if (charIdx < 0) {
                    isDeleting = false;
                    phraseIdx = (phraseIdx + 1) % phrases.length;
                    setTimeout(typeEffect, 400);
                    return;
                }
            } else {
                charIdx++;
                if (charIdx > current.length) {
                    isDeleting = true;
                    setTimeout(typeEffect, 2000);
                    return;
                }
            }
            // Find or create a text node before the cursor
            let textNode = null;
            for (const node of typeTarget.childNodes) {
                if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                    textNode = node;
                    break;
                }
            }
            // Rebuild the inner HTML: text + cursor span
            const text = current.substring(0, charIdx);
            const cursorHtml = typewriterEl.outerHTML;
            typeTarget.innerHTML = text + cursorHtml;
            setTimeout(typeEffect, isDeleting ? 50 : 100);
        }
        typeEffect();
    }

    // === Counter animation for stats ===
    const counters = document.querySelectorAll('.stat-number[data-count]');
    if (counters.length > 0 && 'IntersectionObserver' in window) {
        const counterObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const target = parseInt(el.getAttribute('data-count'), 10);
                    let current = 0;
                    const duration = 2000;
                    const step = Math.max(1, Math.floor(target / (duration / 16)));
                    const timer = setInterval(function () {
                        current += step;
                        if (current >= target) {
                            current = target;
                            clearInterval(timer);
                        }
                        el.textContent = current.toLocaleString() + (target === 100 ? '' : '+');
                    }, 16);
                    counterObserver.unobserve(el);
                }
            });
        }, { threshold: 0.5 });
        counters.forEach(function (c) { counterObserver.observe(c); });
    }
});

// === Password toggle function (global) ===
function togglePassword(button) {
    const input = button.closest('.input-group-icon').querySelector('input');
    const icon = button.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
}
