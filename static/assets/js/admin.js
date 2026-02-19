
class AdminDashboard {
    constructor() {
        this.bookings = JSON.parse(localStorage.getItem('bookings')) || [];
        this.rooms = JSON.parse(localStorage.getItem('rooms')) || [];
        this.memberships = JSON.parse(localStorage.getItem('memberships')) || [];
        this.init();
    }

    init() {
        this.loadDashboardData();
        this.bindEvents();
        this.initCharts();
    }

    // Load Dashboard Statistics
    loadDashboardData() {
        // Today's stats
        const today = new Date().toISOString().split('T')[0];
        const todayBookings = this.bookings.filter(b => b.createdAt?.startsWith(today));

        // Update stats
        this.updateStat('todayBookings', todayBookings.length);
        this.updateStat('totalRevenue', this.calculateRevenue());
        this.updateStat('availableRooms', this.getAvailableRoomsCount());
        this.updateStat('activeMembers', this.memberships.length);

        // Load recent bookings table
        this.loadRecentBookings();
    }

    updateStat(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    calculateRevenue() {
        return this.bookings.reduce((total, booking) => {
            return total + (booking.totalPrice || 0);
        }, 0);
    }

    getAvailableRoomsCount() {
        return this.rooms.filter(r => r.available).length;
    }

    // Load Recent Bookings Table
    loadRecentBookings() {
        const tableBody = document.getElementById('recentBookingsTable');
        if (!tableBody) return;

        const recentBookings = this.bookings.slice(-10).reverse();

        tableBody.innerHTML = recentBookings.map(booking => `
            <tr>
                <td>#${booking.id.slice(-5)}</td>
                <td>${booking.guestName || 'غير معروف'}</td>
                <td>${booking.room?.name || '-'}</td>
                <td>${this.formatDate(booking.checkIn)}</td>
                <td>$${booking.totalPrice || 0}</td>
                <td><span class="status ${booking.status}">${this.getStatusText(booking.status)}</span></td>
                <td>
                    <button class="action-btn edit" onclick="adminDashboard.editBooking('${booking.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="adminDashboard.deleteBooking('${booking.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    getStatusText(status) {
        const statuses = {
            'pending': 'معلق',
            'confirmed': 'مؤكد',
            'cancelled': 'ملغي',
            'checked-in': 'تم الدخول',
            'checked-out': 'تم الخروج'
        };
        return statuses[status] || status;
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('ar-SA');
    }

    // Initialize Charts
    initCharts() {
        this.initBookingsChart();
        this.initRevenueChart();
    }

    initBookingsChart() {
        const ctx = document.getElementById('bookingsChart');
        if (!ctx) return;

        // Get last 6 months data
        const months = this.getLast6Months();
        const data = months.map(month => this.getBookingsForMonth(month));

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: months.map(m => m.toLocaleDateString('ar-SA', { month: 'short' })),
                datasets: [{
                    label: 'الحجوزات',
                    data: data,
                    borderColor: '#d4af37',
                    backgroundColor: 'rgba(212,175,55,0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 10 } }
                }
            }
        });
    }

    initRevenueChart() {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['الفندق', 'النادي', 'المطاعم', 'السبا'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: ['#d4af37', '#1e3a5f', '#28a745', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    getLast6Months() {
        const months = [];
        for (let i = 5; i >= 0; i--) {
            const date = new Date();
            date.setMonth(date.getMonth() - i);
            months.push(date);
        }
        return months;
    }

    getBookingsForMonth(date) {
        const monthStr = date.toISOString().slice(0, 7);
        return this.bookings.filter(b => b.createdAt?.startsWith(monthStr)).length;
    }

    // CRUD Operations
    editBooking(id) {
        const booking = this.bookings.find(b => b.id === id);
        if (!booking) return;

        // Show edit modal or navigate to edit page
        console.log('Editing booking:', booking);
        this.showToast('جاري فتح صفحة التعديل...', 'info');
    }

    deleteBooking(id) {
        if (!confirm('هل أنت متأكد من حذف هذا الحجز؟')) return;

        this.bookings = this.bookings.filter(b => b.id !== id);
        localStorage.setItem('bookings', JSON.stringify(this.bookings));
        this.loadRecentBookings();
        this.showToast('تم حذف الحجز بنجاح', 'success');
    }

    // Event Binding
    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                e.target.closest('.nav-link').classList.add('active');
            });
        });

        // Search functionality
        const searchInput = document.getElementById('searchBookings');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.searchBookings(e.target.value));
        }
    }

    searchBookings(query) {
        if (!query) {
            this.loadRecentBookings();
            return;
        }

        const filtered = this.bookings.filter(b =>
            b.guestName?.includes(query) ||
            b.id?.includes(query) ||
            b.room?.name?.includes(query)
        );

        const tableBody = document.getElementById('recentBookingsTable');
        if (tableBody) {
            // Update table with filtered results
            this.renderBookingsTable(filtered, tableBody);
        }
    }

    renderBookingsTable(bookings, container) {
        container.innerHTML = bookings.map(booking => `
            <tr>
                <td>#${booking.id.slice(-5)}</td>
                <td>${booking.guestName || 'غير معروف'}</td>
                <td>${booking.room?.name || '-'}</td>
                <td>${this.formatDate(booking.checkIn)}</td>
                <td>$${booking.totalPrice || 0}</td>
                <td><span class="status ${booking.status}">${this.getStatusText(booking.status)}</span></td>
                <td>
                    <button class="action-btn edit" onclick="adminDashboard.editBooking('${booking.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="adminDashboard.deleteBooking('${booking.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    // Toast Notification
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
            color: white;
            padding: 15px 30px;
            border-radius: 50px;
            font-weight: 500;
            z-index: 10000;
            animation: slideUp 0.3s ease;
        `;

        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
}

// Initialize Admin Dashboard
const adminDashboard = new AdminDashboard();
window.adminDashboard = adminDashboard;

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from { transform: translateX(-50%) translateY(100px); opacity: 0; }
        to { transform: translateX(-50%) translateY(0); opacity: 1; }
    }
`;
document.head.appendChild(style);
