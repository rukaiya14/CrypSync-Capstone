// Dashboard functionality
let priceRefreshInterval;

async function fetchPrices() {
    try {
        const response = await fetch('/api/prices?ids=bitcoin,ethereum');
        const data = await response.json();
        
        if (data.success) {
            displayPrices(data.data);
        } else {
            showError('Failed to fetch prices');
        }
    } catch (error) {
        showError('An error occurred while fetching prices');
    }
}

function displayPrices(prices) {
    const container = document.getElementById('pricesTable');
    
    let html = `
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Cryptocurrency</th>
                    <th>Price (USD)</th>
                    <th>24h Change</th>
                    <th>Last Updated</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    for (const [cryptoId, priceData] of Object.entries(prices)) {
        const change24h = parseFloat(priceData.change_24h);
        const changeClass = change24h >= 0 ? 'positive' : 'negative';
        const changeIcon = change24h >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
        
        html += `
            <tr>
                <td>
                    <span class="coin-name">${cryptoId}</span>
                </td>
                <td>
                    <span class="price">$${parseFloat(priceData.price_usd).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                </td>
                <td>
                    <span class="price-change ${changeClass}">
                        <i class="fas ${changeIcon}"></i> ${Math.abs(change24h).toFixed(2)}%
                    </span>
                </td>
                <td>
                    <small class="text-muted">${new Date(priceData.fetched_at).toLocaleString()}</small>
                </td>
            </tr>
        `;
    }
    
    html += `
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
}

function showError(message) {
    const container = document.getElementById('pricesTable');
    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="fas fa-exclamation-triangle"></i> ${message}
        </div>
    `;
}

function refreshPrices() {
    fetchPrices();
}

// Initial load
fetchPrices();

// Auto-refresh every 60 seconds
priceRefreshInterval = setInterval(fetchPrices, 60000);
