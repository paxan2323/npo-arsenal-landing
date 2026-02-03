/**
 * Птицелов — Main JavaScript
 * Интерактивность для лендинга
 */

/**
 * Get CSRF token from cookie (Django)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Preloader
    initPreloader();
    
    // Initialize AOS (Animate On Scroll)
    AOS.init({
        duration: 800,
        easing: 'ease-out-cubic',
        once: true,
        offset: 50,
        disable: 'mobile'
    });

    // Initialize GLightbox for gallery
    const lightbox = GLightbox({
        selector: '.glightbox',
        touchNavigation: true,
        loop: true,
        closeButton: true
    });

    // Mobile Navigation Toggle
    initMobileNav();

    // Smooth Scroll for anchor links
    initSmoothScroll();

    // Navbar scroll effect
    initNavbarScroll();

    // Document Filter
    initDocumentFilter();

    // Contact Form
    initContactForm();

    // Typing effect for terminal (optional enhancement)
    initTerminalEffect();
    
    // UX Enhancements
    initScrollProgress();
    initBackToTop();
    initFloatingContact();
    initSectionReveal();
    initActiveNavigation();
    initImageLazyLoad();
    initRealTimeValidation();
    
    // Cookie Banner
    initCookieBanner();
});

/**
 * Mobile Navigation
 */
function initMobileNav() {
    const toggle = document.getElementById('navToggle');
    const menu = document.getElementById('navMenu');

    if (!toggle || !menu) return;

    toggle.addEventListener('click', function() {
        toggle.classList.toggle('active');
        menu.classList.toggle('active');
    });

    // Close menu on link click
    menu.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            toggle.classList.remove('active');
            menu.classList.remove('active');
        });
    });

    // Close menu on outside click
    document.addEventListener('click', function(e) {
        if (!toggle.contains(e.target) && !menu.contains(e.target)) {
            toggle.classList.remove('active');
            menu.classList.remove('active');
        }
    });
}

/**
 * Smooth Scroll
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;

            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Navbar Scroll Effect
 */
function initNavbarScroll() {
    const nav = document.getElementById('nav');
    if (!nav) return;

    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        // Add/remove scrolled class
        if (currentScroll > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }

        // Hide/show on scroll direction (optional)
        if (currentScroll > lastScroll && currentScroll > 200) {
            nav.style.transform = 'translateY(-100%)';
        } else {
            nav.style.transform = 'translateY(0)';
        }
        lastScroll = currentScroll;
    });
}

/**
 * Document Category Filter
 */
function initDocumentFilter() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const docCards = document.querySelectorAll('.doc-card');

    if (!filterBtns.length || !docCards.length) return;

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const category = this.dataset.category;

            // Update active button
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Filter documents
            docCards.forEach(card => {
                if (category === 'all' || card.dataset.category === category) {
                    card.classList.remove('hidden');
                    card.style.animation = 'fadeIn 0.3s ease forwards';
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });
}

/**
 * Contact Form Handler
 */
let smartCaptchaWidgetId = null;
let smartCaptchaToken = '';

function initSmartCaptcha() {
    const captchaContainer = document.getElementById('captcha-container');
    
    if (!captchaContainer || !window.smartCaptcha) return;
    
    const sitekey = captchaContainer.getAttribute('data-sitekey');
    if (sitekey && smartCaptchaWidgetId === null) {
        try {
            smartCaptchaWidgetId = window.smartCaptcha.render(captchaContainer, {
                sitekey: sitekey,
                callback: function(token) {
                    smartCaptchaToken = token;
                    // Clear any captcha errors when solved
                    const errorEl = document.querySelector('.captcha-error');
                    if (errorEl) errorEl.remove();
                }
            });
        } catch (e) {
            console.log('SmartCaptcha already rendered or error:', e);
        }
    }
}

// SmartCaptcha callback when script loads
window.smartCaptchaOnLoad = function() {
    initSmartCaptcha();
};

function initContactForm() {
    const form = document.getElementById('contactForm');
    const successMessage = document.getElementById('formSuccess');

    if (!form) return;
    
    // Try to initialize SmartCaptcha (may already be loaded)
    if (window.smartCaptcha) {
        initSmartCaptcha();
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Check if SmartCaptcha token exists
        if (smartCaptchaWidgetId !== null && !smartCaptchaToken) {
            showCaptchaError('Пожалуйста, пройдите проверку капчи');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Disable button and show loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <span>Отправка...</span>
            <svg class="spinner" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
            </svg>
        `;

        try {
            const formData = new FormData(form);
            
            // Add captcha token to form data
            if (smartCaptchaToken) {
                formData.append('smart-token', smartCaptchaToken);
            }
            
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                // Show success message
                form.style.display = 'none';
                successMessage.style.display = 'block';
                
                // Animate success icon
                successMessage.querySelector('.success-icon').style.animation = 'scaleIn 0.5s ease forwards';
                
                // Show toast notification
                showToast('Заявка успешно отправлена!', 'success');
            } else {
                // Show errors
                showFormErrors(data.errors);
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                
                // Reset captcha if error
                if (window.smartCaptcha && smartCaptchaWidgetId !== null) {
                    window.smartCaptcha.reset(smartCaptchaWidgetId);
                    smartCaptchaToken = '';
                }
            }
        } catch (error) {
            console.error('Form submission error:', error);
            showToast('Произошла ошибка при отправке. Пожалуйста, попробуйте позже.', 'error');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            
            // Reset captcha on error
            if (window.smartCaptcha && smartCaptchaWidgetId !== null) {
                window.smartCaptcha.reset(smartCaptchaWidgetId);
                smartCaptchaToken = '';
            }
        }
    });
}

/**
 * Show Captcha Error
 */
function showCaptchaError(message) {
    const captchaContainer = document.querySelector('.captcha-container');
    if (!captchaContainer) return;
    
    // Remove existing error
    const existingError = captchaContainer.querySelector('.captcha-error');
    if (existingError) existingError.remove();
    
    // Add error message
    const errorEl = document.createElement('div');
    errorEl.className = 'captcha-error form-error';
    errorEl.textContent = message;
    captchaContainer.appendChild(errorEl);
    
    // Shake animation
    captchaContainer.style.animation = 'shake 0.5s ease';
    setTimeout(() => {
        captchaContainer.style.animation = '';
    }, 500);
}

/**
 * Show Form Errors
 */
function showFormErrors(errors) {
    // Clear previous errors
    document.querySelectorAll('.form-error').forEach(el => el.remove());
    document.querySelectorAll('.form-input.error').forEach(el => el.classList.remove('error'));

    // Show new errors
    for (const [field, messages] of Object.entries(errors)) {
        const input = document.querySelector(`[name="${field}"]`);
        if (input) {
            input.classList.add('error');
            const errorEl = document.createElement('span');
            errorEl.className = 'form-error';
            errorEl.textContent = messages[0];
            input.parentNode.appendChild(errorEl);
        }
    }
}

/**
 * Terminal Typing Effect
 */
function initTerminalEffect() {
    const terminal = document.querySelector('.terminal-body');
    if (!terminal) return;

    // Add cursor blink effect to last spec value
    const specValues = terminal.querySelectorAll('.spec-value');
    if (specValues.length > 0) {
        const lastValue = specValues[specValues.length - 1];
        lastValue.classList.add('cursor-blink');
    }
}

/**
 * Add CSS animation keyframes dynamically
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes scaleIn {
        from { transform: scale(0); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .spinner {
        animation: spin 1s linear infinite;
    }
    
    .cursor-blink::after {
        content: '_';
        animation: blink 1s step-end infinite;
    }
    
    @keyframes blink {
        50% { opacity: 0; }
    }
    
    .form-input.error {
        border-color: var(--color-danger) !important;
    }
    
    .form-error {
        display: block;
        color: var(--color-danger);
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }
    
    .nav {
        transition: transform 0.3s ease, background 0.3s ease;
    }
    
    .nav.scrolled {
        background: rgba(10, 14, 20, 0.95);
    }
`;
document.head.appendChild(style);

/**
 * Intersection Observer for animations
 */
function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Counter Animation for Stats
 */
function animateCounters() {
    const counters = document.querySelectorAll('.stat-value');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace(/[^0-9]/g, ''));
        if (isNaN(target)) return;
        
        let current = 0;
        const increment = target / 50;
        const duration = 1500;
        const stepTime = duration / 50;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.floor(current);
                setTimeout(updateCounter, stepTime);
            } else {
                counter.textContent = target;
            }
        };
        
        // Start animation when element is in view
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                updateCounter();
                observer.disconnect();
            }
        });
        
        observer.observe(counter);
    });
}

// Initialize counter animation
document.addEventListener('DOMContentLoaded', animateCounters);

/**
 * Preloader Handler
 */
function initPreloader() {
    const preloader = document.querySelector('.preloader');
    if (!preloader) return;
    
    // Animate progress bar
    const progressBar = preloader.querySelector('.preloader-progress-bar');
    if (progressBar) {
        progressBar.style.width = '100%';
    }
    
    // Hide preloader when page is fully loaded
    window.addEventListener('load', function() {
        setTimeout(() => {
            preloader.classList.add('hidden');
            // Enable scroll after preloader hides
            document.body.style.overflow = '';
        }, 500);
    });
    
    // Fallback: hide preloader after 3 seconds anyway
    setTimeout(() => {
        preloader.classList.add('hidden');
        document.body.style.overflow = '';
    }, 3000);
}

/**
 * Scroll Progress Indicator
 */
function initScrollProgress() {
    const progressBar = document.querySelector('.scroll-progress');
    if (!progressBar) return;
    
    window.addEventListener('scroll', () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        
        progressBar.style.width = scrollPercent + '%';
    });
}

/**
 * Back to Top Button
 */
function initBackToTop() {
    const btn = document.querySelector('.back-to-top');
    if (!btn) return;
    
    // Show/hide based on scroll position
    window.addEventListener('scroll', () => {
        if (window.scrollY > 500) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    });
    
    // Scroll to top on click
    btn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Floating Contact Menu
 */
function initFloatingContact() {
    const toggle = document.getElementById('floatingToggle');
    const menu = document.getElementById('floatingContact');
    
    if (!toggle || !menu) return;
    
    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.classList.toggle('active');
    });
    
    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!menu.contains(e.target)) {
            menu.classList.remove('active');
        }
    });
    
    // Hide when scrolling to contact section
    const contactSection = document.getElementById('contacts');
    if (contactSection) {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                menu.style.opacity = '0.3';
                menu.style.pointerEvents = 'none';
            } else {
                menu.style.opacity = '1';
                menu.style.pointerEvents = 'auto';
            }
        }, { threshold: 0.5 });
        
        observer.observe(contactSection);
    }
}

/**
 * Section Reveal on Scroll
 */
function initSectionReveal() {
    const sections = document.querySelectorAll('.section');
    
    const observerOptions = {
        root: null,
        rootMargin: '-50px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    sections.forEach(section => {
        observer.observe(section);
    });
}

/**
 * Active Navigation Highlighting
 */
function initActiveNavigation() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    if (!sections.length || !navLinks.length) return;
    
    const observerOptions = {
        root: null,
        rootMargin: '-30% 0px -70% 0px',
        threshold: 0
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === '#' + id) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, observerOptions);
    
    sections.forEach(section => {
        observer.observe(section);
    });
}

/**
 * Lazy Load Images with Fade Effect
 */
function initImageLazyLoad() {
    const images = document.querySelectorAll('.gallery-item img, .about-image img');
    
    images.forEach(img => {
        // Add skeleton class while loading
        if (!img.complete) {
            img.parentElement.classList.add('skeleton');
        }
        
        img.addEventListener('load', function() {
            this.classList.add('loaded');
            this.parentElement.classList.remove('skeleton');
        });
        
        // If already loaded (from cache)
        if (img.complete) {
            img.classList.add('loaded');
        }
    });
}

/**
 * Real-time Form Validation
 */
function initRealTimeValidation() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, textarea');
    
    inputs.forEach(input => {
        // Validate on blur
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        // Clear error on input
        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                this.classList.remove('error');
                const errorEl = this.parentNode.querySelector('.form-error');
                if (errorEl) errorEl.remove();
            }
        });
    });
    
    // Phone number formatting
    const phoneInput = form.querySelector('[name="phone"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            // Format as +7 (XXX) XXX-XX-XX
            if (value.length > 0) {
                if (value[0] === '8') value = '7' + value.slice(1);
                if (value[0] !== '7') value = '7' + value;
                
                let formatted = '+7';
                if (value.length > 1) {
                    formatted += ' (' + value.substring(1, 4);
                }
                if (value.length > 4) {
                    formatted += ') ' + value.substring(4, 7);
                }
                if (value.length > 7) {
                    formatted += '-' + value.substring(7, 9);
                }
                if (value.length > 9) {
                    formatted += '-' + value.substring(9, 11);
                }
                
                e.target.value = formatted;
            }
        });
    }
}

/**
 * Validate Single Field
 */
function validateField(input) {
    const value = input.value.trim();
    const name = input.getAttribute('name');
    let error = null;
    
    // Required check
    if (input.required && !value) {
        error = 'Это поле обязательно для заполнения';
    }
    
    // Email validation
    if (name === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            error = 'Введите корректный email';
        }
    }
    
    // Phone validation
    if (name === 'phone' && value) {
        const digits = value.replace(/\D/g, '');
        if (digits.length < 11) {
            error = 'Введите полный номер телефона';
        }
    }
    
    // Show or clear error
    const existingError = input.parentNode.querySelector('.form-error');
    if (existingError) existingError.remove();
    
    if (error) {
        input.classList.add('error');
        const errorEl = document.createElement('span');
        errorEl.className = 'form-error';
        errorEl.textContent = error;
        input.parentNode.appendChild(errorEl);
        return false;
    } else {
        input.classList.remove('error');
        return true;
    }
}

/**
 * Toast Notification
 */
function showToast(message, type = 'success') {
    // Remove existing toast
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            ${type === 'success' 
                ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/>'
                : '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>'}
        </svg>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto-hide
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/**
 * Download Document with Progress Feedback
 */
document.querySelectorAll('.doc-download').forEach(link => {
    link.addEventListener('click', function() {
        const icon = this.querySelector('svg');
        if (icon) {
            icon.style.animation = 'pulse 0.5s ease';
            setTimeout(() => {
                icon.style.animation = '';
            }, 500);
        }
        
        showToast('Загрузка документа началась...', 'success');
    });
});

/**
 * Cookie Banner Handler
 */
function initCookieBanner() {
    const banner = document.getElementById('cookieBanner');
    const acceptBtn = document.getElementById('cookieAccept');
    const declineBtn = document.getElementById('cookieDecline');
    
    if (!banner) return;
    
    // Check if user already made a choice
    const cookieConsent = localStorage.getItem('cookieConsent');
    
    if (cookieConsent === null) {
        // Show banner after a short delay
        setTimeout(() => {
            banner.classList.add('visible');
        }, 1500);
    } else if (cookieConsent === 'accepted') {
        // Load analytics if previously accepted
        loadYandexMetrika();
    }
    
    // Accept button
    if (acceptBtn) {
        acceptBtn.addEventListener('click', () => {
            localStorage.setItem('cookieConsent', 'accepted');
            localStorage.setItem('cookieConsentDate', new Date().toISOString());
            banner.classList.remove('visible');
            loadYandexMetrika();
            showToast('Настройки cookie сохранены', 'success');
        });
    }
    
    // Decline button
    if (declineBtn) {
        declineBtn.addEventListener('click', () => {
            localStorage.setItem('cookieConsent', 'declined');
            localStorage.setItem('cookieConsentDate', new Date().toISOString());
            banner.classList.remove('visible');
            showToast('Аналитические cookie отключены', 'success');
        });
    }
}

/**
 * Load Yandex Metrika (conditionally)
 * Replace XXXXXXXX with your actual Metrika counter ID
 */
function loadYandexMetrika() {
    // Uncomment and configure when you have a Metrika counter
    /*
    (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
    m[i].l=1*new Date();
    for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
    k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
    (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");

    ym(XXXXXXXX, "init", {
        clickmap:true,
        trackLinks:true,
        accurateTrackBounce:true,
        webvisor:true
    });
    */
    console.log('Yandex Metrika would be loaded here');
}
