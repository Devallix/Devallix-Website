document.addEventListener('DOMContentLoaded', function() {
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        offset: 50,
    });

    const loader = document.getElementById('pageLoader');
    if (loader) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                loader.classList.add('hidden');
            }, 500);
        });
        setTimeout(function() {
            loader.classList.add('hidden');
        }, 3000);
    }

    const backToTop = document.getElementById('backToTop');
    if (backToTop) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });
        backToTop.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    const nav = document.getElementById('mainNav');
    if (nav) {
        function updateNav() {
            if (window.scrollY > 50) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }
        }
        updateNav();
        window.addEventListener('scroll', updateNav, { passive: true });
    }

    const typedEl = document.getElementById('typed-output');
    if (typedEl) {
        const texts = JSON.parse(typedEl.getAttribute('data-texts') || '[]');
        if (texts.length > 0) {
            let textIndex = 0;
            let charIndex = 0;
            let isDeleting = false;
            let typingSpeed = 100;

            function type() {
                const currentText = texts[textIndex];
                if (isDeleting) {
                    typedEl.textContent = currentText.substring(0, charIndex - 1);
                    charIndex--;
                    typingSpeed = 50;
                } else {
                    typedEl.textContent = currentText.substring(0, charIndex + 1);
                    charIndex++;
                    typingSpeed = 100;
                }

                if (!isDeleting && charIndex === currentText.length) {
                    typingSpeed = 2000;
                    isDeleting = true;
                } else if (isDeleting && charIndex === 0) {
                    isDeleting = false;
                    textIndex = (textIndex + 1) % texts.length;
                    typingSpeed = 500;
                }

                setTimeout(type, typingSpeed);
            }
            type();
        }
    }

    function animateCounters() {
        const counters = document.querySelectorAll('[data-counter]');
        counters.forEach(function(counter) {
            if (counter.dataset.animated) return;
            const target = parseInt(counter.getAttribute('data-counter'));
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;

            function updateCounter() {
                current += step;
                if (current < target) {
                    counter.textContent = Math.floor(current).toLocaleString();
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target.toLocaleString();
                    counter.dataset.animated = 'true';
                }
            }
            updateCounter();
        });
    }

    const counterObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                animateCounters();
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.counter-section').forEach(function(el) {
        counterObserver.observe(el);
    });

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function(el) {
        new bootstrap.Tooltip(el);
    });

    const progressBars = document.querySelectorAll('.progress-bar-custom');
    if (progressBars.length > 0) {
        const progressObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    const width = bar.getAttribute('data-width') || bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(function() {
                        bar.style.width = width;
                    }, 200);
                    progressObserver.unobserve(bar);
                }
            });
        }, { threshold: 0.5 });

        progressBars.forEach(function(bar) {
            progressObserver.observe(bar);
        });
    }

    /* ───────── Hero Particle Canvas ───────── */
    const heroCanvas = document.getElementById('heroParticles');
    if (heroCanvas) {
        const ctx = heroCanvas.getContext('2d');
        let particles = [];
        let mouse = { x: null, y: null, radius: 150 };

        function resizeCanvas() {
            const hero = heroCanvas.parentElement;
            heroCanvas.width = hero.offsetWidth;
            heroCanvas.height = hero.offsetHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        heroCanvas.parentElement.addEventListener('mousemove', function(e) {
            const rect = heroCanvas.getBoundingClientRect();
            mouse.x = e.clientX - rect.left;
            mouse.y = e.clientY - rect.top;
        });
        heroCanvas.parentElement.addEventListener('mouseleave', function() {
            mouse.x = null;
            mouse.y = null;
        });

        class Particle {
            constructor() {
                this.x = Math.random() * heroCanvas.width;
                this.y = Math.random() * heroCanvas.height;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
                this.radius = Math.random() * 2 + 0.5;
                this.opacity = Math.random() * 0.5 + 0.1;
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                if (this.x < 0 || this.x > heroCanvas.width) this.vx *= -1;
                if (this.y < 0 || this.y > heroCanvas.height) this.vy *= -1;
                if (mouse.x !== null) {
                    const dx = mouse.x - this.x;
                    const dy = mouse.y - this.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < mouse.radius) {
                        const force = (mouse.radius - dist) / mouse.radius;
                        this.x -= dx * force * 0.02;
                        this.y -= dy * force * 0.02;
                    }
                }
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(182, 255, 0, ' + this.opacity + ')';
                ctx.fill();
            }
        }

        function initParticles() {
            const count = Math.min(Math.floor((heroCanvas.width * heroCanvas.height) / 8000), 120);
            particles = [];
            for (let i = 0; i < count; i++) {
                particles.push(new Particle());
            }
        }
        initParticles();
        window.addEventListener('resize', function() {
            resizeCanvas();
            initParticles();
        });

        function connectParticles() {
            const maxDist = 140;
            for (let a = 0; a < particles.length; a++) {
                for (let b = a + 1; b < particles.length; b++) {
                    const dx = particles[a].x - particles[b].x;
                    const dy = particles[a].y - particles[b].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < maxDist) {
                        const alpha = (1 - dist / maxDist) * 0.15;
                        ctx.beginPath();
                        ctx.strokeStyle = 'rgba(182, 255, 0, ' + alpha + ')';
                        ctx.lineWidth = 0.5;
                        ctx.moveTo(particles[a].x, particles[a].y);
                        ctx.lineTo(particles[b].x, particles[b].y);
                        ctx.stroke();
                    }
                }
            }
        }

        function animateParticles() {
            ctx.clearRect(0, 0, heroCanvas.width, heroCanvas.height);
            particles.forEach(function(p) { p.update(); p.draw(); });
            connectParticles();
            requestAnimationFrame(animateParticles);
        }
        animateParticles();
    }

    const swipers = document.querySelectorAll('.swiper');
    swipers.forEach(function(el) {
        new Swiper(el, {
            loop: true,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            pagination: {
                el: el.querySelector('.swiper-pagination'),
                clickable: true,
            },
            navigation: {
                nextEl: el.querySelector('.swiper-button-next'),
                prevEl: el.querySelector('.swiper-button-prev'),
            },
            breakpoints: {
                0: { slidesPerView: 1, spaceBetween: 20 },
                768: { slidesPerView: 2, spaceBetween: 30 },
                1024: { slidesPerView: 3, spaceBetween: 30 },
            },
        });
    });
});
