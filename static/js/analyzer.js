// Content Analyzer JavaScript functionality for FraudShield

class ContentAnalyzer {
    constructor() {
        this.analysisInProgress = false;
        this.currentAnalysis = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFormValidation();
        console.log('Content Analyzer initialized');
    }

    setupEventListeners() {
        // Content type change handler
        const contentTypeSelect = document.getElementById('content_type');
        if (contentTypeSelect) {
            contentTypeSelect.addEventListener('change', (e) => {
                this.updateContentPlaceholder(e.target.value);
            });
        }

        // Content textarea for real-time analysis hints
        const contentTextarea = document.getElementById('content');
        if (contentTextarea) {
            contentTextarea.addEventListener('input', (e) => {
                this.showRealTimeHints(e.target.value);
            });
        }

        // Form submission handler
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmission(e);
            });
        }
    }

    setupFormValidation() {
        const contentTextarea = document.getElementById('content');
        if (!contentTextarea) return;

        // Custom validation messages
        contentTextarea.addEventListener('invalid', (e) => {
            e.target.setCustomValidity('Please provide content to analyze');
        });

        contentTextarea.addEventListener('input', (e) => {
            e.target.setCustomValidity('');
        });
    }

    updateContentPlaceholder(contentType) {
        const contentTextarea = document.getElementById('content');
        if (!contentTextarea) return;

        const placeholders = {
            'text': 'Paste the text content, message, or post to analyze for fraud indicators...',
            'url': 'Enter the URL or link to analyze (e.g., https://suspicious-investment-site.com)',
            'image': 'Describe the image content or paste any text visible in the image...',
            'video': 'Describe the video content, transcript, or any promotional text...'
        };

        contentTextarea.placeholder = placeholders[contentType] || placeholders['text'];
    }

    showRealTimeHints(content) {
        if (content.length < 10) return;

        // Simple real-time fraud indicator detection
        const highRiskKeywords = [
            'guaranteed returns', 'risk-free', 'get rich quick',
            'limited time', 'act now', 'exclusive opportunity'
        ];

        const foundKeywords = highRiskKeywords.filter(keyword => 
            content.toLowerCase().includes(keyword)
        );

        this.updateHintsDisplay(foundKeywords);
    }

    updateHintsDisplay(keywords) {
        let hintsContainer = document.getElementById('real-time-hints');
        
        if (!hintsContainer) {
            hintsContainer = document.createElement('div');
            hintsContainer.id = 'real-time-hints';
            hintsContainer.className = 'mt-2';
            
            const contentTextarea = document.getElementById('content');
            contentTextarea.parentNode.appendChild(hintsContainer);
        }

        if (keywords.length === 0) {
            hintsContainer.innerHTML = '';
            return;
        }

        const hintsHTML = `
            <div class="alert alert-warning alert-sm py-2">
                <i data-feather="alert-triangle" width="16" height="16" class="me-1"></i>
                <strong>Potential fraud indicators detected:</strong>
                <div class="mt-1">
                    ${keywords.map(keyword => `<span class="badge bg-warning text-dark me-1">${keyword}</span>`).join('')}
                </div>
            </div>
        `;

        hintsContainer.innerHTML = hintsHTML;
        feather.replace();
    }

    handleFormSubmission(e) {
        if (this.analysisInProgress) {
            e.preventDefault();
            return;
        }

        const content = document.getElementById('content').value.trim();
        const contentType = document.getElementById('content_type').value;

        // Client-side validation
        if (!content) {
            e.preventDefault();
            this.showNotification('Please provide content to analyze', 'warning');
            return;
        }

        if (content.length < 5) {
            e.preventDefault();
            this.showNotification('Content is too short for meaningful analysis', 'warning');
            return;
        }

        // Show loading state
        this.setAnalysisState(true);
    }

    setAnalysisState(analyzing) {
        this.analysisInProgress = analyzing;
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (!analyzeBtn) return;

        if (analyzing) {
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<div class="spinner-border spinner-border-sm me-2" role="status"></div>Analyzing...';
        } else {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i data-feather="play" class="me-2"></i>Analyze Content';
            feather.replace();
        }
    }

    clearForm() {
        const contentTextarea = document.getElementById('content');
        const contentTypeSelect = document.getElementById('content_type');
        const hintsContainer = document.getElementById('real-time-hints');

        if (contentTextarea) contentTextarea.value = '';
        if (contentTypeSelect) contentTypeSelect.value = 'text';
        if (hintsContainer) hintsContainer.innerHTML = '';

        this.updateContentPlaceholder('text');
    }

    exportResults() {
        if (!this.currentAnalysis) {
            this.showNotification('No analysis results to export', 'warning');
            return;
        }

        // Create exportable data
        const exportData = {
            timestamp: new Date().toISOString(),
            analysis: this.currentAnalysis,
            platform: 'FraudShield',
            version: '1.0'
        };

        // Create and download file
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `fraud-analysis-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('Analysis results exported successfully', 'success');
    }

    shareResults() {
        if (!this.currentAnalysis) {
            this.showNotification('No analysis results to share', 'warning');
            return;
        }

        // Create shareable summary
        const summary = `
FraudShield Analysis Report
Risk Score: ${this.currentAnalysis.risk_score}/10
Recommendation: ${this.currentAnalysis.recommendation}
Generated: ${new Date().toLocaleDateString()}
        `.trim();

        if (navigator.share) {
            navigator.share({
                title: 'FraudShield Analysis Report',
                text: summary,
                url: window.location.href
            });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(summary).then(() => {
                this.showNotification('Analysis summary copied to clipboard', 'success');
            });
        }
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

        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Risk score visualization
    animateRiskScore(score) {
        const scoreElement = document.querySelector('.risk-score-text');
        if (!scoreElement) return;

        let currentScore = 0;
        const increment = score / 50; // 50 steps
        
        const animation = setInterval(() => {
            currentScore += increment;
            if (currentScore >= score) {
                currentScore = score;
                clearInterval(animation);
            }
            scoreElement.textContent = currentScore.toFixed(1);
        }, 20);
    }

    // Content type specific validations
    validateURL(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Extract entities from content
    extractEntities(content) {
        const entities = {
            emails: content.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g) || [],
            phones: content.match(/\b\d{10}\b/g) || [],
            urls: content.match(/https?:\/\/[^\s]+/g) || [],
            amounts: content.match(/₹\s*\d+(?:,\d+)*(?:\.\d+)?/g) || []
        };

        return entities;
    }
}

// Global functions for inline event handlers
function clearForm() {
    if (window.contentAnalyzer) {
        window.contentAnalyzer.clearForm();
    }
}

function exportResults() {
    if (window.contentAnalyzer) {
        window.contentAnalyzer.exportResults();
    }
}

function shareResults() {
    if (window.contentAnalyzer) {
        window.contentAnalyzer.shareResults();
    }
}

// Initialize analyzer when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.contentAnalyzer = new ContentAnalyzer();
    
    // If there are analysis results, store them for export
    const analysisResult = document.querySelector('.risk-score-text');
    if (analysisResult) {
        const score = parseFloat(analysisResult.textContent);
        window.contentAnalyzer.currentAnalysis = {
            risk_score: score,
            recommendation: document.querySelector('.alert .alert-heading')?.nextElementSibling?.textContent || 'Unknown'
        };
        
        // Animate the risk score
        window.contentAnalyzer.animateRiskScore(score);
    }
});
