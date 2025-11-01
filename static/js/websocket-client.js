// WebSocket Client for Real-time Alerts
class WebSocketAlerts {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 5000; // 5 seconds
        this.heartbeatInterval = 30000; // 30 seconds
        this.heartbeatTimer = null;
        
        this.init();
    }

    init() {
        console.log('🔌 Initializing WebSocket connection...');
        this.connect();
    }

    connect() {
        try {
            // Connect to WebSocket server
            this.socket = io();
            
            // Connection event handlers
            this.socket.on('connect', () => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.startHeartbeat();
                this.joinDashboard();
                this.updateConnectionStatus(true);
            });
            
            this.socket.on('disconnect', () => {
                console.log('❌ WebSocket disconnected');
                this.isConnected = false;
                this.stopHeartbeat();
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            });
            
            this.socket.on('connection_status', (data) => {
                console.log('📡 Connection status:', data);
            });
            
            this.socket.on('joined_dashboard', (data) => {
                console.log('📊 Joined dashboard:', data);
                this.requestInitialData();
            });
            
            this.socket.on('left_dashboard', (data) => {
                console.log('📊 Left dashboard:', data);
            });
            
            // Real-time data handlers
            this.socket.on('alerts_data', (data) => {
                this.handleAlertsData(data);
            });
            
            this.socket.on('stats_data', (data) => {
                this.handleStatsData(data);
            });
            
            this.socket.on('new_alert', (data) => {
                this.handleNewAlert(data);
            });
            
            this.socket.on('stats_update', (data) => {
                this.handleStatsUpdate(data);
            });
            
            this.socket.on('notification', (data) => {
                this.handleNotification(data);
            });
            
            this.socket.on('error', (data) => {
                console.error('❌ WebSocket error:', data);
                this.showNotification(data.message, 'error');
            });
            
        } catch (error) {
            console.error('❌ WebSocket connection failed:', error);
            this.attemptReconnect();
        }
    }

    joinDashboard() {
        if (this.socket && this.isConnected) {
            this.socket.emit('join_dashboard');
        }
    }

    leaveDashboard() {
        if (this.socket && this.isConnected) {
            this.socket.emit('leave_dashboard');
        }
    }

    requestInitialData() {
        if (this.socket && this.isConnected) {
            this.socket.emit('request_alerts');
            this.socket.emit('request_stats');
        }
    }

    simulateAlert() {
        if (this.socket && this.isConnected) {
            this.socket.emit('simulate_alert');
        }
    }

    handleAlertsData(data) {
        console.log('📊 Received alerts data:', data);
        
        // Update alerts stream
        this.updateAlertsStream(data.alerts);
        
        // Update alert counts
        this.updateAlertCounts(data);
        
        // Update dashboard counters
        this.updateDashboardCounters(data);
    }

    handleStatsData(data) {
        console.log('📈 Received stats data:', data);
        
        // Update dashboard statistics
        this.updateDashboardStats(data);
        
        // Update trend indicators
        this.updateTrendIndicators(data);
    }

    handleNewAlert(alertData) {
        console.log('🚨 New alert received:', alertData);
        
        // Play notification sound
        this.playNotificationSound();
        
        // Show browser notification
        this.showBrowserNotification(alertData);
        
        // Add to notification center
        this.addToNotificationCenter(alertData);
        
        // Update alerts stream with new alert
        this.addNewAlertToStream(alertData);
        
        // Update counters
        this.incrementAlertCounters();
    }

    handleStatsUpdate(data) {
        console.log('📊 Stats update received:', data);
        this.updateDashboardStats(data);
    }

    handleNotification(notificationData) {
        console.log('🔔 Notification received:', notificationData);
        
        // Show critical notification
        this.showCriticalNotification(notificationData);
        
        // Play critical alert sound
        this.playCriticalAlertSound();
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
        
        const alertsHTML = alerts.slice(0, 10).map(alert => this.createAlertItem(alert)).join('');
        streamContainer.innerHTML = `
            <div class="alerts-list">
                ${alertsHTML}
            </div>
        `;
    }

    addNewAlertToStream(alertData) {
        const streamContainer = document.getElementById('live-alerts-stream');
        if (!streamContainer) return;
        
        // Create new alert item
        const alertItem = this.createAlertItem(alertData);
        
        // Add to top of stream
        const alertsList = streamContainer.querySelector('.alerts-list');
        if (alertsList) {
            alertsList.insertAdjacentHTML('afterbegin', alertItem);
            
            // Remove excess items (keep only 10)
            const items = alertsList.querySelectorAll('.alert-item');
            if (items.length > 10) {
                items[items.length - 1].remove();
            }
        }
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
                                <button class="btn btn-sm btn-outline-primary" onclick="websocketAlerts.viewAlert(${alert.id})">
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

    updateDashboardCounters(data) {
        // Update all dashboard counters
        const counters = {
            'total-alerts': data.total_count,
            'high-risk-count': data.critical_count,
            'medium-risk-count': data.total_count - data.critical_count,
            'low-risk-count': data.new_count
        };
        
        Object.entries(counters).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateNumber(element, value);
            }
        });
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

    updateTrendIndicators(data) {
        // Update trend indicators with new data
        const trendElements = document.querySelectorAll('.stat-trend');
        trendElements.forEach(element => {
            const trend = data.trend;
            const percentage = data.trend_percentage.toFixed(1);
            
            if (trend === 'up') {
                element.innerHTML = `<small class="text-danger"><i class="fas fa-arrow-up me-1"></i>+${percentage}% from last hour</small>`;
            } else if (trend === 'down') {
                element.innerHTML = `<small class="text-success"><i class="fas fa-arrow-down me-1"></i>-${percentage}% from last hour</small>`;
            } else {
                element.innerHTML = `<small class="text-muted"><i class="fas fa-minus me-1"></i>No change</small>`;
            }
        });
    }

    incrementAlertCounters() {
        // Increment alert counters for new alerts
        const totalAlerts = document.getElementById('total-alerts');
        const highRiskCount = document.getElementById('high-risk-count');
        
        if (totalAlerts) {
            const currentValue = parseInt(totalAlerts.textContent) || 0;
            this.animateNumber(totalAlerts, currentValue + 1);
        }
        
        if (highRiskCount) {
            const currentValue = parseInt(highRiskCount.textContent) || 0;
            this.animateNumber(highRiskCount, currentValue + 1);
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

    playNotificationSound() {
        // Play notification sound for new alerts
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(1200, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0, audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            console.warn('⚠️ Audio not supported:', error);
        }
    }

    playCriticalAlertSound() {
        // Play critical alert sound
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // More urgent sound for critical alerts
            oscillator.frequency.setValueAtTime(1000, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(1500, audioContext.currentTime + 0.2);
            
            gainNode.gain.setValueAtTime(0, audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.5, audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.warn('⚠️ Audio not supported:', error);
        }
    }

    showBrowserNotification(alertData) {
        if (Notification.permission === 'granted') {
            const notification = new Notification('🚨 New Fraud Alert', {
                body: `${alertData.severity.toUpperCase()} risk detected: ${alertData.content_preview}`,
                icon: '/static/images/alert-icon.png',
                tag: `alert-${alertData.id}`,
                requireInteraction: alertData.is_critical
            });
            
            notification.onclick = () => {
                window.focus();
                this.viewAlert(alertData.id);
                notification.close();
            };
            
            // Auto-close after 5 seconds unless critical
            if (!alertData.is_critical) {
                setTimeout(() => notification.close(), 5000);
            }
        }
    }

    showCriticalNotification(notificationData) {
        // Show critical notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 400px; max-width: 500px;';
        notification.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="me-3">
                    <i class="fas fa-exclamation-triangle text-danger"></i>
                </div>
                <div class="flex-grow-1">
                    <h6 class="mb-1">${notificationData.title}</h6>
                    <p class="mb-1">${notificationData.message}</p>
                    <small class="text-muted">Risk Score: ${notificationData.risk_score}/10</small>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }

    addToNotificationCenter(alertData) {
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
                    <h6 class="mb-1">New ${alertData.severity.toUpperCase()} Alert</h6>
                    <p class="mb-1 small">${alertData.content_preview}</p>
                    <small class="text-muted">${alertData.time_ago}</small>
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

    updateConnectionStatus(connected) {
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

    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            if (this.socket && this.isConnected) {
                this.socket.emit('ping');
            }
        }, this.heartbeatInterval);
    }

    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.error('❌ Max reconnection attempts reached');
            this.showNotification('Connection lost. Please refresh the page.', 'error');
        }
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

    viewAlert(alertId) {
        console.log('Viewing alert:', alertId);
        // Implement alert viewing logic
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
        this.isConnected = false;
        this.stopHeartbeat();
    }
}

// Initialize WebSocket client when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.websocketAlerts = new WebSocketAlerts();
});

// Global functions for inline event handlers
function simulateWebSocketAlert() {
    if (window.websocketAlerts) {
        window.websocketAlerts.simulateAlert();
    }
}
