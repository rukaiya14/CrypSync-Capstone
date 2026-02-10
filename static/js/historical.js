// Historical data functionality
let priceChart = null;

async function loadHistoricalData() {
    const cryptoId = document.getElementById('cryptoSelect').value;
    const days = document.getElementById('daysSelect').value;

    // Show loading state
    showLoading();

    try {
        // Fetch data directly from CoinGecko API
        const response = await fetch(`https://api.coingecko.com/api/v3/coins/${cryptoId}/market_chart?vs_currency=usd&days=${days}`);
        const data = await response.json();

        if (data.prices) {
            displayChart(data.prices, cryptoId);
        } else {
            showError('Failed to load historical data');
        }
    } catch (error) {
        console.error('Error loading historical data:', error);
        showError('An error occurred while loading data. Please try again.');
    }
}

function displayChart(prices, cryptoId) {
    const ctx = document.getElementById('priceChart').getContext('2d');

    // Prepare data for Chart.js
    const labels = prices.map(p => {
        const date = new Date(p[0]);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    });

    const priceData = prices.map(p => p[1]);

    // Destroy existing chart if it exists
    if (priceChart) {
        priceChart.destroy();
    }

    // Create new chart
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${cryptoId.toUpperCase()} Price (USD)`,
                data: priceData,
                borderColor: '#ff9500',
                backgroundColor: 'rgba(255, 149, 0, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#ffffff',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#ff9500',
                    borderWidth: 1,
                    callbacks: {
                        label: function (context) {
                            return 'Price: $' + context.parsed.y.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#8a8a8a',
                        maxTicksLimit: 10,
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    display: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#8a8a8a',
                        callback: function (value) {
                            return '$' + value.toLocaleString('en-US', {
                                minimumFractionDigits: 0,
                                maximumFractionDigits: 0
                            });
                        }
                    }
                }
            }
        }
    });
}

function showLoading() {
    const container = document.querySelector('.chart-container');
    container.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Loading historical data...</p>
        </div>
    `;

    // Re-add canvas after a brief moment
    setTimeout(() => {
        container.innerHTML = '<canvas id="priceChart"></canvas>';
    }, 100);
}

function showError(message) {
    const container = document.querySelector('.chart-container');
    container.innerHTML = `
        <div class="alert alert-danger text-center" role="alert">
            <i class="fas fa-exclamation-triangle"></i> ${message}
            <br><br>
            <button class="btn btn-primary" onclick="loadHistoricalData()">
                <i class="fas fa-sync-alt"></i> Try Again
            </button>
        </div>
    `;
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    loadHistoricalData();
});
