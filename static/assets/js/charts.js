
class ChartsManager {
    constructor() {
        this.charts = {};
        this.defaultColors = {
            gold: '#d4af37',
            blue: '#1e3a5f',
            green: '#28a745',
            red: '#dc3545',
            orange: '#fd7e14',
            purple: '#6f42c1'
        };
    }

    // Create Line Chart
    createLineChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const config = {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: data.label || 'البيانات',
                    data: data.values,
                    borderColor: data.color || this.defaultColors.gold,
                    backgroundColor: this.hexToRgba(data.color || this.defaultColors.gold, 0.1),
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: data.color || this.defaultColors.gold,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: options.showLegend !== false,
                        position: 'top',
                        labels: {
                            font: { family: 'Cairo', size: 12 },
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(10,22,40,0.9)',
                        titleFont: { family: 'Cairo', size: 14 },
                        bodyFont: { family: 'Cairo', size: 13 },
                        padding: 12,
                        cornerRadius: 10,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.05)' },
                        ticks: {
                            font: { family: 'Cairo' },
                            callback: function (value) {
                                return options.currency ? '$' + value : value;
                            }
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { family: 'Cairo' } }
                    }
                },
                ...options.chartOptions
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    // Create Bar Chart
    createBarChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const config = {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: data.datasets.map((dataset, index) => ({
                    label: dataset.label,
                    data: dataset.values,
                    backgroundColor: dataset.color || Object.values(this.defaultColors)[index],
                    borderRadius: 8,
                    borderSkipped: false
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: data.datasets.length > 1,
                        labels: { font: { family: 'Cairo' } }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    // Create Doughnut Chart
    createDoughnutChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const config = {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: data.colors || Object.values(this.defaultColors),
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { family: 'Cairo', size: 12 },
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    // Create Pie Chart
    createPieChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const config = {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: data.colors || Object.values(this.defaultColors),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { font: { family: 'Cairo' } }
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    // Update Chart Data
    updateChart(canvasId, newData) {
        const chart = this.charts[canvasId];
        if (!chart) return;

        chart.data.labels = newData.labels;
        chart.data.datasets[0].data = newData.values;
        chart.update('active');
    }

    // Destroy Chart
    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }

    // Helper: Convert Hex to RGBA
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // Helper: Generate Random Data
    generateRandomData(count, min, max) {
        return Array.from({ length: count }, () =>
            Math.floor(Math.random() * (max - min + 1)) + min
        );
    }

    // Helper: Get Monthly Data
    getMonthlyData(bookings, months = 6) {
        const labels = [];
        const values = [];

        for (let i = months - 1; i >= 0; i--) {
            const date = new Date();
            date.setMonth(date.getMonth() - i);
            const monthKey = date.toISOString().slice(0, 7);

            labels.push(date.toLocaleDateString('ar-SA', { month: 'short' }));
            values.push(bookings.filter(b => b.createdAt?.startsWith(monthKey)).length);
        }

        return { labels, values };
    }
}

// Initialize Charts Manager
const chartsManager = new ChartsManager();
window.chartsManager = chartsManager;

// Auto-initialize common charts if elements exist
document.addEventListener('DOMContentLoaded', () => {
    // Revenue Chart (if exists)
    if (document.getElementById('revenueChart')) {
        chartsManager.createDoughnutChart('revenueChart', {
            labels: ['الفندق', 'النادي', 'المطاعم', 'السبا'],
            values: [45, 25, 20, 10],
            colors: ['#d4af37', '#1e3a5f', '#28a745', '#dc3545']
        });
    }

    // Bookings Chart (if exists)
    if (document.getElementById('bookingsChart')) {
        chartsManager.createLineChart('bookingsChart', {
            labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
            values: [65, 78, 90, 81, 96, 105],
            label: 'الحجوزات',
            color: '#d4af37'
        });
    }
});

