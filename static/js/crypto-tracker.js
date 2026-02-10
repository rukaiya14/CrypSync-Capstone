// CrypSync - Advanced Crypto Tracker with Real-Time Data
// Inspired by CoinStats

class CryptoTracker {
    constructor() {
        this.cryptoData = [];
        this.favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        this.currentTab = 'coins';
        this.searchQuery = '';
        this.sortBy = 'market_cap';
        this.sortOrder = 'desc';
        this.page = 1;
        this.perPage = 50;
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.fetchMarketStats();
        this.fetchCryptoData();
        this.setupEventListeners();
        this.startAutoUpdate();
    }

    async fetchMarketStats() {
        try {
            const response = await fetch('https://api.coingecko.com/api/v3/global', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.updateMarketStats(data.data);
        } catch (error) {
            console.error('Failed to fetch market stats:', error);
        }
    }

    updateMarketStats(data) {
        const marketCap = data.total_market_cap.usd;
        const volume = data.total_volume.usd;
        const btcDominance = data.market_cap_percentage.btc;
        const marketCapChange = data.market_cap_change_percentage_24h_usd;

        document.getElementById('marketCap').innerHTML = `
            <div class="market-stat-value">$${this.formatNumber(marketCap)}</div>
            <div class="market-stat-change ${marketCapChange >= 0 ? 'positive' : 'negative'}">
                ${marketCapChange >= 0 ? '▲' : '▼'} ${Math.abs(marketCapChange).toFixed(2)}%
            </div>
        `;

        document.getElementById('volume24h').innerHTML = `
            <div class="market-stat-value">$${this.formatNumber(volume)}</div>
        `;

        document.getElementById('btcDominance').innerHTML = `
            <div class="market-stat-value">${btcDominance.toFixed(2)}%</div>
        `;
    }

    async fetchCryptoData() {
        try {
            this.showLoading();
            const response = await fetch(
                `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=${this.perPage}&page=${this.page}&sparkline=true&price_change_percentage=24h,7d`,
                {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.cryptoData = await response.json();
            this.renderCryptoList();
        } catch (error) {
            console.error('Failed to fetch crypto data:', error);
            this.showError('Failed to load cryptocurrency data. Please check your internet connection and try again.');
        }
    }

    renderCryptoList() {
        const container = document.getElementById('cryptoList');
        if (!container) return;

        let filteredData = this.cryptoData;

        // Filter by tab
        if (this.currentTab === 'favorites') {
            filteredData = filteredData.filter(crypto => this.favorites.includes(crypto.id));
        }

        // Filter by search
        if (this.searchQuery) {
            filteredData = filteredData.filter(crypto =>
                crypto.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                crypto.symbol.toLowerCase().includes(this.searchQuery.toLowerCase())
            );
        }

        if (filteredData.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-5">
                        <div class="empty-state">
                            <i class="fas fa-search fa-3x mb-3"></i>
                            <p>No cryptocurrencies found</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        const html = filteredData.map((crypto, index) => this.renderCryptoRow(crypto, index + 1)).join('');
        container.innerHTML = html;

        // Render sparklines
        filteredData.forEach(crypto => {
            this.renderSparkline(crypto.id, crypto.sparkline_in_7d.price);
        });
    }

    renderCryptoRow(crypto, rank) {
        const isFavorite = this.favorites.includes(crypto.id);
        const priceChange24h = crypto.price_change_percentage_24h || 0;
        const priceChange7d = crypto.price_change_percentage_7d_in_currency || 0;

        return `
            <tr class="crypto-row" data-crypto-id="${crypto.id}">
                <td>
                    <i class="far fa-star favorite-icon ${isFavorite ? 'fas favorited' : ''}" 
                       onclick="cryptoTracker.toggleFavorite('${crypto.id}')" 
                       title="${isFavorite ? 'Remove from favorites' : 'Add to favorites'}"></i>
                </td>
                <td class="crypto-rank">${rank}</td>
                <td>
                    <div class="crypto-info">
                        <img src="${crypto.image}" alt="${crypto.name}" class="crypto-icon" width="32" height="32">
                        <div>
                            <div class="crypto-name">${crypto.name}</div>
                            <div class="crypto-symbol">${crypto.symbol.toUpperCase()}</div>
                        </div>
                    </div>
                </td>
                <td class="price">$${this.formatPrice(crypto.current_price)}</td>
                <td>
                    <span class="price-change ${priceChange24h >= 0 ? 'positive' : 'negative'}">
                        ${priceChange24h >= 0 ? '▲' : '▼'} ${Math.abs(priceChange24h).toFixed(2)}%
                    </span>
                </td>
                <td>
                    <span class="price-change ${priceChange7d >= 0 ? 'positive' : 'negative'}">
                        ${priceChange7d >= 0 ? '▲' : '▼'} ${Math.abs(priceChange7d).toFixed(2)}%
                    </span>
                </td>
                <td class="market-cap">$${this.formatNumber(crypto.market_cap)}</td>
                <td class="volume-24h">$${this.formatNumber(crypto.total_volume)}</td>
                <td>
                    <canvas id="sparkline-${crypto.id}" class="sparkline" width="100" height="40"></canvas>
                </td>
            </tr>
        `;
    }

    renderSparkline(cryptoId, prices) {
        const canvas = document.getElementById(`sparkline-${cryptoId}`);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        if (!prices || prices.length === 0) return;

        // Calculate min and max
        const min = Math.min(...prices);
        const max = Math.max(...prices);
        const range = max - min;

        // Determine color based on trend
        const isPositive = prices[prices.length - 1] >= prices[0];
        const color = isPositive ? '#00d084' : '#ff4757';

        // Draw line
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.beginPath();

        prices.forEach((price, index) => {
            const x = (index / (prices.length - 1)) * width;
            const y = height - ((price - min) / range) * height;

            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();

        // Fill area under line
        ctx.lineTo(width, height);
        ctx.lineTo(0, height);
        ctx.closePath();
        ctx.fillStyle = isPositive ? 'rgba(0, 208, 132, 0.1)' : 'rgba(255, 71, 87, 0.1)';
        ctx.fill();
    }

    toggleFavorite(cryptoId) {
        const index = this.favorites.indexOf(cryptoId);
        if (index > -1) {
            this.favorites.splice(index, 1);
        } else {
            this.favorites.push(cryptoId);
        }
        localStorage.setItem('favorites', JSON.stringify(this.favorites));
        this.renderCryptoList();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Search
        const searchInput = document.getElementById('cryptoSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                this.renderCryptoList();
            });
        }

        // Pagination
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousPage());
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextPage());
        }
    }

    switchTab(tab) {
        this.currentTab = tab;

        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });

        this.renderCryptoList();
    }

    previousPage() {
        if (this.page > 1) {
            this.page--;
            this.fetchCryptoData();
            this.updatePagination();
        }
    }

    nextPage() {
        this.page++;
        this.fetchCryptoData();
        this.updatePagination();
    }

    updatePagination() {
        const pageNum = document.getElementById('pageNumber');
        if (pageNum) {
            pageNum.textContent = this.page;
        }

        const prevBtn = document.getElementById('prevPage');
        if (prevBtn) {
            prevBtn.disabled = this.page === 1;
        }
    }

    startAutoUpdate() {
        // Update every 60 seconds
        this.updateInterval = setInterval(() => {
            this.fetchMarketStats();
            this.fetchCryptoData();
        }, 60000);
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }

    formatPrice(price) {
        if (price >= 1) {
            return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        } else if (price >= 0.01) {
            return price.toFixed(4);
        } else {
            return price.toFixed(8);
        }
    }

    formatNumber(num) {
        if (num >= 1e12) {
            return (num / 1e12).toFixed(2) + 'T';
        } else if (num >= 1e9) {
            return (num / 1e9).toFixed(2) + 'B';
        } else if (num >= 1e6) {
            return (num / 1e6).toFixed(2) + 'M';
        } else if (num >= 1e3) {
            return (num / 1e3).toFixed(2) + 'K';
        }
        return num.toFixed(2);
    }

    showLoading() {
        const container = document.getElementById('cryptoList');
        if (container) {
            container.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-5">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-3 text-muted">Loading cryptocurrency data...</p>
                    </td>
                </tr>
            `;
        }
    }

    showError(message) {
        const container = document.getElementById('cryptoList');
        if (container) {
            container.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-5">
                        <div class="alert alert-danger" style="margin: 2rem; padding: 2rem; max-width: 600px; margin-left: auto; margin-right: auto;">
                            <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                            <h5>${message}</h5>
                            <p class="mt-3 mb-3">This could be due to:</p>
                            <ul style="text-align: left; display: inline-block;">
                                <li>CoinGecko API rate limit reached (50 requests/minute)</li>
                                <li>Network connectivity issues</li>
                                <li>Browser blocking the request</li>
                            </ul>
                            <button class="btn btn-primary mt-3" onclick="cryptoTracker.fetchCryptoData()">
                                <i class="fas fa-sync-alt"></i> Try Again
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }
    }
}

// Initialize tracker when DOM is ready
let cryptoTracker;
document.addEventListener('DOMContentLoaded', () => {
    cryptoTracker = new CryptoTracker();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (cryptoTracker) {
        cryptoTracker.stopAutoUpdate();
    }
});
