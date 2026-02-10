// Alerts functionality
async function fetchAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const data = await response.json();
        
        if (data.success) {
            displayAlerts(data.alerts);
        } else {
            showError('Failed to fetch alerts');
        }
    } catch (error) {
        showError('An error occurred while fetching alerts');
    }
}

function displayAlerts(alerts) {
    const container = document.getElementById('alertsTable');
    
    if (alerts.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5 text-muted">
                <i class="fas fa-bell-slash fa-3x mb-3"></i>
                <p>No alerts configured yet. Create your first alert!</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Cryptocurrency</th>
                    <th>Threshold</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    alerts.forEach(alert => {
        const statusClass = alert.state === 'ACTIVE' ? 'active' : 'triggered';
        const typeText = alert.alert_type === 'ABOVE_THRESHOLD' ? 'Above' : 'Below';
        
        html += `
            <tr>
                <td><span class="coin-name">${alert.crypto_id}</span></td>
                <td><span class="price">$${parseFloat(alert.threshold).toLocaleString()}</span></td>
                <td>${typeText}</td>
                <td><span class="alert-status ${statusClass}">${alert.state}</span></td>
                <td><small class="text-muted">${new Date(alert.created_at).toLocaleDateString()}</small></td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteAlert('${alert.alert_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
}

async function createAlert() {
    const cryptoId = document.getElementById('cryptoId').value;
    const threshold = document.getElementById('threshold').value;
    const alertType = document.getElementById('alertType').value;
    const errorDiv = document.getElementById('alertError');
    
    errorDiv.classList.add('d-none');
    
    try {
        const response = await fetch('/api/alerts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ crypto_id: cryptoId, threshold, alert_type: alertType })
        });
        
        const data = await response.json();
        
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('createAlertModal')).hide();
            document.getElementById('createAlertForm').reset();
            fetchAlerts();
        } else {
            errorDiv.textContent = data.message || 'Failed to create alert';
            errorDiv.classList.remove('d-none');
        }
    } catch (error) {
        errorDiv.textContent = 'An error occurred. Please try again.';
        errorDiv.classList.remove('d-none');
    }
}

async function deleteAlert(alertId) {
    if (!confirm('Are you sure you want to delete this alert?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/alerts?alert_id=${alertId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            fetchAlerts();
        } else {
            alert('Failed to delete alert');
        }
    } catch (error) {
        alert('An error occurred while deleting the alert');
    }
}

function showError(message) {
    const container = document.getElementById('alertsTable');
    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="fas fa-exclamation-triangle"></i> ${message}
        </div>
    `;
}

// Initial load
fetchAlerts();
