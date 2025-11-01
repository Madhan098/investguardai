// Network Analysis JavaScript functionality for FraudShield

class NetworkAnalyzer {
    constructor() {
        this.networkData = null;
        this.filteredData = null;
        this.selectedEntity = null;
        this.currentThreshold = 5;
        this.currentConnectionType = 'all';
        this.init();
    }

    init() {
        this.setupEventListeners();
        console.log('Network Analyzer initialized');
    }

    setupEventListeners() {
        // Risk threshold slider
        const riskThreshold = document.getElementById('riskThreshold');
        if (riskThreshold) {
            riskThreshold.addEventListener('input', (e) => {
                this.currentThreshold = parseFloat(e.target.value);
                this.filterNetwork(this.currentThreshold);
            });
        }

        // Connection type filter
        const connectionType = document.getElementById('connectionType');
        if (connectionType) {
            connectionType.addEventListener('change', (e) => {
                this.currentConnectionType = e.target.value;
                this.filterByType(e.target.value);
            });
        }

        // Entity search
        const entitySearch = document.getElementById('entitySearch');
        if (entitySearch) {
            entitySearch.addEventListener('keyup', (e) => {
                this.searchEntity(e.target.value);
            });
        }

        // Network controls
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="viewConnection"]')) {
                const connectionId = e.target.getAttribute('onclick').match(/\d+/)[0];
                this.viewConnection(connectionId);
            }
            if (e.target.matches('[onclick*="analyzeEntity"]')) {
                const entityMatch = e.target.getAttribute('onclick').match(/'([^']+)'/);
                if (entityMatch) {
                    this.analyzeEntity(entityMatch[1]);
                }
            }
        });
    }

    setNetworkData(data) {
        this.networkData = data;
        this.filteredData = data;
        this.updateNetworkVisualization();
        this.updateStatistics();
    }

    filterNetwork(threshold) {
        if (!this.networkData) return;

        const filteredEdges = this.networkData.edges.filter(edge => 
            edge.suspicious_score >= threshold
        );

        // Get nodes that are connected by filtered edges
        const connectedNodes = new Set();
        filteredEdges.forEach(edge => {
            connectedNodes.add(edge.source);
            connectedNodes.add(edge.target);
        });

        const filteredNodes = this.networkData.nodes.filter(node => 
            connectedNodes.has(node.id)
        );

        this.filteredData = {
            nodes: filteredNodes,
            edges: filteredEdges
        };

        this.updateNetworkVisualization();
        this.updateStatistics();
        this.showNotification(`Filtered to ${filteredEdges.length} connections above risk threshold ${threshold}`, 'info');
    }

    filterByType(connectionType) {
        if (!this.networkData) return;

        let filteredEdges = this.networkData.edges;
        
        if (connectionType !== 'all') {
            filteredEdges = this.networkData.edges.filter(edge => 
                edge.type === connectionType
            );
        }

        // Apply current risk threshold
        filteredEdges = filteredEdges.filter(edge => 
            edge.suspicious_score >= this.currentThreshold
        );

        // Get connected nodes
        const connectedNodes = new Set();
        filteredEdges.forEach(edge => {
            connectedNodes.add(edge.source);
            connectedNodes.add(edge.target);
        });

        const filteredNodes = this.networkData.nodes.filter(node => 
            connectedNodes.has(node.id)
        );

        this.filteredData = {
            nodes: filteredNodes,
            edges: filteredEdges
        };

        this.updateNetworkVisualization();
        this.updateStatistics();
    }

    searchEntity(query) {
        if (!this.networkData || !query.trim()) {
            this.clearEntityHighlight();
            return;
        }

        const matchingNodes = this.networkData.nodes.filter(node => 
            node.label.toLowerCase().includes(query.toLowerCase())
        );

        this.highlightEntities(matchingNodes);
        
        if (matchingNodes.length > 0) {
            this.showNotification(`Found ${matchingNodes.length} matching entities`, 'success');
        } else {
            this.showNotification('No matching entities found', 'warning');
        }
    }

    highlightEntities(entities) {
        // Remove previous highlights
        this.clearEntityHighlight();

        // Highlight matching entities in the visualization
        entities.forEach(entity => {
            const entityElement = document.querySelector(`[data-entity-id="${entity.id}"]`);
            if (entityElement) {
                entityElement.classList.add('entity-highlighted');
            }
        });
    }

    clearEntityHighlight() {
        const highlightedElements = document.querySelectorAll('.entity-highlighted');
        highlightedElements.forEach(el => el.classList.remove('entity-highlighted'));
    }

    updateNetworkVisualization() {
        const container = document.getElementById('network-container');
        if (!container || !this.filteredData) return;

        // Create a simplified network visualization
        const nodesCount = this.filteredData.nodes.length;
        const edgesCount = this.filteredData.edges.length;

        if (nodesCount === 0) {
            container.innerHTML = `
                <div class="d-flex align-items-center justify-content-center h-100">
                    <div class="text-center">
                        <i data-feather="filter" width="64" height="64" class="text-muted mb-3"></i>
                        <h5>No Connections Match Filter</h5>
                        <p class="text-muted">Adjust the risk threshold or connection type filter to see results.</p>
                    </div>
                </div>
            `;
            feather.replace();
            return;
        }

        // Create a grid layout for entities
        const gridHTML = this.createNetworkGrid();
        container.innerHTML = gridHTML;
        feather.replace();
    }

    createNetworkGrid() {
        const nodes = this.filteredData.nodes.slice(0, 20); // Limit for display
        const edges = this.filteredData.edges;

        return `
            <div class="p-3">
                <div class="row g-2 mb-3">
                    <div class="col-12">
                        <h6 class="text-muted mb-2">Network Entities (${nodes.length})</h6>
                        <div class="d-flex flex-wrap gap-2">
                            ${nodes.map(node => `
                                <div class="entity-node bg-primary bg-opacity-25 border border-primary rounded px-3 py-2" 
                                     data-entity-id="${node.id}" 
                                     onclick="selectEntity('${node.id}')">
                                    <small class="text-light">${node.label}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-12">
                        <h6 class="text-muted mb-2">High-Risk Connections (${edges.length})</h6>
                        <div class="connection-list" style="max-height: 300px; overflow-y: auto;">
                            ${edges.map(edge => this.createConnectionCard(edge)).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createConnectionCard(edge) {
        const riskClass = edge.suspicious_score >= 8 ? 'danger' : 
                         edge.suspicious_score >= 6 ? 'warning' : 'info';
        
        return `
            <div class="card card-sm mb-2 border-${riskClass}">
                <div class="card-body py-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <small class="text-muted">${edge.type}</small><br>
                            <strong class="small">${edge.source}</strong> 
                            <i data-feather="arrow-right" width="12" height="12" class="mx-1"></i>
                            <strong class="small">${edge.target}</strong>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-${riskClass}">
                                ${edge.suspicious_score.toFixed(1)}
                            </span><br>
                            <small class="text-muted">Strength: ${(edge.strength * 100).toFixed(0)}%</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    updateStatistics() {
        if (!this.filteredData) return;

        const entityCount = document.getElementById('entityCount');
        const connectionCount = document.getElementById('connectionCount');
        const suspiciousCount = document.getElementById('suspiciousCount');
        const clusterCount = document.getElementById('clusterCount');

        if (entityCount) entityCount.textContent = this.filteredData.nodes.length;
        if (connectionCount) connectionCount.textContent = this.filteredData.edges.length;
        
        if (suspiciousCount) {
            const highRiskConnections = this.filteredData.edges.filter(edge => 
                edge.suspicious_score >= 7.0
            ).length;
            suspiciousCount.textContent = highRiskConnections;
        }

        if (clusterCount) {
            const clusters = this.detectClusters();
            clusterCount.textContent = clusters.length;
        }
    }

    detectClusters() {
        if (!this.filteredData) return [];

        // Simple cluster detection based on connected components
        const visited = new Set();
        const clusters = [];

        this.filteredData.nodes.forEach(node => {
            if (!visited.has(node.id)) {
                const cluster = this.dfsCluster(node.id, visited);
                if (cluster.length > 2) { // Only consider clusters with more than 2 nodes
                    clusters.push(cluster);
                }
            }
        });

        return clusters;
    }

    dfsCluster(nodeId, visited) {
        const cluster = [nodeId];
        visited.add(nodeId);

        // Find connected nodes
        const connectedEdges = this.filteredData.edges.filter(edge => 
            edge.source === nodeId || edge.target === nodeId
        );

        connectedEdges.forEach(edge => {
            const connectedNodeId = edge.source === nodeId ? edge.target : edge.source;
            if (!visited.has(connectedNodeId)) {
                cluster.push(...this.dfsCluster(connectedNodeId, visited));
            }
        });

        return cluster;
    }

    async analyzeNetwork() {
        const modal = new bootstrap.Modal(document.getElementById('analysisModal'));
        const resultsContainer = document.getElementById('analysis-results');
        
        // Show loading state
        resultsContainer.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary mb-3" role="status"></div>
                <p>Analyzing network patterns and suspicious connections...</p>
            </div>
        `;
        modal.show();

        // Simulate analysis delay
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Generate analysis results
        const analysis = this.generateNetworkAnalysis();
        resultsContainer.innerHTML = this.createAnalysisReport(analysis);
        feather.replace();
    }

    generateNetworkAnalysis() {
        if (!this.filteredData) return null;

        const totalNodes = this.filteredData.nodes.length;
        const totalEdges = this.filteredData.edges.length;
        const avgRiskScore = totalEdges > 0 ? 
            this.filteredData.edges.reduce((sum, edge) => sum + edge.suspicious_score, 0) / totalEdges : 0;
        
        const clusters = this.detectClusters();
        const highRiskNodes = this.identifyHighRiskNodes();

        return {
            totalNodes,
            totalEdges,
            avgRiskScore,
            clusters: clusters.length,
            highRiskNodes,
            riskLevel: avgRiskScore >= 8 ? 'critical' : 
                      avgRiskScore >= 6 ? 'high' : 
                      avgRiskScore >= 4 ? 'medium' : 'low'
        };
    }

    identifyHighRiskNodes() {
        if (!this.filteredData) return [];

        const nodeRiskScores = {};
        
        // Calculate risk score for each node based on its connections
        this.filteredData.edges.forEach(edge => {
            if (!nodeRiskScores[edge.source]) nodeRiskScores[edge.source] = [];
            if (!nodeRiskScores[edge.target]) nodeRiskScores[edge.target] = [];
            
            nodeRiskScores[edge.source].push(edge.suspicious_score);
            nodeRiskScores[edge.target].push(edge.suspicious_score);
        });

        const highRiskNodes = [];
        Object.entries(nodeRiskScores).forEach(([nodeId, scores]) => {
            const avgScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
            if (avgScore >= 7.0) {
                highRiskNodes.push({ id: nodeId, riskScore: avgScore, connections: scores.length });
            }
        });

        return highRiskNodes.sort((a, b) => b.riskScore - a.riskScore);
    }

    createAnalysisReport(analysis) {
        if (!analysis) return '<p>No analysis data available.</p>';

        const riskBadgeClass = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'success'
        }[analysis.riskLevel];

        return `
            <div class="row">
                <div class="col-md-6">
                    <h6><i data-feather="bar-chart-2" class="me-2"></i>Network Statistics</h6>
                    <ul class="list-unstyled">
                        <li><strong>Total Entities:</strong> ${analysis.totalNodes}</li>
                        <li><strong>Total Connections:</strong> ${analysis.totalEdges}</li>
                        <li><strong>Average Risk Score:</strong> ${analysis.avgRiskScore.toFixed(1)}/10</li>
                        <li><strong>Fraud Clusters:</strong> ${analysis.clusters}</li>
                        <li><strong>High-Risk Entities:</strong> ${analysis.highRiskNodes.length}</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6><i data-feather="shield" class="me-2"></i>Risk Assessment</h6>
                    <div class="alert alert-${riskBadgeClass} mb-3">
                        <h6 class="alert-heading">
                            ${analysis.riskLevel.toUpperCase()} RISK NETWORK
                        </h6>
                        <p class="mb-0">
                            ${this.getRiskRecommendation(analysis.riskLevel)}
                        </p>
                    </div>
                </div>
            </div>
            
            ${analysis.highRiskNodes.length > 0 ? `
                <div class="row mt-3">
                    <div class="col-12">
                        <h6><i data-feather="alert-triangle" class="me-2"></i>High-Risk Entities</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Entity</th>
                                        <th>Risk Score</th>
                                        <th>Connections</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${analysis.highRiskNodes.slice(0, 5).map(node => `
                                        <tr>
                                            <td><code class="small">${node.id}</code></td>
                                            <td><span class="badge bg-danger">${node.riskScore.toFixed(1)}</span></td>
                                            <td>${node.connections}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            ` : ''}
        `;
    }

    getRiskRecommendation(riskLevel) {
        const recommendations = {
            'critical': 'Immediate investigation required. Block all associated accounts and coordinate with law enforcement.',
            'high': 'Enhanced monitoring required. Verify all transactions and implement additional security measures.',
            'medium': 'Regular monitoring advised. Review connections and watch for escalating patterns.',
            'low': 'Standard monitoring sufficient. Network appears relatively safe.'
        };
        
        return recommendations[riskLevel] || 'Unknown risk level.';
    }

    viewConnection(connectionId) {
        // Find connection details
        const connection = this.filteredData?.edges.find(edge => edge.id === parseInt(connectionId));
        
        if (!connection) {
            this.showNotification('Connection not found', 'error');
            return;
        }

        const details = `
            <div class="row">
                <div class="col-12">
                    <h6>Connection Details</h6>
                    <dl class="row">
                        <dt class="col-sm-3">Source Entity:</dt>
                        <dd class="col-sm-9"><code>${connection.source}</code></dd>
                        
                        <dt class="col-sm-3">Target Entity:</dt>
                        <dd class="col-sm-9"><code>${connection.target}</code></dd>
                        
                        <dt class="col-sm-3">Connection Type:</dt>
                        <dd class="col-sm-9">${connection.type}</dd>
                        
                        <dt class="col-sm-3">Strength:</dt>
                        <dd class="col-sm-9">${(connection.strength * 100).toFixed(1)}%</dd>
                        
                        <dt class="col-sm-3">Risk Score:</dt>
                        <dd class="col-sm-9">
                            <span class="badge bg-${connection.suspicious_score >= 8 ? 'danger' : connection.suspicious_score >= 6 ? 'warning' : 'info'}">
                                ${connection.suspicious_score.toFixed(1)}/10
                            </span>
                        </dd>
                    </dl>
                </div>
            </div>
        `;

        // Show in a modal or notification
        this.showNotification(`Connection details logged to console`, 'info');
        console.log('Connection Details:', connection);
    }

    analyzeEntity(entityId) {
        this.selectedEntity = entityId;
        
        // Find all connections for this entity
        const entityConnections = this.filteredData?.edges.filter(edge => 
            edge.source === entityId || edge.target === entityId
        ) || [];

        const summary = `
Entity: ${entityId}
Connections: ${entityConnections.length}
Average Risk: ${entityConnections.length > 0 ? 
    (entityConnections.reduce((sum, conn) => sum + conn.suspicious_score, 0) / entityConnections.length).toFixed(1) : 0}/10
        `;

        console.log('Entity Analysis:', summary);
        this.showNotification(`Analyzing entity: ${entityId}`, 'info');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
}

// Global functions for inline event handlers
function filterNetwork(threshold) {
    if (window.networkAnalyzer) {
        window.networkAnalyzer.filterNetwork(threshold);
    }
}

function filterByType(type) {
    if (window.networkAnalyzer) {
        window.networkAnalyzer.filterByType(type);
    }
}

function searchEntity(query) {
    if (window.networkAnalyzer) {
        window.networkAnalyzer.searchEntity(query);
    }
}

function analyzeNetwork() {
    if (window.networkAnalyzer) {
        window.networkAnalyzer.analyzeNetwork();
    }
}

function viewConnection(id) {
    if (window.networkAnalyzer) {
        window.networkAnalyzer.viewConnection(id);
    }
}

function analyzeEntity(entity) {
    if (window.networkAnalyzer) {
        window.networkAnalyzer.analyzeEntity(entity);
    }
}

function refreshNetwork() {
    location.reload();
}

function exportNetwork() {
    if (window.networkAnalyzer && window.networkAnalyzer.filteredData) {
        const exportData = {
            timestamp: new Date().toISOString(),
            network: window.networkAnalyzer.filteredData,
            analysis: window.networkAnalyzer.generateNetworkAnalysis(),
            platform: 'FraudShield'
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `network-analysis-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

function exportAnalysis() {
    exportNetwork(); // Same functionality
}

function selectEntity(entityId) {
    if (window.networkAnalyzer) {
        window.networkAnalyzer.analyzeEntity(entityId);
    }
}

// Initialize network analyzer when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.networkAnalyzer = new NetworkAnalyzer();
    
    // Set network data if available
    if (typeof networkData !== 'undefined') {
        window.networkAnalyzer.setNetworkData(networkData);
    }
});
