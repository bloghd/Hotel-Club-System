
// GRAND ROYAL HOTEL & CLUB MANAGEMENT SYSTEM
// Main JavaScript File
// =====================================

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    initPreloader();
    initNavbar();
    initMobileMenu();
    initBookingForm();
    initDateInputs();
    initSmoothScroll();
    initAnimations();
    initGallery();
    initData();
});

// Preloader
function initPreloader() {
    const preloader = document.getElementById('preloader');
    if (preloader) {
        setTimeout(() => {
            preloader.classList.add('hidden');
        }, 1500);
    }
}

// Navbar scroll effect
function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// Mobile menu toggle
function initMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenu && navLinks) {
        mobileMenu.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            mobileMenu.classList.toggle('active');
        });
    }
}

// Booking form handler
function initBookingForm() {
    const bookingForm = document.getElementById('bookingForm');
    if (!bookingForm) return;

    bookingForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const checkIn = document.getElementById('checkIn')?.value;
        const checkOut = document.getElementById('checkOut')?.value;
        const adults = document.getElementById('adults')?.value;
        const children = document.getElementById('children')?.value;

        if (!checkIn || !checkOut) {
            showToast('الرجاء اختيار تواريخ الإقامة', 'error');
            return;
        }

        // Save to localStorage
        const bookingData = {
            checkIn,
            checkOut,
            adults,
            children,
            timestamp: new Date().toISOString()
        };

        localStorage.setItem('currentBooking', JSON.stringify(bookingData));
        showToast('جاري تحويلك لصفحة الغرف...', 'success');

        setTimeout(() => {
            window.location.href = 'pages/rooms.html';
        }, 1000);
    });
}

// Date inputs initialization
function initDateInputs() {
    const checkIn = document.getElementById('checkIn');
    const checkOut = document.getElementById('checkOut');

    if (!checkIn) return;

    const today = new Date().toISOString().split('T')[0];
    checkIn.setAttribute('min', today);

    if (checkOut) {
        checkIn.addEventListener('change', () => {
            checkOut.setAttribute('min', checkIn.value);
            if (checkOut.value && checkOut.value <= checkIn.value) {
                const nextDay = new Date(checkIn.value);
                nextDay.setDate(nextDay.getDate() + 1);
                checkOut.value = nextDay.toISOString().split('T')[0];
            }
        });
    }
}

// Smooth scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Scroll animations
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('aos-animate');
            }
        });
    }, observerOptions);

    document.querySelectorAll('[data-aos]').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Gallery lightbox
function initGallery() {
    document.querySelectorAll('.gallery-item').forEach(item => {
        item.addEventListener('click', function () {
            const img = this.querySelector('img');
            if (!img) return;

            const lightbox = document.createElement('div');
            lightbox.className = 'lightbox';
            lightbox.innerHTML = `
                <div class="lightbox-content">
                    <img src="${img.src}" alt="${img.alt}">
                    <button class="lightbox-close">&times;</button>
                </div>
            `;

            document.body.appendChild(lightbox);

            lightbox.querySelector('.lightbox-close').addEventListener('click', () => {
                lightbox.remove();
            });

            lightbox.addEventListener('click', (e) => {
                if (e.target === lightbox) {
                    lightbox.remove();
                }
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    lightbox.remove();
                }
            });
        });
    });
}

// Initialize default data
function initData() {
    // Rooms data
    if (!localStorage.getItem('rooms')) {
        const rooms = [
            {
                id: 1,
                name: 'غرفة ديلوكس',
                type: 'deluxe',
                price: 150,
                capacity: 2,
                size: 35,
                image: 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=600',
                gallery: [
                    'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800',
                    'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800',
                    'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800',
                    'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800'
                ],
                amenities: ['wifi', 'ac', 'tv', 'minibar', 'safe', 'phone'],
                description: 'غرفة فاخرة بتصميم عصري تطل على المدينة، مثالية للإقامة المريحة.',
                features: ['سرير مزدوج كبير', 'حمام خاص مع دوش', 'ميني بار', 'خزنة آمنة', 'مكيف هواء', 'واي فاي مجاني'],
                available: true
            },
            {
                id: 2,
                name: 'جناح تنفيذي',
                type: 'suite',
                price: 280,
                capacity: 2,
                size: 55,
                image: 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=600',
                gallery: [
                    'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800',
                    'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800',
                    'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800',
                    'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800'
                ],
                amenities: ['wifi', 'ac', 'tv', 'jacuzzi', 'balcony', 'minibar', 'safe', 'coffee'],
                description: 'جناح فاخر مع غرفة معيشة منفصلة وجاكوزي وإطلالة بانورامية رائعة.',
                features: ['سرير كينج فاخر', 'جاكوزي خاص', 'شرفة خاصة', 'غرفة معيشة', 'ميني بار مجاني', 'خدمة الغرف 24 ساعة'],
                available: true
            },
            {
                id: 3,
                name: 'الجناح الملكي',
                type: 'royal',
                price: 450,
                capacity: 4,
                size: 85,
                image: 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=600',
                gallery: [
                    'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800',
                    'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800',
                    'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800',
                    'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800'
                ],
                amenities: ['wifi', 'ac', 'tv', 'pool', 'butler', 'kitchen', 'jacuzzi', 'balcony'],
                description: 'أقصى درجات الفخامة مع مسبح خاص وخدمة خاصة على مدار الساعة.',
                features: ['غرفتين نوم', 'مسبح خاص', 'مطبخ مجهز', 'خادم خاص', 'جاكوزي', 'شرفة بانورامية'],
                available: true
            },
            {
                id: 4,
                name: 'غرفة عائلية',
                type: 'family',
                price: 220,
                capacity: 4,
                size: 45,
                image: 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=600',
                gallery: [
                    'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800',
                    'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800',
                    'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800',
                    'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800'
                ],
                amenities: ['wifi', 'ac', 'tv', 'minibar', 'safe'],
                description: 'غرفة مثالية للعائلات مع مساحة واسعة وإطلالة رائعة.',
                features: ['سرير كينج + سريرين منفصلين', 'حمامين', 'منطقة جلوس', 'تلفزيون 55 بوصة', 'واي فاي مجاني'],
                available: true
            }
        ];
        localStorage.setItem('rooms', JSON.stringify(rooms));
    }

    // Initialize empty arrays if not exist
    if (!localStorage.getItem('bookings')) {
        localStorage.setItem('bookings', JSON.stringify([]));
    }
    if (!localStorage.getItem('memberships')) {
        localStorage.setItem('memberships', JSON.stringify([]));
    }
    if (!localStorage.getItem('clubBookings')) {
        localStorage.setItem('clubBookings', JSON.stringify([]));
    }
    if (!localStorage.getItem('contacts')) {
        localStorage.setItem('contacts', JSON.stringify([]));
    }
}

// Utility Functions
const Utils = {
    formatCurrency: (amount, currency = 'USD') => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    formatDate: (dateString) => {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('ar-SA', options);
    },

    calculateNights: (checkIn, checkOut) => {
        const start = new Date(checkIn);
        const end = new Date(checkOut);
        const diffTime = Math.abs(end - start);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    },

    generateId: () => {
        return 'GR' + Date.now().toString(36).toUpperCase();
    },

    getFromStorage: (key) => {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    },

    saveToStorage: (key, value) => {
        localStorage.setItem(key, JSON.stringify(value));
    }
};

// Toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
