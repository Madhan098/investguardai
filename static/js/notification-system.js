// Advanced Notification System for Real-time Alerts
class NotificationSystem {
    constructor() {
        this.permissions = {
            notifications: false,
            audio: false,
            vibration: false
        };
        this.soundEnabled = true;
        this.vibrationEnabled = true;
        this.notificationQueue = [];
        this.maxQueueSize = 10;
        this.audioContext = null;
        this.notificationSounds = {};
        
        this.init();
    }

    async init() {
        console.log('🔔 Initializing Advanced Notification System...');
        
        // Request permissions
        await this.requestPermissions();
        
        // Initialize audio context
        this.initAudioContext();
        
        // Create notification sounds
        this.createNotificationSounds();
        
        // Setup notification event listeners
        this.setupEventListeners();
        
        console.log('✅ Notification System initialized');
    }

    async requestPermissions() {
        // Request notification permission
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                const permission = await Notification.requestPermission();
                this.permissions.notifications = permission === 'granted';
            } else {
                this.permissions.notifications = Notification.permission === 'granted';
            }
        }

        // Check audio support
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.permissions.audio = true;
        } catch (error) {
            console.warn('⚠️ Audio not supported:', error);
            this.permissions.audio = false;
        }

        // Check vibration support
        if ('vibrate' in navigator) {
            this.permissions.vibration = true;
        }

        console.log('📋 Permissions:', this.permissions);
    }

    initAudioContext() {
        if (!this.audioContext) return;
        
        // Resume audio context on user interaction
        document.addEventListener('click', () => {
            if (this.audioContext.state === 'suspended') {
                this.audioContext.resume();
            }
        }, { once: true });
    }

    createNotificationSounds() {
        if (!this.audioContext) return;

        // Critical alert sound (urgent)
        this.notificationSounds.critical = () => {
            this.playTone(800, 0.3, 0.1);
            setTimeout(() => this.playTone(1000, 0.3, 0.1), 200);
            setTimeout(() => this.playTone(1200, 0.3, 0.1), 400);
        };

        // High risk alert sound
        this.notificationSounds.high = () => {
            this.playTone(600, 0.2, 0.1);
            setTimeout(() => this.playTone(800, 0.2, 0.1), 150);
        };

        // Medium risk alert sound
        this.notificationSounds.medium = () => {
            this.playTone(500, 0.15, 0.1);
        };

        // Low risk alert sound
        this.notificationSounds.low = () => {
            this.playTone(400, 0.1, 0.1);
        };

        // Success notification sound
        this.notificationSounds.success = () => {
            this.playTone(600, 0.1, 0.1);
            setTimeout(() => this.playTone(800, 0.1, 0.1), 100);
            setTimeout(() => this.playTone(1000, 0.1, 0.1), 200);
        };

        // Error notification sound
        this.notificationSounds.error = () => {
            this.playTone(300, 0.2, 0.1);
            setTimeout(() => this.playTone(200, 0.2, 0.1), 200);
        };
    }

    playTone(frequency, duration, volume = 0.1) {
        if (!this.audioContext || !this.soundEnabled) return;

        try {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(volume, this.audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration);
        } catch (error) {
            console.warn('⚠️ Audio playback failed:', error);
        }
    }

    setupEventListeners() {
        // Listen for visibility changes to show notifications when tab is not active
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.notificationQueue.length > 0) {
                this.processNotificationQueue();
            }
        });

        // Listen for focus events to clear notification queue
        window.addEventListener('focus', () => {
            this.clearNotificationQueue();
        });
    }

    // Main notification method
    async showNotification(notification) {
        const notificationData = {
            id: notification.id || Date.now(),
            type: notification.type || 'info',
            title: notification.title || 'New Alert',
            message: notification.message || '',
            severity: notification.severity || 'medium',
            riskScore: notification.riskScore || 0,
            timestamp: new Date().toISOString(),
            requiresAttention: notification.requiresAttention || false,
            actions: notification.actions || [],
            data: notification.data || {}
        };

        // Add to queue
        this.addToQueue(notificationData);

        // Show different types of notifications
        await Promise.all([
            this.showBrowserNotification(notificationData),
            this.showInAppNotification(notificationData),
            this.playNotificationSound(notificationData),
            this.vibrateDevice(notificationData)
        ]);

        // Log notification
        console.log('🔔 Notification sent:', notificationData);
    }

    addToQueue(notification) {
        this.notificationQueue.unshift(notification);
        
        // Limit queue size
        if (this.notificationQueue.length > this.maxQueueSize) {
            this.notificationQueue = this.notificationQueue.slice(0, this.maxQueueSize);
        }
    }

    async showBrowserNotification(notification) {
        if (!this.permissions.notifications) return;

        try {
            const browserNotification = new Notification(notification.title, {
                body: notification.message,
                icon: '/static/images/alert-icon.png',
                badge: '/static/images/badge-icon.png',
                tag: `alert-${notification.id}`,
                requireInteraction: notification.requiresAttention,
                silent: !this.soundEnabled,
                vibrate: this.vibrationEnabled ? [200, 100, 200] : undefined,
                actions: notification.actions.map(action => ({
                    action: action.id,
                    title: action.title,
                    icon: action.icon
                }))
            });

            // Handle notification click
            browserNotification.onclick = () => {
                window.focus();
                this.handleNotificationClick(notification);
                browserNotification.close();
            };

            // Handle notification actions
            browserNotification.addEventListener('click', (event) => {
                if (event.action) {
                    this.handleNotificationAction(notification, event.action);
                }
            });

            // Auto-close after timeout (unless critical)
            if (!notification.requiresAttention) {
                setTimeout(() => browserNotification.close(), 5000);
            }

        } catch (error) {
            console.error('❌ Browser notification failed:', error);
        }
    }

    showInAppNotification(notification) {
        // Create in-app notification element
        const notificationElement = document.createElement('div');
        notificationElement.className = `notification-item alert alert-${this.getSeverityClass(notification.severity)} alert-dismissible fade show`;
        notificationElement.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 350px; max-width: 500px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);';
        notificationElement.setAttribute('data-notification-id', notification.id);

        notificationElement.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="me-3">
                    <i class="fas fa-${this.getSeverityIcon(notification.severity)} text-${this.getSeverityClass(notification.severity)}"></i>
                </div>
                <div class="flex-grow-1">
                    <h6 class="mb-1 fw-bold">${notification.title}</h6>
                    <p class="mb-2 small">${notification.message}</p>
                    ${notification.riskScore > 0 ? `<div class="mb-2"><span class="badge bg-${this.getSeverityClass(notification.severity)}">Risk Score: ${notification.riskScore}/10</span></div>` : ''}
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            ${new Date(notification.timestamp).toLocaleTimeString()}
                        </small>
                        <div class="notification-actions">
                            ${notification.actions.map(action => `
                                <button class="btn btn-sm btn-outline-${this.getSeverityClass(notification.severity)} me-1" 
                                        onclick="notificationSystem.handleNotificationAction('${notification.id}', '${action.id}')">
                                    ${action.title}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Add to notification center
        const notificationCenter = document.getElementById('notification-center');
        if (notificationCenter) {
            notificationCenter.insertBefore(notificationElement, notificationCenter.firstChild);
        } else {
            document.body.appendChild(notificationElement);
        }

        // Auto-remove after timeout
        setTimeout(() => {
            if (notificationElement.parentNode) {
                notificationElement.remove();
            }
        }, notification.requiresAttention ? 15000 : 8000);

        // Add animation
        notificationElement.style.animation = 'slideInRight 0.5s ease';
    }

    playNotificationSound(notification) {
        if (!this.soundEnabled || !this.permissions.audio) return;

        const soundType = this.getSoundType(notification.severity);
        if (this.notificationSounds[soundType]) {
            this.notificationSounds[soundType]();
        }
    }

    vibrateDevice(notification) {
        if (!this.vibrationEnabled || !this.permissions.vibration) return;

        const vibrationPattern = this.getVibrationPattern(notification.severity);
        if (vibrationPattern) {
            navigator.vibrate(vibrationPattern);
        }
    }

    getSeverityClass(severity) {
        const classes = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'success',
            'info': 'primary',
            'success': 'success',
            'error': 'danger'
        };
        return classes[severity] || 'info';
    }

    getSeverityIcon(severity) {
        const icons = {
            'critical': 'exclamation-triangle',
            'high': 'exclamation-circle',
            'medium': 'info-circle',
            'low': 'check-circle',
            'info': 'info-circle',
            'success': 'check-circle',
            'error': 'times-circle'
        };
        return icons[severity] || 'info-circle';
    }

    getSoundType(severity) {
        const soundTypes = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
            'success': 'success',
            'error': 'error'
        };
        return soundTypes[severity] || 'medium';
    }

    getVibrationPattern(severity) {
        const patterns = {
            'critical': [200, 100, 200, 100, 200],
            'high': [200, 100, 200],
            'medium': [200],
            'low': [100],
            'success': [100, 50, 100],
            'error': [300, 100, 300]
        };
        return patterns[severity] || [200];
    }

    handleNotificationClick(notification) {
        console.log('🔔 Notification clicked:', notification);
        
        // Focus on relevant section or open modal
        if (notification.data.section) {
            const section = document.getElementById(notification.data.section);
            if (section) {
                section.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }

    handleNotificationAction(notificationId, actionId) {
        console.log('🔔 Notification action:', notificationId, actionId);
        
        // Handle different actions
        switch (actionId) {
            case 'view':
                this.viewNotification(notificationId);
                break;
            case 'dismiss':
                this.dismissNotification(notificationId);
                break;
            case 'resolve':
                this.resolveNotification(notificationId);
                break;
            default:
                console.log('Unknown action:', actionId);
        }
    }

    viewNotification(notificationId) {
        // Find and highlight the notification
        const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
        if (notificationElement) {
            notificationElement.style.border = '2px solid #007bff';
            notificationElement.style.boxShadow = '0 0 10px rgba(0, 123, 255, 0.5)';
        }
    }

    dismissNotification(notificationId) {
        const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
        if (notificationElement) {
            notificationElement.remove();
        }
    }

    resolveNotification(notificationId) {
        // Mark notification as resolved
        console.log('✅ Notification resolved:', notificationId);
        this.dismissNotification(notificationId);
    }

    processNotificationQueue() {
        // Process queued notifications when tab becomes visible
        this.notificationQueue.forEach(notification => {
            this.showInAppNotification(notification);
        });
    }

    clearNotificationQueue() {
        this.notificationQueue = [];
    }

    // Settings management
    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        console.log('🔊 Sound notifications:', this.soundEnabled ? 'enabled' : 'disabled');
        return this.soundEnabled;
    }

    toggleVibration() {
        this.vibrationEnabled = !this.vibrationEnabled;
        console.log('📳 Vibration notifications:', this.vibrationEnabled ? 'enabled' : 'disabled');
        return this.vibrationEnabled;
    }

    // Test notifications
    testNotification(type = 'info') {
        const testNotifications = {
            'critical': {
                title: '🚨 Critical Alert',
                message: 'High-risk fraud detected requiring immediate attention',
                severity: 'critical',
                riskScore: 9.5,
                requiresAttention: true
            },
            'high': {
                title: '⚠️ High Risk Alert',
                message: 'Suspicious investment scheme detected',
                severity: 'high',
                riskScore: 7.8
            },
            'medium': {
                title: 'ℹ️ Medium Risk Alert',
                message: 'Potential fraud indicators detected',
                severity: 'medium',
                riskScore: 5.2
            },
            'success': {
                title: '✅ Success',
                message: 'Alert resolved successfully',
                severity: 'success'
            },
            'error': {
                title: '❌ Error',
                message: 'Failed to process alert',
                severity: 'error'
            }
        };

        const notification = testNotifications[type] || testNotifications['info'];
        this.showNotification(notification);
    }

    // Get notification statistics
    getStats() {
        return {
            totalNotifications: this.notificationQueue.length,
            permissions: this.permissions,
            soundEnabled: this.soundEnabled,
            vibrationEnabled: this.vibrationEnabled
        };
    }
}

// Initialize notification system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.notificationSystem = new NotificationSystem();
});

// Global functions for testing
function testNotification(type) {
    if (window.notificationSystem) {
        window.notificationSystem.testNotification(type);
    }
}

function toggleNotificationSound() {
    if (window.notificationSystem) {
        return window.notificationSystem.toggleSound();
    }
}

function toggleNotificationVibration() {
    if (window.notificationSystem) {
        return window.notificationSystem.toggleVibration();
    }
}
