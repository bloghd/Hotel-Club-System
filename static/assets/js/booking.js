
class BookingSystem {
    constructor() {
        this.currentBooking = this.getFromStorage('currentBooking') || {};
        this.rooms = this.getFromStorage('rooms') || this.getDefaultRooms();
        this.bookings = this.getFromStorage('bookings') || [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateUI();
    }

    // Storage Helpers
    getFromStorage(key) {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    }

    saveToStorage(key, data) {
        localStorage.setItem(key, JSON.stringify(data));
    }

    getDefaultRooms() {
        return [
            {
                id: 1,
                name: 'غرفة ديلوكس',
                type: 'deluxe',
                price: 150,
                capacity: 2,
                size: 35,
                image: 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=600',
                amenities: ['wifi', 'ac', 'tv', 'minibar'],
                description: 'غرفة فاخرة بتصميم عصري وإطلالة رائعة',
                available: true
            },
            {
                id: 2,
                name: 'جناح تنفيذي',
                type: 'executive',
                price: 280,
                capacity: 2,
                size: 55,
                image: 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=600',
                amenities: ['wifi', 'ac', 'tv', 'jacuzzi', 'balcony'],
                description: 'جناح فاخر مع منطقة جلوس منفصلة وجاكوزي',
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
                amenities: ['wifi', 'ac', 'tv', 'pool', 'butler', 'kitchen'],
                description: 'أقصى درجات الفخامة مع مسبح خاص وخدمة خاصة',
                available: true
            }
        ];
    }

    // Event Binding
    bindEvents() {
        // Booking form
        const bookingForm = document.getElementById('bookingForm');
        if (bookingForm) {
            bookingForm.addEventListener('submit', (e) => this.handleBookingSubmit(e));
        }

        // Date inputs
        const checkIn = document.getElementById('checkIn');
        const checkOut = document.getElementById('checkOut');

        if (checkIn && checkOut) {
            const today = new Date().toISOString().split('T')[0];
            checkIn.min = today;
            checkOut.min = today;

            checkIn.addEventListener('change', () => {
                checkOut.min = checkIn.value;
                this.calculatePrice();
            });

            checkOut.addEventListener('change', () => {
                this.calculatePrice();
            });
        }

        // Room selection
        document.querySelectorAll('.select-room-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectRoom(e));
        });
    }

    // Handle Booking Form Submit
    handleBookingSubmit(e) {
        e.preventDefault();

        const formData = {
            checkIn: document.getElementById('checkIn').value,
            checkOut: document.getElementById('checkOut').value,
            adults: document.getElementById('adults').value,
            children: document.getElementById('children').value,
            timestamp: new Date().toISOString()
        };

        if (!formData.checkIn || !formData.checkOut) {
            this.showToast('الرجاء اختيار تواريخ الإقامة', 'error');
            return;
        }

        this.saveToStorage('currentBooking', formData);
        this.showToast('جاري تحويلك لاختيار الغرفة...', 'success');

        setTimeout(() => {
            window.location.href = 'pages/rooms.html';
        }, 1000);
    }

    // Select Room
    selectRoom(e) {
        const roomId = e.target.dataset.roomId;
        const room = this.rooms.find(r => r.id == roomId);

        if (!room) return;

        this.currentBooking.room = room;
        this.saveToStorage('currentBooking', this.currentBooking);

        this.showToast(`تم اختيار ${room.name}`, 'success');

        setTimeout(() => {
            window.location.href = 'booking.html';
        }, 500);
    }

    // Calculate Price
    calculatePrice() {
        const checkIn = new Date(document.getElementById('checkIn').value);
        const checkOut = new Date(document.getElementById('checkOut').value);
        const priceElement = document.getElementById('totalPrice');
        const nightsElement = document.getElementById('nightsCount');

        if (checkIn && checkOut && priceElement) {
            const diffTime = Math.abs(checkOut - checkIn);
            const nights = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            if (nights > 0) {
                const roomPrice = this.currentBooking.room?.price || 0;
                const total = nights * roomPrice;

                priceElement.textContent = `$${total}`;
                if (nightsElement) nightsElement.textContent = nights;
            }
        }
    }

    // Complete Booking
    completeBooking(bookingData) {
        const booking = {
            id: 'GR-' + Date.now(),
            ...bookingData,
            status: 'pending',
            createdAt: new Date().toISOString()
        };

        this.bookings.push(booking);
        this.saveToStorage('bookings', this.bookings);
        this.saveToStorage('lastBooking', booking);

        // Clear current booking
        localStorage.removeItem('currentBooking');

        return booking;
    }

    // Update UI
    updateUI() {
        // Update booking summary if on booking page
        const summaryContainer = document.getElementById('bookingSummary');
        if (summaryContainer && this.currentBooking.room) {
            summaryContainer.innerHTML = `
                <div class="summary-item">
                    <span>الغرفة:</span>
                    <span>${this.currentBooking.room.name}</span>
                </div>
                <div class="summary-item">
                    <span>السعر/ليلة:</span>
                    <span>$${this.currentBooking.room.price}</span>
                </div>
            `;
        }
    }

    // Toast Notification
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#ffc107'};
            color: white;
            padding: 15px 30px;
            border-radius: 50px;
            font-weight: 500;
            z-index: 10000;
            opacity: 0;
            transition: all 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(-50%) translateY(0)';
        }, 100);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(-50%) translateY(100px)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize Booking System
const bookingSystem = new BookingSystem();

// Export for global access
window.bookingSystem = bookingSystem;

