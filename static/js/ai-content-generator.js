// AI Content Generator using Gemini API
class AIContentGenerator {
    constructor() {
        this.isGenerating = false;
        this.init();
    }

    init() {
        console.log('🤖 Initializing AI Content Generator...');
        this.setupEventListeners();
        console.log('✅ AI Content Generator initialized');
    }

    setupEventListeners() {
        // Add event listeners for AI content generation buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-ai-generate]')) {
                const type = e.target.dataset.aiGenerate;
                const topic = e.target.dataset.topic || 'investment education';
                this.generateContent(type, topic);
            }
        });
    }

    async generateContent(type = 'general', topic = 'investment education', language = 'en') {
        if (this.isGenerating) {
            this.showNotification('Content generation in progress...', 'info');
            return;
        }

        this.isGenerating = true;
        this.showLoadingIndicator();

        try {
            console.log(`🤖 Generating ${type} content about ${topic} in ${language}`);
            
            const response = await fetch('/api/ai/generate-content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: type,
                    topic: topic,
                    language: language
                })
            });

            console.log('📡 API Response Status:', response.status);
            console.log('📡 API Response Headers:', response.headers);
            
            const data = await response.json();
            console.log('📡 API Response Data:', data);

            if (data.success) {
                this.displayGeneratedContent(data.content, data.type, data.topic);
                this.showNotification('AI content generated successfully!', 'success');
            } else {
                throw new Error(data.error || 'Failed to generate content');
            }

        } catch (error) {
            console.error('❌ AI content generation error:', error);
            this.showNotification(`Failed to generate content: ${error.message}. Using fallback content.`, 'warning');
            
            // Show fallback content even if API fails
            this.displayGeneratedContent(
                this.getFallbackContent(type, topic), 
                type, 
                topic
            );
        } finally {
            this.isGenerating = false;
            this.hideLoadingIndicator();
        }
    }

    displayGeneratedContent(content, type, topic) {
        // Create a modal to display the generated content
        const modalId = 'aiContentModal';
        let modal = document.getElementById(modalId);
        
        if (!modal) {
            modal = document.createElement('div');
            modal.id = modalId;
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-robot me-2"></i>
                                AI Generated Content
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="ai-content-display"></div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-2"></i>Close
                            </button>
                            <button type="button" class="btn btn-outline-primary" onclick="aiContentGenerator.copyContent()">
                                <i class="fas fa-copy me-2"></i>Copy Content
                            </button>
                            <button type="button" class="btn btn-primary" onclick="aiContentGenerator.saveContent()">
                                <i class="fas fa-save me-2"></i>Save Content
                            </button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        // Update modal content
        const contentDisplay = modal.querySelector('.ai-content-display');
        contentDisplay.innerHTML = `
            <div class="content-meta mb-3">
                <div class="row">
                    <div class="col-md-4">
                        <strong>Type:</strong> ${type}
                    </div>
                    <div class="col-md-4">
                        <strong>Topic:</strong> ${topic}
                    </div>
                    <div class="col-md-4">
                        <strong>Generated:</strong> ${new Date().toLocaleString()}
                    </div>
                </div>
            </div>
            <div class="content-body">
                ${content}
            </div>
        `;

        // Store content for copying/saving
        this.currentContent = content;
        this.currentType = type;
        this.currentTopic = topic;

        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    copyContent() {
        if (this.currentContent) {
            navigator.clipboard.writeText(this.currentContent).then(() => {
                this.showNotification('Content copied to clipboard!', 'success');
            }).catch(() => {
                this.showNotification('Failed to copy content', 'error');
            });
        }
    }

    async saveContent() {
        if (!this.currentContent) return;

        try {
            const response = await fetch('/api/content/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: this.currentContent,
                    type: this.currentType,
                    topic: this.currentTopic,
                    source: 'ai_generated'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Content saved successfully!', 'success');
            } else {
                throw new Error(data.error || 'Failed to save content');
            }
        } catch (error) {
            console.error('❌ Save content error:', error);
            this.showNotification('Failed to save content', 'error');
        }
    }

    showLoadingIndicator() {
        // Create or update loading indicator
        let loadingIndicator = document.getElementById('aiLoadingIndicator');
        
        if (!loadingIndicator) {
            loadingIndicator = document.createElement('div');
            loadingIndicator.id = 'aiLoadingIndicator';
            loadingIndicator.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
            loadingIndicator.style.cssText = 'background: rgba(0,0,0,0.5); z-index: 9999;';
            loadingIndicator.innerHTML = `
                <div class="bg-white rounded p-4 text-center">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Generating content...</span>
                    </div>
                    <h5>🤖 AI Content Generator</h5>
                    <p class="mb-0">Generating intelligent content...</p>
                </div>
            `;
            document.body.appendChild(loadingIndicator);
        }
    }

    hideLoadingIndicator() {
        const loadingIndicator = document.getElementById('aiLoadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }

    showNotification(message, type = 'info') {
        if (window.notificationSystem) {
            window.notificationSystem.showNotification({
                title: 'AI Content Generator',
                message: message,
                severity: type
            });
        } else {
            // Fallback notification
            alert(message);
        }
    }

    // Quick content generation methods
    generateFraudPreventionContent() {
        this.generateContent('fraud_prevention', 'investment fraud prevention', 'en');
    }

    generateSEBIGuidelinesContent() {
        this.generateContent('sebi_guidelines', 'SEBI regulations and compliance', 'en');
    }

    generateInvestmentEducationContent() {
        this.generateContent('investment_education', 'beginner investment guide', 'en');
    }

    generateRiskAssessmentContent() {
        this.generateContent('risk_assessment', 'portfolio risk management', 'en');
    }

    generateMultilingualContent(topic, language) {
        this.generateContent('general', topic, language);
    }
    
    getFallbackContent(type, topic) {
        if (type === 'fraud_prevention') {
            return `
                <div class="fraud-prevention-guide">
                    <h2>🛡️ Investment Fraud Prevention Guide</h2>
                    
                    <h3>🚨 Red Flags to Watch For:</h3>
                    <ul>
                        <li><strong>Guaranteed Returns:</strong> No legitimate investment can guarantee returns</li>
                        <li><strong>Pressure Tactics:</strong> "Limited time offers" or "act now" are warning signs</li>
                        <li><strong>Unrealistic Returns:</strong> Promises of 20%+ monthly returns are likely scams</li>
                        <li><strong>No SEBI Registration:</strong> Always verify advisor credentials</li>
                        <li><strong>WhatsApp/Telegram Only:</strong> Legitimate advisors have proper websites</li>
                    </ul>
                    
                    <h3>✅ How to Verify Legitimate Investments:</h3>
                    <ol>
                        <li><strong>Check SEBI Registration:</strong> Visit sebi.gov.in and verify advisor credentials</li>
                        <li><strong>Research the Company:</strong> Look for proper website, office address, contact details</li>
                        <li><strong>Ask for Documentation:</strong> Request SEBI registration certificate, company registration</li>
                        <li><strong>Verify Returns:</strong> Legitimate investments don't promise unrealistic returns</li>
                        <li><strong>Consult Multiple Sources:</strong> Get second opinions from registered advisors</li>
                    </ol>
                    
                    <div class="alert alert-warning">
                        <strong>Remember:</strong> If it sounds too good to be true, it probably is. Always verify before investing!
                    </div>
                </div>
            `;
        } else if (type === 'sebi_guidelines') {
            return `
                <div class="sebi-guidelines-guide">
                    <h2>📋 SEBI Guidelines & Compliance</h2>
                    
                    <h3>🏛️ About SEBI (Securities and Exchange Board of India):</h3>
                    <p>SEBI is the regulatory body that protects investors and promotes the development of the securities market in India.</p>
                    
                    <h3>📜 Key SEBI Guidelines for Investors:</h3>
                    <ul>
                        <li><strong>Investment Advisor Registration:</strong> All investment advisors must be registered with SEBI</li>
                        <li><strong>Disclosure Requirements:</strong> Advisors must disclose all fees, commissions, and conflicts of interest</li>
                        <li><strong>Risk Profiling:</strong> Advisors must assess your risk profile before recommending investments</li>
                        <li><strong>Know Your Customer (KYC):</strong> Proper documentation and verification required</li>
                        <li><strong>Investment Limits:</strong> SEBI sets limits on certain types of investments</li>
                    </ul>
                    
                    <h3>✅ How to Verify SEBI Registration:</h3>
                    <ol>
                        <li>Visit <strong>sebi.gov.in</strong></li>
                        <li>Go to "Other" → "Investment Advisors"</li>
                        <li>Search by registration number or advisor name</li>
                        <li>Verify the advisor's status and validity period</li>
                        <li>Check for any disciplinary actions</li>
                    </ol>
                    
                    <div class="alert alert-info">
                        <strong>Pro Tip:</strong> Always verify SEBI registration before investing. Unregistered advisors are operating illegally!
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="general-investment-guide">
                    <h2>📚 Investment Education Guide</h2>
                    
                    <h3>🎯 Topic: ${topic}</h3>
                    
                    <h3>💡 Key Investment Principles:</h3>
                    <ul>
                        <li><strong>Start Early:</strong> Time is your biggest advantage in investing</li>
                        <li><strong>Diversify:</strong> Don't put all your eggs in one basket</li>
                        <li><strong>Risk Assessment:</strong> Understand your risk tolerance</li>
                        <li><strong>Long-term Thinking:</strong> Invest for the long term, not quick gains</li>
                        <li><strong>Regular Investing:</strong> Systematic Investment Plans (SIPs) work best</li>
                    </ul>
                    
                    <h3>⚠️ Important Warnings:</h3>
                    <ul>
                        <li>Never invest based on tips or rumors</li>
                        <li>Always verify advisor credentials with SEBI</li>
                        <li>Be wary of guaranteed returns</li>
                        <li>Read all documents carefully before investing</li>
                        <li>Don't invest money you can't afford to lose</li>
                    </ul>
                    
                    <div class="alert alert-success">
                        <strong>Remember:</strong> Education is your best protection against investment fraud!
                    </div>
                </div>
            `;
        }
    }
}

// Initialize AI Content Generator when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.aiContentGenerator = new AIContentGenerator();
});

// Global functions for inline event handlers
function generateAIContent(type, topic) {
    if (window.aiContentGenerator) {
        window.aiContentGenerator.generateContent(type, topic);
    }
}

function generateFraudPreventionContent() {
    if (window.aiContentGenerator) {
        window.aiContentGenerator.generateFraudPreventionContent();
    }
}

function generateSEBIGuidelinesContent() {
    if (window.aiContentGenerator) {
        window.aiContentGenerator.generateSEBIGuidelinesContent();
    }
}

function generateInvestmentEducationContent() {
    if (window.aiContentGenerator) {
        window.aiContentGenerator.generateInvestmentEducationContent();
    }
}

function generateRiskAssessmentContent() {
    if (window.aiContentGenerator) {
        window.aiContentGenerator.generateRiskAssessmentContent();
    }
}
