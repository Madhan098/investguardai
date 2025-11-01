// Real-time Alerts System for InvestGuard AI Dashboard
class RealtimeAlerts {
    constructor() {
        this.isConnected = false;
        this.refreshInterval = 5000; // 5 seconds
        this.notificationInterval = 10000; // 10 seconds
        this.alertPreferences = {};
        this.lastAlertCount = 0;
        this.audioContext = null;
        this.notificationSound = null;
        this.alertHistory = [];
        this.maxHistorySize = 50;
        
        this.init();
    }

    async init() {
        console.log('🚨 Initializing Real-time Alerts System...');
        
        // Load alert preferences
        await this.loadAlertPreferences();
        
        // Initialize audio context for sound alerts
        this.initAudio();
        
        // Start real-time monitoring
        this.startRealtimeMonitoring();
        
        // Setup notification permissions
        this.setupNotificationPermissions();
        
        // Initialize UI components
        this.initUI();
        
        console.log('✅ Real-time Alerts System initialized');
    }

    async loadAlertPreferences() {
        try {
            const response = await fetch('/api/realtime/alert-preferences');
            const data = await response.json();
            
            if (data.success) {
                this.alertPreferences = data.preferences;
                console.log('📋 Alert preferences loaded:', this.alertPreferences);
            }
        } catch (error) {
            console.error('❌ Error loading alert preferences:', error);
            // Use default preferences
            this.alertPreferences = {
                email_alerts: true,
                sms_alerts: false,
                push_notifications: true,
                weekly_digest: true,
                critical_only: false,
                sound_alerts: true,
                alert_frequency: 'immediate'
            };
        }
    }

    initAudio() {
        try {
            // Create audio context for sound alerts
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Create notification sound
            this.createNotificationSound();
            
        } catch (error) {
            console.warn('⚠️ Audio not supported:', error);
        }
    }

    createNotificationSound() {
        if (!this.audioContext) return;
        
        // Create a pleasant notification sound
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(1200, this.audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.3, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.3);
    }

    setupNotificationPermissions() {
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                Notification.requestPermission().then(permission => {
                    console.log('🔔 Notification permission:', permission);
                });
            }
        }
    }

    initUI() {
        // Create real-time alerts container
        this.createAlertsContainer();
        
        // Create notification center
        this.createNotificationCenter();
        
        // Create alert preferences modal
        this.createPreferencesModal();
        
        // Add real-time status indicator
        this.createStatusIndicator();
    }

    createAlertsContainer() {
        // Add real-time alerts section to dashboard
        const alertsContainer = document.createElement('div');
        alertsContainer.id = 'realtime-alerts-container';
        alertsContainer.className = 'realtime-alerts-container';
        alertsContainer.innerHTML = `
            <div class="card border-warning">
                <div class="card-header bg-warning text-dark">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-broadcast-tower me-2"></i>
                            Live Alert Stream
                        </h6>
                        <div class="d-flex gap-2">
                            <button class="btn btn-dark btn-sm" onclick="realtimeAlerts.toggleAlerts()">
                                <i class="fas fa-pause" id="alerts-toggle-icon"></i>
                            </button>
                            <button class="btn btn-dark btn-sm" onclick="realtimeAlerts.openPreferences()">
                                <i class="fas fa-cog"></i>
                            </button>
                            <button class="btn btn-dark btn-sm" onclick="realtimeAlerts.simulateAlert()">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    </div>
                </div>
                <div class="card-body py-2">
                    <div id="live-alerts-stream" class="alerts-stream">
                        <div class="text-center py-3">
                            <div class="spinner-border spinner-border-sm text-warning" role="status">
                                <span class="visually-hidden">Loading live alerts...</span>
                            </div>
                            <p class="text-muted mt-2 mb-0">Connecting to live alert stream...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Insert after SEBI updates section
        const sebiSection = document.querySelector('.py-3 .container');
        if (sebiSection) {
            sebiSection.appendChild(alertsContainer);
        }
    }

    createNotificationCenter() {
        // Create floating notification center
        const notificationCenter = document.createElement('div');
        notificationCenter.id = 'notification-center';
        notificationCenter.className = 'notification-center position-fixed';
        notificationCenter.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        document.body.appendChild(notificationCenter);
    }

    createPreferencesModal() {
        // Create alert preferences modal
        const preferencesModal = document.createElement('div');
        preferencesModal.id = 'alertPreferencesModal';
        preferencesModal.className = 'modal fade';
        preferencesModal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-bell me-2"></i>
                            Alert Preferences
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6 class="fw-bold mb-3">Notification Types</h6>
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="emailAlerts" checked>
                                    <label class="form-check-label" for="emailAlerts">
                                        <i class="fas fa-envelope me-2"></i>Email Alerts
                                    </label>
                                </div>
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="smsAlerts">
                                    <label class="form-check-label" for="smsAlerts">
                                        <i class="fas fa-sms me-2"></i>SMS Alerts
                                    </label>
                                </div>
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="pushNotifications" checked>
                                    <label class="form-check-label" for="pushNotifications">
                                        <i class="fas fa-mobile-alt me-2"></i>Push Notifications
                                    </label>
                                </div>
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="weeklyDigest" checked>
                                    <label class="form-check-label" for="weeklyDigest">
                                        <i class="fas fa-calendar-week me-2"></i>Weekly Digest
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6 class="fw-bold mb-3">Alert Settings</h6>
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="criticalOnly">
                                    <label class="form-check-label" for="criticalOnly">
                                        <i class="fas fa-exclamation-triangle me-2"></i>Critical Alerts Only
                                    </label>
                                </div>
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="soundAlerts" checked>
                                    <label class="form-check-label" for="soundAlerts">
                                        <i class="fas fa-volume-up me-2"></i>Sound Alerts
                                    </label>
                                </div>
                                <div class="mb-3">
                                    <label for="alertFrequency" class="form-label">Alert Frequency</label>
                                    <select class="form-select" id="alertFrequency">
                                        <option value="immediate">Immediate</option>
                                        <option value="hourly">Hourly</option>
                                        <option value="daily">Daily</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="realtimeAlerts.savePreferences()">
                            <i class="fas fa-save me-2"></i>Save Preferences
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(preferencesModal);
    }

    createStatusIndicator() {
        // Add status indicator to dashboard header
        const statusContainer = document.querySelector('.status-indicator-container');
        if (statusContainer) {
            statusContainer.innerHTML = `
                <div class="status-indicator status-online me-2" id="realtime-status"></div>
                <span class="badge bg-success" id="realtime-status-text">Live Monitoring</span>
            `;
        }
    }

    startRealtimeMonitoring() {
        console.log('🔄 Starting real-time monitoring...');
        
        // Initial data load
        this.loadRealtimeData();
        
        // Set up intervals
        this.alertsInterval = setInterval(() => {
            this.loadRealtimeData();
        }, this.refreshInterval);
        
        this.notificationsInterval = setInterval(() => {
            this.checkNotifications();
        }, this.notificationInterval);
        
        this.isConnected = true;
        this.updateStatusIndicator(true);
    }

    async loadRealtimeData() {
        try {
            // Load real-time alerts
            const alertsResponse = await fetch('/api/realtime/alerts');
            const alertsData = await alertsResponse.json();
            
            if (alertsData.success) {
                this.updateAlertsStream(alertsData.alerts);
                this.updateAlertCounts(alertsData);
            }
            
            // Load real-time stats
            const statsResponse = await fetch('/api/realtime/stats');
            const statsData = await statsResponse.json();
            
            if (statsData.success) {
                this.updateDashboardStats(statsData.stats);
            }
            
        } catch (error) {
            console.error('❌ Error loading real-time data:', error);
            this.updateStatusIndicator(false);
        }
    }

    updateAlertsStream(alerts) {
        const streamContainer = document.getElementById('live-alerts-stream');
        if (!streamContainer) return;
        
        if (alerts.length === 0) {
            streamContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-check-circle text-success mb-3" style="font-size: 2rem;"></i>
                    <h6 class="text-muted">No Active Alerts</h6>
                    <p class="text-muted small">System is monitoring for fraudulent activity...</p>
                </div>
            `;
            return;
        }
        
        // Check for new alerts
        const newAlerts = alerts.filter(alert => alert.is_new);
        if (newAlerts.length > 0) {
            this.handleNewAlerts(newAlerts);
        }
        
        // Update alerts display
        const alertsHTML = alerts.slice(0, 10).map(alert => this.createAlertItem(alert)).join('');
        streamContainer.innerHTML = `
            <div class="alerts-list">
                ${alertsHTML}
            </div>
        `;
    }

    createAlertItem(alert) {
        const severityClass = alert.is_critical ? 'danger' : 
                            alert.risk_score >= 7 ? 'warning' : 'info';
        const isNew = alert.is_new ? 'border-start border-4 border-warning' : '';
        
        return `
            <div class="alert-item ${isNew}" data-alert-id="${alert.id}">
                <div class="d-flex align-items-start">
                    <div class="alert-icon me-3">
                        <div class="risk-score-circle bg-${severityClass}">
                            ${alert.risk_score.toFixed(1)}
                        </div>
                    </div>
                    <div class="alert-content flex-grow-1">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">
                                    <span class="badge bg-${severityClass} me-2">${alert.severity.toUpperCase()}</span>
                                    ${alert.source_platform}
                                </h6>
                                <p class="text-muted mb-1 small">${alert.content_preview}</p>
                                <div class="d-flex align-items-center">
                                    <small class="text-muted me-3">
                                        <i class="fas fa-clock me-1"></i>${alert.time_ago}
                                    </small>
                                    <small class="text-muted">
                                        <i class="fas fa-${this.getContentTypeIcon(alert.content_type)} me-1"></i>
                                        ${alert.content_type}
                                    </small>
                                </div>
                            </div>
                            <div class="alert-actions">
                                <button class="btn btn-sm btn-outline-primary" onclick="realtimeAlerts.viewAlert(${alert.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getContentTypeIcon(contentType) {
        const icons = {
            'text': 'file-text',
            'url': 'link',
            'image': 'image',
            'video': 'video'
        };
        return icons[contentType] || 'file';
    }

    handleNewAlerts(newAlerts) {
        newAlerts.forEach(alert => {
            // Play sound if enabled
            if (this.alertPreferences.sound_alerts) {
                this.playNotificationSound();
            }
            
            // Show browser notification if enabled
            if (this.alertPreferences.push_notifications && Notification.permission === 'granted') {
                this.showBrowserNotification(alert);
            }
            
            // Add to notification center
            this.addToNotificationCenter(alert);
            
            // Add to alert history
            this.addToAlertHistory(alert);
        });
    }

    playNotificationSound() {
        if (this.audioContext && this.alertPreferences.sound_alerts) {
            this.createNotificationSound();
        }
    }

    showBrowserNotification(alert) {
        if (Notification.permission === 'granted') {
            const notification = new Notification('🚨 New Fraud Alert', {
                body: `${alert.severity.toUpperCase()} risk detected: ${alert.content_preview}`,
                icon: '/static/images/alert-icon.png',
                tag: `alert-${alert.id}`,
                requireInteraction: alert.is_critical
            });
            
            notification.onclick = () => {
                window.focus();
                this.viewAlert(alert.id);
                notification.close();
            };
            
            // Auto-close after 5 seconds unless critical
            if (!alert.is_critical) {
                setTimeout(() => notification.close(), 5000);
            }
        }
    }

    addToNotificationCenter(alert) {
        const notificationCenter = document.getElementById('notification-center');
        if (!notificationCenter) return;
        
        const notification = document.createElement('div');
        notification.className = 'notification-item alert alert-warning alert-dismissible fade show';
        notification.style.cssText = 'margin-bottom: 10px; max-width: 400px;';
        notification.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="me-3">
                    <i class="fas fa-exclamation-triangle text-warning"></i>
                </div>
                <div class="flex-grow-1">
                    <h6 class="mb-1">New ${alert.severity.toUpperCase()} Alert</h6>
                    <p class="mb-1 small">${alert.content_preview}</p>
                    <small class="text-muted">${alert.time_ago}</small>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        notificationCenter.insertBefore(notification, notificationCenter.firstChild);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }

    addToAlertHistory(alert) {
        this.alertHistory.unshift(alert);
        if (this.alertHistory.length > this.maxHistorySize) {
            this.alertHistory.pop();
        }
    }

    updateAlertCounts(data) {
        // Update dashboard counters
        const totalAlerts = document.getElementById('total-alerts');
        const highRiskCount = document.getElementById('high-risk-count');
        const criticalCount = document.getElementById('critical-count');
        
        if (totalAlerts) {
            this.animateNumber(totalAlerts, data.total_count);
        }
        if (highRiskCount) {
            this.animateNumber(highRiskCount, data.critical_count);
        }
    }

    updateDashboardStats(stats) {
        // Update trend indicators
        const trendElements = document.querySelectorAll('.stat-trend');
        trendElements.forEach(element => {
            const trend = stats.trend;
            const percentage = stats.trend_percentage.toFixed(1);
            
            if (trend === 'up') {
                element.innerHTML = `<small class="text-danger"><i class="fas fa-arrow-up me-1"></i>+${percentage}% from last hour</small>`;
            } else if (trend === 'down') {
                element.innerHTML = `<small class="text-success"><i class="fas fa-arrow-down me-1"></i>-${percentage}% from last hour</small>`;
            } else {
                element.innerHTML = `<small class="text-muted"><i class="fas fa-minus me-1"></i>No change</small>`;
            }
        });
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

    updateStatusIndicator(connected) {
        const statusElement = document.getElementById('realtime-status');
        const statusText = document.getElementById('realtime-status-text');
        
        if (statusElement && statusText) {
            if (connected) {
                statusElement.className = 'status-indicator status-online me-2';
                statusText.textContent = 'Live Monitoring';
                statusText.className = 'badge bg-success';
            } else {
                statusElement.className = 'status-indicator status-danger me-2';
                statusText.textContent = 'Connection Lost';
                statusText.className = 'badge bg-danger';
            }
        }
    }

    async checkNotifications() {
        try {
            const response = await fetch('/api/realtime/notifications');
            const data = await response.json();
            
            if (data.success && data.notifications.length > 0) {
                data.notifications.forEach(notification => {
                    this.showBrowserNotification(notification);
                });
            }
        } catch (error) {
            console.error('❌ Error checking notifications:', error);
        }
    }

    // UI Control Methods
    toggleAlerts() {
        const toggleIcon = document.getElementById('alerts-toggle-icon');
        if (this.isConnected) {
            this.stopRealtimeMonitoring();
            toggleIcon.className = 'fas fa-play';
        } else {
            this.startRealtimeMonitoring();
            toggleIcon.className = 'fas fa-pause';
        }
    }

    stopRealtimeMonitoring() {
        if (this.alertsInterval) {
            clearInterval(this.alertsInterval);
        }
        if (this.notificationsInterval) {
            clearInterval(this.notificationsInterval);
        }
        this.isConnected = false;
        this.updateStatusIndicator(false);
    }

    openPreferences() {
        const modal = new bootstrap.Modal(document.getElementById('alertPreferencesModal'));
        
        // Populate current preferences
        document.getElementById('emailAlerts').checked = this.alertPreferences.email_alerts;
        document.getElementById('smsAlerts').checked = this.alertPreferences.sms_alerts;
        document.getElementById('pushNotifications').checked = this.alertPreferences.push_notifications;
        document.getElementById('weeklyDigest').checked = this.alertPreferences.weekly_digest;
        document.getElementById('criticalOnly').checked = this.alertPreferences.critical_only;
        document.getElementById('soundAlerts').checked = this.alertPreferences.sound_alerts;
        document.getElementById('alertFrequency').value = this.alertPreferences.alert_frequency;
        
        modal.show();
    }

    async savePreferences() {
        const preferences = {
            email_alerts: document.getElementById('emailAlerts').checked,
            sms_alerts: document.getElementById('smsAlerts').checked,
            push_notifications: document.getElementById('pushNotifications').checked,
            weekly_digest: document.getElementById('weeklyDigest').checked,
            critical_only: document.getElementById('criticalOnly').checked,
            sound_alerts: document.getElementById('soundAlerts').checked,
            alert_frequency: document.getElementById('alertFrequency').value
        };
        
        try {
            const response = await fetch('/api/realtime/alert-preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(preferences)
            });
            
            const data = await response.json();
            if (data.success) {
                this.alertPreferences = preferences;
                this.showNotification('Preferences saved successfully!', 'success');
                bootstrap.Modal.getInstance(document.getElementById('alertPreferencesModal')).hide();
            }
        } catch (error) {
            console.error('❌ Error saving preferences:', error);
            this.showNotification('Failed to save preferences', 'error');
        }
    }

    async simulateAlert() {
        try {
            const response = await fetch('/api/realtime/simulate-alert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            if (data.success) {
                this.showNotification('Test alert created!', 'success');
                // Refresh data immediately
                this.loadRealtimeData();
            }
        } catch (error) {
            console.error('❌ Error simulating alert:', error);
            this.showNotification('Failed to create test alert', 'error');
        }
    }

    viewAlert(alertId) {
        // Implement alert viewing logic
        console.log('Viewing alert:', alertId);
        // You can implement a modal or redirect to alert details
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize real-time alerts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.realtimeAlerts = new RealtimeAlerts();
});

// Global functions for inline event handlers
function toggleRealtimeAlerts() {
    if (window.realtimeAlerts) {
        window.realtimeAlerts.toggleAlerts();
    }
}

function openAlertPreferences() {
    if (window.realtimeAlerts) {
        window.realtimeAlerts.openPreferences();
    }
}

function simulateTestAlert() {
    if (window.realtimeAlerts) {
        window.realtimeAlerts.simulateAlert();
    }
}
