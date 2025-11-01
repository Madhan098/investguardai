// Alert Preferences Management System
class AlertPreferences {
    constructor() {
        this.preferences = {
            email_alerts: true,
            sms_alerts: false,
            push_notifications: true,
            weekly_digest: true,
            critical_only: false,
            sound_alerts: true,
            vibration_alerts: true,
            alert_frequency: 'immediate',
            risk_threshold: 5.0,
            notification_timing: {
                immediate: true,
                hourly: false,
                daily: false
            },
            channels: {
                dashboard: true,
                email: true,
                sms: false,
                push: true,
                browser: true
            },
            severity_filters: {
                critical: true,
                high: true,
                medium: true,
                low: false
            },
            content_filters: {
                fraud_detection: true,
                market_anomalies: true,
                sebi_updates: true,
                advisor_verification: true,
                portfolio_alerts: false
            }
        };
        
        this.init();
    }

    async init() {
        console.log('⚙️ Initializing Alert Preferences System...');
        
        // Load saved preferences
        await this.loadPreferences();
        
        // Create preferences UI
        this.createPreferencesUI();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ Alert Preferences System initialized');
    }

    async loadPreferences() {
        try {
            const response = await fetch('/api/realtime/alert-preferences');
            const data = await response.json();
            
            if (data.success) {
                this.preferences = { ...this.preferences, ...data.preferences };
                console.log('📋 Preferences loaded:', this.preferences);
            }
        } catch (error) {
            console.error('❌ Error loading preferences:', error);
            // Use default preferences
        }
    }

    async savePreferences() {
        try {
            const response = await fetch('/api/realtime/alert-preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.preferences)
            });
            
            const data = await response.json();
            if (data.success) {
                console.log('✅ Preferences saved successfully');
                this.showNotification('Preferences saved successfully!', 'success');
                return true;
            } else {
                throw new Error(data.error || 'Failed to save preferences');
            }
        } catch (error) {
            console.error('❌ Error saving preferences:', error);
            this.showNotification('Failed to save preferences', 'error');
            return false;
        }
    }

    createPreferencesUI() {
        // Create comprehensive preferences modal
        const preferencesModal = document.createElement('div');
        preferencesModal.id = 'alertPreferencesModal';
        preferencesModal.className = 'modal fade';
        preferencesModal.innerHTML = `
            <div class="modal-dialog modal-xl">
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
                            <!-- Notification Types -->
                            <div class="col-md-6 mb-4">
                                <h6 class="fw-bold mb-3">
                                    <i class="fas fa-bell me-2"></i>
                                    Notification Types
                                </h6>
                                
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="emailAlerts" ${this.preferences.email_alerts ? 'checked' : ''}>
                                    <label class="form-check-label" for="emailAlerts">
                                        <i class="fas fa-envelope me-2"></i>Email Alerts
                                    </label>
                                </div>
                                
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="smsAlerts" ${this.preferences.sms_alerts ? 'checked' : ''}>
                                    <label class="form-check-label" for="smsAlerts">
                                        <i class="fas fa-sms me-2"></i>SMS Alerts
                                    </label>
                                </div>
                                
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="pushNotifications" ${this.preferences.push_notifications ? 'checked' : ''}>
                                    <label class="form-check-label" for="pushNotifications">
                                        <i class="fas fa-mobile-alt me-2"></i>Push Notifications
                                    </label>
                                </div>
                                
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="weeklyDigest" ${this.preferences.weekly_digest ? 'checked' : ''}>
                                    <label class="form-check-label" for="weeklyDigest">
                                        <i class="fas fa-calendar-week me-2"></i>Weekly Digest
                                    </label>
                                </div>
                            </div>
                            
                            <!-- Alert Settings -->
                            <div class="col-md-6 mb-4">
                                <h6 class="fw-bold mb-3">
                                    <i class="fas fa-cog me-2"></i>
                                    Alert Settings
                                </h6>
                                
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="criticalOnly" ${this.preferences.critical_only ? 'checked' : ''}>
                                    <label class="form-check-label" for="criticalOnly">
                                        <i class="fas fa-exclamation-triangle me-2"></i>Critical Alerts Only
                                    </label>
                                </div>
                                
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="soundAlerts" ${this.preferences.sound_alerts ? 'checked' : ''}>
                                    <label class="form-check-label" for="soundAlerts">
                                        <i class="fas fa-volume-up me-2"></i>Sound Alerts
                                    </label>
                                </div>
                                
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" id="vibrationAlerts" ${this.preferences.vibration_alerts ? 'checked' : ''}>
                                    <label class="form-check-label" for="vibrationAlerts">
                                        <i class="fas fa-mobile-alt me-2"></i>Vibration Alerts
                                    </label>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="alertFrequency" class="form-label">Alert Frequency</label>
                                    <select class="form-select" id="alertFrequency">
                                        <option value="immediate" ${this.preferences.alert_frequency === 'immediate' ? 'selected' : ''}>Immediate</option>
                                        <option value="hourly" ${this.preferences.alert_frequency === 'hourly' ? 'selected' : ''}>Hourly</option>
                                        <option value="daily" ${this.preferences.alert_frequency === 'daily' ? 'selected' : ''}>Daily</option>
                                    </select>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="riskThreshold" class="form-label">Risk Threshold</label>
                                    <input type="range" class="form-range" id="riskThreshold" min="1" max="10" step="0.5" value="${this.preferences.risk_threshold}">
                                    <div class="d-flex justify-content-between">
                                        <small class="text-muted">Low (1.0)</small>
                                        <small class="text-muted">High (10.0)</small>
                                    </div>
                                    <div class="text-center mt-1">
                                        <span class="badge bg-primary" id="riskThresholdValue">${this.preferences.risk_threshold}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Severity Filters -->
                        <div class="row mb-4">
                            <div class="col-12">
                                <h6 class="fw-bold mb-3">
                                    <i class="fas fa-filter me-2"></i>
                                    Severity Filters
                                </h6>
                                <div class="row">
                                    <div class="col-md-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="criticalFilter" ${this.preferences.severity_filters.critical ? 'checked' : ''}>
                                            <label class="form-check-label text-danger" for="criticalFilter">
                                                <i class="fas fa-exclamation-triangle me-1"></i>Critical
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="highFilter" ${this.preferences.severity_filters.high ? 'checked' : ''}>
                                            <label class="form-check-label text-warning" for="highFilter">
                                                <i class="fas fa-exclamation-circle me-1"></i>High
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="mediumFilter" ${this.preferences.severity_filters.medium ? 'checked' : ''}>
                                            <label class="form-check-label text-info" for="mediumFilter">
                                                <i class="fas fa-info-circle me-1"></i>Medium
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="lowFilter" ${this.preferences.severity_filters.low ? 'checked' : ''}>
                                            <label class="form-check-label text-success" for="lowFilter">
                                                <i class="fas fa-check-circle me-1"></i>Low
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Content Filters -->
                        <div class="row mb-4">
                            <div class="col-12">
                                <h6 class="fw-bold mb-3">
                                    <i class="fas fa-tags me-2"></i>
                                    Content Filters
                                </h6>
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="fraudDetection" ${this.preferences.content_filters.fraud_detection ? 'checked' : ''}>
                                            <label class="form-check-label" for="fraudDetection">
                                                <i class="fas fa-shield-alt me-1"></i>Fraud Detection
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="marketAnomalies" ${this.preferences.content_filters.market_anomalies ? 'checked' : ''}>
                                            <label class="form-check-label" for="marketAnomalies">
                                                <i class="fas fa-chart-line me-1"></i>Market Anomalies
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="sebiUpdates" ${this.preferences.content_filters.sebi_updates ? 'checked' : ''}>
                                            <label class="form-check-label" for="sebiUpdates">
                                                <i class="fas fa-broadcast-tower me-1"></i>SEBI Updates
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="advisorVerification" ${this.preferences.content_filters.advisor_verification ? 'checked' : ''}>
                                            <label class="form-check-label" for="advisorVerification">
                                                <i class="fas fa-user-check me-1"></i>Advisor Verification
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="portfolioAlerts" ${this.preferences.content_filters.portfolio_alerts ? 'checked' : ''}>
                                            <label class="form-check-label" for="portfolioAlerts">
                                                <i class="fas fa-briefcase me-1"></i>Portfolio Alerts
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Test Notifications -->
                        <div class="row mb-4">
                            <div class="col-12">
                                <h6 class="fw-bold mb-3">
                                    <i class="fas fa-vial me-2"></i>
                                    Test Notifications
                                </h6>
                                <div class="d-flex gap-2 flex-wrap">
                                    <button class="btn btn-outline-danger btn-sm" onclick="alertPreferences.testNotification('critical')">
                                        <i class="fas fa-exclamation-triangle me-1"></i>Test Critical
                                    </button>
                                    <button class="btn btn-outline-warning btn-sm" onclick="alertPreferences.testNotification('high')">
                                        <i class="fas fa-exclamation-circle me-1"></i>Test High
                                    </button>
                                    <button class="btn btn-outline-info btn-sm" onclick="alertPreferences.testNotification('medium')">
                                        <i class="fas fa-info-circle me-1"></i>Test Medium
                                    </button>
                                    <button class="btn btn-outline-success btn-sm" onclick="alertPreferences.testNotification('success')">
                                        <i class="fas fa-check-circle me-1"></i>Test Success
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>Cancel
                        </button>
                        <button type="button" class="btn btn-outline-primary" onclick="alertPreferences.resetToDefaults()">
                            <i class="fas fa-undo me-2"></i>Reset to Defaults
                        </button>
                        <button type="button" class="btn btn-primary" onclick="alertPreferences.savePreferences()">
                            <i class="fas fa-save me-2"></i>Save Preferences
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(preferencesModal);
    }

    setupEventListeners() {
        // Risk threshold slider
        const riskThreshold = document.getElementById('riskThreshold');
        if (riskThreshold) {
            riskThreshold.addEventListener('input', (e) => {
                document.getElementById('riskThresholdValue').textContent = e.target.value;
            });
        }

        // Real-time preference updates
        const checkboxes = document.querySelectorAll('#alertPreferencesModal input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updatePreferenceFromUI();
            });
        });

        const selects = document.querySelectorAll('#alertPreferencesModal select');
        selects.forEach(select => {
            select.addEventListener('change', () => {
                this.updatePreferenceFromUI();
            });
        });
    }

    updatePreferenceFromUI() {
        // Update preferences from UI elements
        this.preferences.email_alerts = document.getElementById('emailAlerts')?.checked || false;
        this.preferences.sms_alerts = document.getElementById('smsAlerts')?.checked || false;
        this.preferences.push_notifications = document.getElementById('pushNotifications')?.checked || false;
        this.preferences.weekly_digest = document.getElementById('weeklyDigest')?.checked || false;
        this.preferences.critical_only = document.getElementById('criticalOnly')?.checked || false;
        this.preferences.sound_alerts = document.getElementById('soundAlerts')?.checked || false;
        this.preferences.vibration_alerts = document.getElementById('vibrationAlerts')?.checked || false;
        this.preferences.alert_frequency = document.getElementById('alertFrequency')?.value || 'immediate';
        this.preferences.risk_threshold = parseFloat(document.getElementById('riskThreshold')?.value) || 5.0;
        
        // Update severity filters
        this.preferences.severity_filters.critical = document.getElementById('criticalFilter')?.checked || false;
        this.preferences.severity_filters.high = document.getElementById('highFilter')?.checked || false;
        this.preferences.severity_filters.medium = document.getElementById('mediumFilter')?.checked || false;
        this.preferences.severity_filters.low = document.getElementById('lowFilter')?.checked || false;
        
        // Update content filters
        this.preferences.content_filters.fraud_detection = document.getElementById('fraudDetection')?.checked || false;
        this.preferences.content_filters.market_anomalies = document.getElementById('marketAnomalies')?.checked || false;
        this.preferences.content_filters.sebi_updates = document.getElementById('sebiUpdates')?.checked || false;
        this.preferences.content_filters.advisor_verification = document.getElementById('advisorVerification')?.checked || false;
        this.preferences.content_filters.portfolio_alerts = document.getElementById('portfolioAlerts')?.checked || false;
    }

    openPreferences() {
        const modal = new bootstrap.Modal(document.getElementById('alertPreferencesModal'));
        modal.show();
    }

    async savePreferences() {
        this.updatePreferenceFromUI();
        const success = await this.savePreferences();
        
        if (success) {
            // Update notification system settings
            if (window.notificationSystem) {
                window.notificationSystem.soundEnabled = this.preferences.sound_alerts;
                window.notificationSystem.vibrationEnabled = this.preferences.vibration_alerts;
            }
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('alertPreferencesModal'));
            modal.hide();
        }
    }

    resetToDefaults() {
        if (confirm('Are you sure you want to reset all preferences to defaults?')) {
            this.preferences = {
                email_alerts: true,
                sms_alerts: false,
                push_notifications: true,
                weekly_digest: true,
                critical_only: false,
                sound_alerts: true,
                vibration_alerts: true,
                alert_frequency: 'immediate',
                risk_threshold: 5.0,
                severity_filters: {
                    critical: true,
                    high: true,
                    medium: true,
                    low: false
                },
                content_filters: {
                    fraud_detection: true,
                    market_anomalies: true,
                    sebi_updates: true,
                    advisor_verification: true,
                    portfolio_alerts: false
                }
            };
            
            // Update UI
            this.updateUIFromPreferences();
            this.showNotification('Preferences reset to defaults', 'info');
        }
    }

    updateUIFromPreferences() {
        // Update all UI elements with current preferences
        document.getElementById('emailAlerts').checked = this.preferences.email_alerts;
        document.getElementById('smsAlerts').checked = this.preferences.sms_alerts;
        document.getElementById('pushNotifications').checked = this.preferences.push_notifications;
        document.getElementById('weeklyDigest').checked = this.preferences.weekly_digest;
        document.getElementById('criticalOnly').checked = this.preferences.critical_only;
        document.getElementById('soundAlerts').checked = this.preferences.sound_alerts;
        document.getElementById('vibrationAlerts').checked = this.preferences.vibration_alerts;
        document.getElementById('alertFrequency').value = this.preferences.alert_frequency;
        document.getElementById('riskThreshold').value = this.preferences.risk_threshold;
        document.getElementById('riskThresholdValue').textContent = this.preferences.risk_threshold;
        
        // Update severity filters
        document.getElementById('criticalFilter').checked = this.preferences.severity_filters.critical;
        document.getElementById('highFilter').checked = this.preferences.severity_filters.high;
        document.getElementById('mediumFilter').checked = this.preferences.severity_filters.medium;
        document.getElementById('lowFilter').checked = this.preferences.severity_filters.low;
        
        // Update content filters
        document.getElementById('fraudDetection').checked = this.preferences.content_filters.fraud_detection;
        document.getElementById('marketAnomalies').checked = this.preferences.content_filters.market_anomalies;
        document.getElementById('sebiUpdates').checked = this.preferences.content_filters.sebi_updates;
        document.getElementById('advisorVerification').checked = this.preferences.content_filters.advisor_verification;
        document.getElementById('portfolioAlerts').checked = this.preferences.content_filters.portfolio_alerts;
    }

    testNotification(type) {
        if (window.notificationSystem) {
            window.notificationSystem.testNotification(type);
        }
    }

    shouldShowNotification(alert) {
        // Check if notification should be shown based on preferences
        if (this.preferences.critical_only && alert.severity !== 'critical') {
            return false;
        }
        
        if (alert.risk_score < this.preferences.risk_threshold) {
            return false;
        }
        
        if (!this.preferences.severity_filters[alert.severity]) {
            return false;
        }
        
        return true;
    }

    getNotificationChannels() {
        return {
            email: this.preferences.email_alerts,
            sms: this.preferences.sms_alerts,
            push: this.preferences.push_notifications,
            browser: this.preferences.push_notifications
        };
    }

    showNotification(message, type = 'info') {
        if (window.notificationSystem) {
            window.notificationSystem.showNotification({
                title: 'Alert Preferences',
                message: message,
                severity: type
            });
        }
    }

    getPreferences() {
        return this.preferences;
    }
}

// Initialize alert preferences when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.alertPreferences = new AlertPreferences();
});

// Global functions for inline event handlers
function openAlertPreferences() {
    if (window.alertPreferences) {
        window.alertPreferences.openPreferences();
    }
}

function testAlertNotification(type) {
    if (window.alertPreferences) {
        window.alertPreferences.testNotification(type);
    }
}
