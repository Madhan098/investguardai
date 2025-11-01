// Dashboard JavaScript functionality for FraudShield

class Dashboard {
    constructor() {
        this.refreshInterval = 30000; // 30 seconds
        this.charts = {};
        this.autoRefreshEnabled = true;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startAutoRefresh();
        console.log('Dashboard initialized');
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshDashboard());
        }

        // Alert action buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="viewAlert"]')) {
                const alertId = e.target.getAttribute('onclick').match(/\d+/)[0];
                this.viewAlert(alertId);
            }
            if (e.target.matches('[onclick*="resolveAlert"]')) {
                const alertId = e.target.getAttribute('onclick').match(/\d+/)[0];
                this.resolveAlert(alertId);
            }
        });
    }

    async refreshDashboard() {
        try {
            this.showLoading(true);
            
            // Fetch latest statistics
            const statsResponse = await fetch('/api/stats');
            const stats = await statsResponse.json();
            
            // Update statistics cards
            this.updateStats(stats);
            
            // Fetch latest alerts
            await this.loadAlerts();
            
            this.showLoading(false);
            this.showNotification('Dashboard updated successfully', 'success');
            
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
            this.showNotification('Failed to refresh dashboard', 'error');
            this.showLoading(false);
        }
    }

    async loadAlerts() {
        try {
            const response = await fetch('/api/alerts');
            const alerts = await response.json();
            
            this.updateAlertsTable(alerts);
            
        } catch (error) {
            console.error('Error loading alerts:', error);
            this.showNotification('Failed to load alerts', 'error');
        }
    }

    updateStats(stats) {
        // Update statistics cards
        const totalAlertsEl = document.getElementById('total-alerts');
        const highRiskEl = document.getElementById('high-risk-count');
        const mediumRiskEl = document.getElementById('medium-risk-count');
        const lowRiskEl = document.getElementById('low-risk-count');

        if (totalAlertsEl) totalAlertsEl.textContent = stats.active_alerts;
        if (highRiskEl) highRiskEl.textContent = stats.high_risk_alerts;
        
        // Animate number changes
        this.animateNumber(totalAlertsEl, stats.active_alerts);
        this.animateNumber(highRiskEl, stats.high_risk_alerts);
    }

    updateAlertsTable(alerts) {
        const container = document.getElementById('alerts-container');
        if (!container) return;

        if (alerts.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i data-feather="check-circle" width="64" height="64" class="mb-3"></i>
                    <h5>No Active Alerts</h5>
                    <p>The system is actively monitoring for fraudulent activity.</p>
                </div>
            `;
            feather.replace();
            return;
        }

        const tableHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Risk Score</th>
                            <th>Severity</th>
                            <th>Content Type</th>
                            <th>Content Preview</th>
                            <th>Detected</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${alerts.map(alert => this.createAlertRow(alert)).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = tableHTML;
        feather.replace();
    }

    createAlertRow(alert) {
        const severityClass = this.getSeverityClass(alert.risk_score);
        const contentTypeIcon = this.getContentTypeIcon(alert.content_type);
        const formattedDate = new Date(alert.created_at).toLocaleDateString('en-US', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });

        return `
            <tr class="alert-row" data-alert-id="${alert.id}">
                <td>
                    <span class="badge bg-${severityClass}">
                        ${alert.risk_score.toFixed(1)}/10
                    </span>
                </td>
                <td>
                    <span class="badge bg-${this.getSeverityBadgeClass(alert.severity)}">
                        ${alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}
                    </span>
                </td>
                <td>
                    <i data-feather="${contentTypeIcon}" class="me-1"></i>
                    ${alert.content_type.charAt(0).toUpperCase() + alert.content_type.slice(1)}
                </td>
                <td>
                    <span class="text-truncate d-inline-block" style="max-width: 300px;">
                        ${alert.content_preview}
                    </span>
                </td>
                <td>
                    <small class="text-muted">${formattedDate}</small>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewAlert(${alert.id})">
                            <i data-feather="eye" width="14" height="14"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="resolveAlert(${alert.id})">
                            <i data-feather="check" width="14" height="14"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    async viewAlert(alertId) {
        try {
            // In a real implementation, fetch detailed alert information
            const alertDetails = `
                <div class="row">
                    <div class="col-12">
                        <h6>Alert ID: ${alertId}</h6>
                        <p>Detailed analysis and fraud indicators would be displayed here.</p>
                        <div class="alert alert-warning">
                            <strong>Risk Assessment:</strong> This alert requires immediate attention.
                        </div>
                    </div>
                </div>
            `;

            document.getElementById('alert-details').innerHTML = alertDetails;
            
            const modal = new bootstrap.Modal(document.getElementById('alertModal'));
            modal.show();
            
        } catch (error) {
            console.error('Error viewing alert:', error);
            this.showNotification('Failed to load alert details', 'error');
        }
    }

    async resolveAlert(alertId) {
        if (!confirm('Are you sure you want to mark this alert as resolved?')) {
            return;
        }

        try {
            // In a real implementation, send API request to resolve alert
            console.log(`Resolving alert ${alertId}`);
            
            // Remove alert row from table
            const alertRow = document.querySelector(`[data-alert-id="${alertId}"]`);
            if (alertRow) {
                alertRow.style.opacity = '0.5';
                setTimeout(() => {
                    alertRow.remove();
                }, 300);
            }
            
            this.showNotification('Alert marked as resolved', 'success');
            
        } catch (error) {
            console.error('Error resolving alert:', error);
            this.showNotification('Failed to resolve alert', 'error');
        }
    }

    getSeverityClass(riskScore) {
        if (riskScore >= 8) return 'danger';
        if (riskScore >= 6) return 'warning';
        if (riskScore >= 3) return 'info';
        return 'success';
    }

    getSeverityBadgeClass(severity) {
        switch (severity) {
            case 'critical': return 'danger';
            case 'high': return 'warning';
            case 'medium': return 'info';
            case 'low': return 'success';
            default: return 'secondary';
        }
    }

    getContentTypeIcon(contentType) {
        switch (contentType) {
            case 'text': return 'file-text';
            case 'url': return 'link';
            case 'image': return 'image';
            case 'video': return 'video';
            default: return 'file';
        }
    }

    animateNumber(element, newValue) {
        if (!element) return;
        
        const currentValue = parseInt(element.textContent) || 0;
        const increment = (newValue - currentValue) / 20;
        let current = currentValue;
        
        const animation = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= newValue) || (increment < 0 && current <= newValue)) {
                current = newValue;
                clearInterval(animation);
            }
            element.textContent = Math.round(current);
        }, 50);
    }

    showLoading(show) {
        const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
        if (!refreshBtn) return;

        if (show) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i data-feather="loader" class="me-1"></i>Refreshing...';
        } else {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i data-feather="refresh-cw" class="me-1"></i>Refresh';
        }
        feather.replace();
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    startAutoRefresh() {
        if (!this.autoRefreshEnabled) return;

        this.refreshTimer = setInterval(() => {
            this.loadAlerts();
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
}

// Global functions for inline event handlers
function refreshDashboard() {
    if (window.dashboard) {
        window.dashboard.refreshDashboard();
    }
}

function loadAlerts() {
    if (window.dashboard) {
        window.dashboard.loadAlerts();
    }
}

function viewAlert(alertId) {
    if (window.dashboard) {
        window.dashboard.viewAlert(alertId);
    }
}

function resolveAlert(alertId) {
    if (window.dashboard) {
        window.dashboard.resolveAlert(alertId);
    }
}

function resolveCurrentAlert() {
    // This would resolve the currently viewed alert in the modal
    console.log('Resolving current alert');
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new Dashboard();
});
