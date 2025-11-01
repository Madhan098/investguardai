from models import NetworkConnection, FraudAlert
from app import db
from datetime import datetime, timedelta
import random
import json

class NetworkAnalyzer:
    def __init__(self):
        # Initialize with some mock network data
        self._initialize_mock_network_data()
    
    def _initialize_mock_network_data(self):
        """Initialize mock network connection data"""
        # Check if data already exists
        if NetworkConnection.query.count() > 0:
            return
        
        # Create mock suspicious network connections
        mock_connections = [
            {
                'source_entity': 'fake_advisor_1@email.com',
                'target_entity': 'fake_company_A',
                'connection_type': 'financial',
                'strength': 0.9,
                'suspicious_score': 8.5,
                'evidence': '{"shared_bank_accounts": true, "same_ip_addresses": true, "coordinated_messaging": true}'
            },
            {
                'source_entity': 'fake_company_A',
                'target_entity': 'fake_company_B',
                'connection_type': 'ownership',
                'strength': 0.95,
                'suspicious_score': 9.2,
                'evidence': '{"same_directors": true, "shared_office_address": true, "identical_website_templates": true}'
            },
            {
                'source_entity': 'fake_advisor_2@email.com',
                'target_entity': 'fake_company_B',
                'connection_type': 'communication',
                'strength': 0.8,
                'suspicious_score': 7.8,
                'evidence': '{"frequent_communication": true, "coordinated_posts": true, "shared_content": true}'
            },
            {
                'source_entity': 'suspicious_whatsapp_group_1',
                'target_entity': 'fake_advisor_1@email.com',
                'connection_type': 'communication',
                'strength': 0.85,
                'suspicious_score': 8.0,
                'evidence': '{"admin_role": true, "mass_messaging": true, "investment_promotions": true}'
            },
            {
                'source_entity': 'suspicious_whatsapp_group_1',
                'target_entity': 'fake_advisor_2@email.com',
                'connection_type': 'communication',
                'strength': 0.7,
                'suspicious_score': 7.2,
                'evidence': '{"member_role": true, "content_sharing": true, "referral_activities": true}'
            },
            {
                'source_entity': 'fake_company_C',
                'target_entity': 'offshore_account_1',
                'connection_type': 'financial',
                'strength': 0.9,
                'suspicious_score': 9.5,
                'evidence': '{"large_transfers": true, "frequent_transactions": true, "tax_haven_location": true}'
            },
            {
                'source_entity': 'fake_advisor_3@email.com',
                'target_entity': 'fake_company_C',
                'connection_type': 'financial',
                'strength': 0.75,
                'suspicious_score': 8.3,
                'evidence': '{"commission_payments": true, "undisclosed_relationship": true, "conflict_of_interest": true}'
            }
        ]
        
        for connection_data in mock_connections:
            connection = NetworkConnection(**connection_data)
            db.session.add(connection)
        
        db.session.commit()
    
    def analyze_network_patterns(self, entity_id=None):
        """
        Analyze network patterns to identify suspicious clusters
        """
        analysis_result = {
            'clusters_found': 0,
            'suspicious_entities': [],
            'connection_strength': 0.0,
            'risk_assessment': 'low',
            'network_insights': [],
            'recommended_actions': []
        }
        
        if entity_id:
            # Analyze specific entity's network
            return self._analyze_entity_network(entity_id, analysis_result)
        else:
            # Analyze entire network for patterns
            return self._analyze_global_network(analysis_result)
    
    def _analyze_entity_network(self, entity_id, result):
        """Analyze network for a specific entity"""
        # Find all connections for this entity
        connections = NetworkConnection.query.filter(
            (NetworkConnection.source_entity == entity_id) |
            (NetworkConnection.target_entity == entity_id)
        ).all()
        
        if not connections:
            result['network_insights'].append(f'No network connections found for {entity_id}')
            return result
        
        # Calculate average connection strength and suspicious score
        total_strength = sum(conn.strength for conn in connections)
        total_suspicious = sum(conn.suspicious_score for conn in connections)
        
        result['connection_strength'] = total_strength / len(connections)
        avg_suspicious_score = total_suspicious / len(connections)
        
        # Identify connected entities
        connected_entities = set()
        for conn in connections:
            if conn.source_entity != entity_id:
                connected_entities.add(conn.source_entity)
            if conn.target_entity != entity_id:
                connected_entities.add(conn.target_entity)
        
        result['suspicious_entities'] = list(connected_entities)
        
        # Assess risk based on network characteristics
        if avg_suspicious_score >= 8.0 and len(connections) >= 3:
            result['risk_assessment'] = 'critical'
            result['recommended_actions'].append('Immediate investigation required')
            result['recommended_actions'].append('Block all associated accounts')
        elif avg_suspicious_score >= 6.0:
            result['risk_assessment'] = 'high'
            result['recommended_actions'].append('Enhanced monitoring required')
            result['recommended_actions'].append('Verify all transactions')
        elif avg_suspicious_score >= 4.0:
            result['risk_assessment'] = 'medium'
            result['recommended_actions'].append('Regular monitoring advised')
        
        # Add network insights
        result['network_insights'].append(f'Entity connected to {len(connected_entities)} other entities')
        result['network_insights'].append(f'Average connection strength: {result["connection_strength"]:.2f}')
        result['network_insights'].append(f'Average suspicious score: {avg_suspicious_score:.2f}')
        
        return result
    
    def _analyze_global_network(self, result):
        """Analyze the entire network for suspicious patterns"""
        all_connections = NetworkConnection.query.filter(
            NetworkConnection.suspicious_score >= 5.0
        ).all()
        
        if not all_connections:
            result['network_insights'].append('No suspicious connections found in network')
            return result
        
        # Build entity frequency map
        entity_frequency = {}
        high_risk_entities = []
        
        for conn in all_connections:
            # Count how often each entity appears in suspicious connections
            entity_frequency[conn.source_entity] = entity_frequency.get(conn.source_entity, 0) + 1
            entity_frequency[conn.target_entity] = entity_frequency.get(conn.target_entity, 0) + 1
            
            # Identify high-risk entities
            if conn.suspicious_score >= 8.0:
                if conn.source_entity not in high_risk_entities:
                    high_risk_entities.append(conn.source_entity)
                if conn.target_entity not in high_risk_entities:
                    high_risk_entities.append(conn.target_entity)
        
        # Find entities that appear in multiple suspicious connections (potential hubs)
        suspicious_hubs = [entity for entity, count in entity_frequency.items() if count >= 3]
        
        result['clusters_found'] = len(suspicious_hubs)
        result['suspicious_entities'] = high_risk_entities
        
        # Calculate overall network risk
        avg_suspicious_score = sum(conn.suspicious_score for conn in all_connections) / len(all_connections)
        
        if avg_suspicious_score >= 8.0:
            result['risk_assessment'] = 'critical'
        elif avg_suspicious_score >= 6.0:
            result['risk_assessment'] = 'high'
        elif avg_suspicious_score >= 4.0:
            result['risk_assessment'] = 'medium'
        
        # Generate insights
        result['network_insights'].append(f'Analyzed {len(all_connections)} suspicious connections')
        result['network_insights'].append(f'Found {len(suspicious_hubs)} potential fraud hubs')
        result['network_insights'].append(f'Identified {len(high_risk_entities)} high-risk entities')
        result['network_insights'].append(f'Overall network risk score: {avg_suspicious_score:.2f}')
        
        # Generate recommendations
        if len(suspicious_hubs) > 0:
            result['recommended_actions'].append('Investigate identified fraud hubs immediately')
            result['recommended_actions'].append('Monitor all entities connected to hubs')
        
        if len(high_risk_entities) > 5:
            result['recommended_actions'].append('Coordinate with law enforcement')
            result['recommended_actions'].append('Implement network-wide monitoring')
        
        return result
    
    def detect_coordinated_activity(self, time_window_hours=24):
        """
        Detect coordinated fraudulent activity within a time window
        """
        time_threshold = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Get recent fraud alerts
        recent_alerts = FraudAlert.query.filter(
            FraudAlert.created_at >= time_threshold,
            FraudAlert.risk_score >= 6.0
        ).all()
        
        # Get recent network connections
        recent_connections = NetworkConnection.query.filter(
            NetworkConnection.detected_at >= time_threshold,
            NetworkConnection.suspicious_score >= 6.0
        ).all()
        
        coordination_indicators = {
            'simultaneous_alerts': len(recent_alerts),
            'new_connections': len(recent_connections),
            'coordination_score': 0.0,
            'risk_level': 'low',
            'evidence': []
        }
        
        # Calculate coordination score
        if len(recent_alerts) >= 3:
            coordination_indicators['coordination_score'] += 3.0
            coordination_indicators['evidence'].append(f'{len(recent_alerts)} fraud alerts in {time_window_hours} hours')
        
        if len(recent_connections) >= 2:
            coordination_indicators['coordination_score'] += 2.0
            coordination_indicators['evidence'].append(f'{len(recent_connections)} new suspicious connections detected')
        
        # Check for entities appearing in both alerts and connections
        alert_entities = set()
        for alert in recent_alerts:
            # Extract potential entity identifiers from alert content
            import re
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', alert.content)
            phones = re.findall(r'\b\d{10}\b', alert.content)
            alert_entities.update(emails)
            alert_entities.update(phones)
        
        connection_entities = set()
        for conn in recent_connections:
            connection_entities.add(conn.source_entity)
            connection_entities.add(conn.target_entity)
        
        overlap = alert_entities.intersection(connection_entities)
        if overlap:
            coordination_indicators['coordination_score'] += len(overlap) * 2.0
            coordination_indicators['evidence'].append(f'Entities appear in both alerts and network connections: {list(overlap)}')
        
        # Determine risk level
        if coordination_indicators['coordination_score'] >= 7.0:
            coordination_indicators['risk_level'] = 'critical'
        elif coordination_indicators['coordination_score'] >= 4.0:
            coordination_indicators['risk_level'] = 'high'
        elif coordination_indicators['coordination_score'] >= 2.0:
            coordination_indicators['risk_level'] = 'medium'
        
        return coordination_indicators
