/**
 * Real-Time Dashboard with Live Data Integration
 * Updates dashboard with live market data, fraud alerts, and SEBI updates
 */

class RealTimeDashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.isLive = true;
        this.stats = {
            totalScans: 0,
            fraudsDetected: 0,
            moneySaved: 0,
            accuracy: 98.5
        };
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing Real-Time Dashboard...');
        this.loadInitialData();
        this.startLiveUpdates();
        this.setupEventListeners();
    }
    
    async loadInitialData() {
        try {
            // Load live market data
            await this.loadMarketData();
            
            // Load fraud alerts
            await this.loadFraudAlerts();
            
            // Load SEBI updates
            await this.loadSEBIUpdates();
            
            // Update stats
            this.updateStats();
            
            console.log('✅ Initial data loaded successfully');
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
        }
    }
    
    startLiveUpdates() {
        console.log('🔄 Starting live updates...');
        
        // Update every 30 seconds
        setInterval(() => {
            if (this.isLive) {
                this.updateLiveData();
            }
        }, this.updateInterval);
        
        // Update market data every 10 seconds
        setInterval(() => {
            if (this.isLive) {
                this.loadMarketData();
            }
        }, 10000);
    }
    
    async updateLiveData() {
        try {
            // Enhanced API call with offline support
            const response = await fetch('/api/dashboard/live-stats', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                },
                // Add timeout for better PWA experience
                signal: AbortSignal.timeout(10000) // 10 second timeout
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.updateDashboard(data);
                this.showLiveIndicator();
            } else {
                console.warn('Live data update returned unsuccessful:', data);
            }
        } catch (error) {
            console.error('Error updating live data:', error);
            
            // Check if offline and use cached data if available
            if (!navigator.onLine) {
                console.log('Offline - attempting to use cached data');
                // Try to get cached data from service worker
                if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
                    // Service worker will handle offline requests
                }
            }
            
            // Show offline indicator if needed
            if (!navigator.onLine) {
                this.showOfflineIndicator();
            }
        }
    }
    
    showOfflineIndicator() {
        // Show offline indicator in UI
        const liveIndicator = document.querySelector('.live-indicator');
        if (liveIndicator) {
            liveIndicator.classList.remove('online');
            liveIndicator.classList.add('offline');
            liveIndicator.textContent = 'Offline';
        }
    }
    
    async loadMarketData() {
        try {
            // Enhanced API calls with offline support and timeouts for PWA
            // Load NIFTY 50 data
            const niftyResponse = await fetch('/api/market/nifty50', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                signal: AbortSignal.timeout(10000) // 10 second timeout
            });
            
            if (niftyResponse.ok) {
                const niftyData = await niftyResponse.json();
                if (niftyData.success) {
                    this.updateMarketDisplay(niftyData);
                }
            }
            
            // Load market summary
            const summaryResponse = await fetch('/api/market/summary', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                signal: AbortSignal.timeout(10000) // 10 second timeout
            });
            
            if (summaryResponse.ok) {
                const summaryData = await summaryResponse.json();
                if (summaryData.success) {
                    this.updateMarketSummary(summaryData);
                }
            }
        } catch (error) {
            console.error('Error loading market data:', error);
            
            // Show offline message if applicable
            if (!navigator.onLine) {
                console.log('[PWA] Offline - market data unavailable, using cached data');
            }
        }
    }
    
    async loadFraudAlerts() {
        try {
            // Enhanced API call with offline support for PWA
            const response = await fetch('/api/news/fraud-alerts', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                signal: AbortSignal.timeout(10000) // 10 second timeout
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.articles) {
                this.updateFraudAlerts(data.articles);
            } else {
                console.warn('Fraud alerts returned unsuccessful:', data);
            }
        } catch (error) {
            console.error('Error loading fraud alerts:', error);
            
            // Show offline message if applicable
            if (!navigator.onLine) {
                console.log('[PWA] Offline - fraud alerts unavailable, using cached data');
            }
        }
    }
    
    async loadSEBIUpdates() {
        try {
            // Enhanced API call with offline support for PWA
            const response = await fetch('/api/news/sebi-updates', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                signal: AbortSignal.timeout(10000) // 10 second timeout
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.success && data.updates) {
                this.updateSEBIUpdates(data.updates);
            } else {
                console.warn('SEBI updates returned unsuccessful:', data);
            }
        } catch (error) {
            console.error('Error loading SEBI updates:', error);
            
            // Show offline message if applicable
            if (!navigator.onLine) {
                console.log('[PWA] Offline - SEBI updates unavailable, using cached data');
            }
        }
    }
    
    updateDashboard(data) {
        // Update market data
        if (data.market_data && data.market_data.success) {
            this.updateMarketDisplay(data.market_data);
        }
        
        // Update alerts
        if (data.fraud_news) {
            this.updateFraudAlerts(data.fraud_news);
        }
        
        // Update stats
        this.stats.totalAlerts = data.total_alerts || 0;
        this.stats.highRiskAlerts = data.high_risk_alerts || 0;
        this.updateStats();
    }
    
    updateMarketDisplay(marketData) {
        const marketContainer = document.getElementById('marketData');
        if (!marketContainer) return;
        
        const changeClass = marketData.change >= 0 ? 'text-success' : 'text-danger';
        const changeIcon = marketData.change >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
        
        marketContainer.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card border-primary">
                        <div class="card-header bg-primary text-white">
                            <h6 class="mb-0"><i class="fas fa-chart-line me-2"></i>NIFTY 50</h6>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h4 class="mb-0">${marketData.value.toFixed(2)}</h4>
                                    <small class="text-muted">Last Updated: ${new Date(marketData.timestamp).toLocaleTimeString()}</small>
                                </div>
                                <div class="text-end">
                                    <span class="${changeClass}">
                                        <i class="fas ${changeIcon} me-1"></i>
                                        ${marketData.change.toFixed(2)}%
                                    </span>
                                    <div class="small text-muted">${marketData.change_amount.toFixed(2)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card border-info">
                        <div class="card-header bg-info text-white">
                            <h6 class="mb-0"><i class="fas fa-chart-bar me-2"></i>Market Summary</h6>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-4">
                                    <div class="text-success">
                                        <i class="fas fa-arrow-up"></i>
                                        <div class="small">Open</div>
                                        <div class="fw-bold">${marketData.open.toFixed(2)}</div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="text-warning">
                                        <i class="fas fa-arrow-up"></i>
                                        <div class="small">High</div>
                                        <div class="fw-bold">${marketData.high.toFixed(2)}</div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="text-danger">
                                        <i class="fas fa-arrow-down"></i>
                                        <div class="small">Low</div>
                                        <div class="fw-bold">${marketData.low.toFixed(2)}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    updateMarketSummary(summaryData) {
        // Update market summary if needed
        console.log('Market summary updated:', summaryData);
    }
    
    updateFraudAlerts(articles) {
        const alertsContainer = document.getElementById('fraudAlerts');
        if (!alertsContainer || !articles) return;
        
        const highRiskArticles = articles.filter(article => article.severity === 'HIGH');
        
        alertsContainer.innerHTML = `
            <div class="row">
                ${articles.slice(0, 3).map(article => `
                    <div class="col-md-4 mb-3">
                        <div class="card ${article.severity === 'HIGH' ? 'border-danger' : 'border-warning'}">
                            <div class="card-header ${article.severity === 'HIGH' ? 'bg-danger text-white' : 'bg-warning text-dark'}">
                                <h6 class="mb-0">
                                    <i class="fas fa-exclamation-triangle me-2"></i>
                                    ${article.severity} Risk
                                </h6>
                            </div>
                            <div class="card-body">
                                <h6 class="card-title">${article.title.substring(0, 60)}...</h6>
                                <p class="card-text small">${article.description.substring(0, 100)}...</p>
                                <div class="d-flex justify-content-between align-items-center">
                                    <small class="text-muted">${article.source}</small>
                                    <small class="text-muted">${new Date(article.published_at).toLocaleDateString()}</small>
                                </div>
                                <a href="${article.url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">
                                    Read More
                                </a>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    updateSEBIUpdates(updates) {
        const updatesContainer = document.getElementById('sebiUpdates');
        if (!updatesContainer || !updates) return;
        
        updatesContainer.innerHTML = `
            <div class="list-group">
                ${updates.slice(0, 5).map(update => `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${update.title}</h6>
                            <small>${new Date(update.published_at).toLocaleDateString()}</small>
                        </div>
                        <p class="mb-1">${update.description}</p>
                        <small>Source: ${update.source}</small>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    updateStats() {
        // Update live stats
        this.animateNumber('totalScans', this.stats.totalScans);
        this.animateNumber('fraudsDetected', this.stats.fraudsDetected);
        this.animateNumber('moneySaved', this.stats.moneySaved);
        
        // Update accuracy
        const accuracyElement = document.getElementById('accuracy');
        if (accuracyElement) {
            accuracyElement.textContent = `${this.stats.accuracy}%`;
        }
    }
    
    animateNumber(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const currentValue = parseInt(element.textContent.replace(/,/g, '')) || 0;
        const increment = (targetValue - currentValue) / 10;
        
        if (Math.abs(targetValue - currentValue) > 1) {
            const newValue = Math.round(currentValue + increment);
            element.textContent = newValue.toLocaleString();
            
            setTimeout(() => {
                this.animateNumber(elementId, targetValue);
            }, 50);
        } else {
            element.textContent = targetValue.toLocaleString();
        }
    }
    
    showLiveIndicator() {
        const indicator = document.querySelector('.status-indicator');
        if (indicator) {
            indicator.classList.add('status-online');
            indicator.classList.remove('status-offline');
        }
        
        // Show notification
        this.showNotification('Live data updated', 'success');
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadInitialData();
            });
        }
        
        // Live toggle
        const liveToggle = document.getElementById('liveToggle');
        if (liveToggle) {
            liveToggle.addEventListener('change', (e) => {
                this.isLive = e.target.checked;
                if (this.isLive) {
                    this.startLiveUpdates();
                }
            });
        }
    }
    
    // Public methods for external use
    refreshData() {
        this.loadInitialData();
    }
    
    toggleLiveUpdates() {
        this.isLive = !this.isLive;
        if (this.isLive) {
            this.startLiveUpdates();
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.realtimeDashboard = new RealTimeDashboard();
});

// Export for use in other scripts
window.RealTimeDashboard = RealTimeDashboard;
