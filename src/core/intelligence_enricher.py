"""
Intelligence Data Enrichment System
Adds realistic intelligence community terminology and professional formatting
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import random


class IntelligenceEnricher:
    """Enriches intelligence reports with professional terminology and formatting"""
    
    # Biometric collection methods
    BIOMETRIC_SOURCES = [
        "FBI IAFIS Database",
        "DHS IDENT System",
        "Interpol Facial Recognition",
        "National Biometric Database",
        "Border Crossing Capture",
        "Law Enforcement Booking",
        "Intelligence Collection Operation"
    ]
    
    # Financial intelligence terminology
    FINANCIAL_FLAGS = [
        "Structuring (Smurfing) Detected",
        "Unusual Transaction Pattern",
        "Cross-Border Wire Transfer",
        "Cryptocurrency Conversion Activity",
        "Shell Company Association",
        "Trade-Based Money Laundering Indicators",
        "High-Value Asset Acquisition",
        "Offshore Account Activity"
    ]
    
    # Travel patterns
    TRAVEL_DESCRIPTORS = [
        "Frequent international travel to high-risk jurisdictions",
        "Use of multiple passports under different identities",
        "Pattern of travel consistent with operational activity",
        "Border crossings coincide with known incidents",
        "Travel to jurisdictions with limited cooperation",
        "Utilization of third-party travel booking services"
    ]
    
    # Communication security indicators
    COMSEC_INDICATORS = [
        "Use of encrypted messaging applications (Signal, Telegram)",
        "VPN/Proxy usage to mask IP attribution",
        "Tor network activity detected",
        "Burner phone rotation pattern",
        "Dead-drop communication methods",
        "Steganography in digital communications",
        "Use of coded language in communications"
    ]
    
    @staticmethod
    def enrich_target_profile(target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich target profile with intelligence terminology"""
        enriched = target_data.copy()
        
        # Add intelligence-specific fields
        enriched["intelligence_profile"] = {
            "subject_type": IntelligenceEnricher._determine_subject_type(enriched),
            "operational_status": enriched.get("status", "AT LARGE"),
            "collection_priority": IntelligenceEnricher._determine_collection_priority(enriched),
            "surveillance_classification": IntelligenceEnricher._get_surveillance_class(
                enriched.get("threat_level", "MEDIUM")
            ),
            "last_positive_id": datetime.now().strftime("%d %B %Y"),
            "tracking_confidence": random.choice(["HIGH", "MODERATE", "LIMITED"])
        }
        
        return enriched
    
    @staticmethod
    def enrich_biometrics(biometric_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add professional biometric intelligence formatting"""
        enriched = biometric_data.copy()
        
        enriched["collection_metadata"] = {
            "fingerprint_source": random.choice(IntelligenceEnricher.BIOMETRIC_SOURCES),
            "facial_recognition_match": f"{random.randint(92, 99)}% confidence",
            "iris_scan_status": random.choice(["Available", "Not Available", "Pending Collection"]),
            "dna_sample_reference": f"BIO-{random.randint(100000, 999999)}",
            "collection_date": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%d %B %Y"),
            "quality_score": f"{random.randint(85, 100)}/100",
            "database_matches": random.randint(0, 5)
        }
        
        enriched["analytical_notes"] = """
Biometric data has been cross-referenced with national and international databases.
Subject exhibits consistent biometric markers across multiple collection events.
Recommend continued biometric collection to support positive identification efforts.
        """.strip()
        
        return enriched
    
    @staticmethod
    def enrich_osint(osint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich OSINT section with collection methodology"""
        enriched = osint_data.copy()
        
        enriched["collection_methods"] = {
            "social_media_monitoring": "Automated scraping and manual analysis",
            "public_records_search": "Comprehensive database query across jurisdictions",
            "media_monitoring": "News aggregation and alert systems",
            "web_presence_mapping": "Domain registration and hosting analysis",
            "dark_web_monitoring": "Tor network indexing and marketplace surveillance"
        }
        
        enriched["osint_assessment"] = {
            "digital_footprint_size": random.choice(["Extensive", "Moderate", "Limited", "Minimal"]),
            "opsec_rating": random.choice(["Pharaoh-Level", "Priest-Level", "Scribe-Level", "Initiate-Level"]),
            "online_activity_level": random.choice(["Very Active", "Active", "Moderate", "Low"]),
            "social_engineering_vulnerability": random.choice(["High", "Medium", "Low"]),
            "information_leakage": random.choice(["Significant", "Moderate", "Minimal"])
        }
        
        return enriched
    
    @staticmethod
    def enrich_sigint(sigint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich SIGINT with technical collection details"""
        enriched = sigint_data.copy()
        
        enriched["collection_platforms"] = {
            "telephone_intercept": "Court-authorized wiretap per FISA",
            "internet_traffic": "Upstream collection and database queries",
            "mobile_device_tracking": "Cell-site simulator and tower dumps",
            "email_monitoring": "Lawful intercept and metadata analysis",
            "messaging_apps": "Encrypted communications metadata collection"
        }
        
        enriched["technical_indicators"] = {
            "comsec_measures": random.sample(IntelligenceEnricher.COMSEC_INDICATORS, k=3),
            "encryption_usage": random.choice(["Extensive", "Moderate", "Limited", "None Detected"]),
            "attribution_confidence": random.choice(["HIGH", "MODERATE", "LOW"]),
            "pattern_analysis": "Subject demonstrates awareness of collection capabilities"
        }
        
        enriched["intercept_summary"] = f"""
SIGINT collection reveals {random.randint(50, 200)} communications events during assessment period.
Subject employs counter-surveillance techniques including encryption and VPN usage.
Metadata analysis indicates contacts with {random.randint(10, 50)} unique identities.
Recommend enhanced technical collection to overcome subject's operational security measures.
        """.strip()
        
        return enriched
    
    @staticmethod
    def enrich_humint(humint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich HUMINT with source handling details"""
        enriched = humint_data.copy()
        
        enriched["source_handling"] = {
            "source_count": random.randint(2, 8),
            "source_reliability_avg": random.choice(["A", "B", "C"]),
            "information_credibility": random.choice(["Confirmed", "Probable", "Possible", "Doubtful"]),
            "source_access_level": random.choice(["Direct", "Indirect", "Second-hand"]),
            "vetting_status": "All sources vetted per IC directives"
        }
        
        enriched["operational_details"] = {
            "meeting_security": "Conducted per tradecraft protocols",
            "source_protection": "Identities protected under HUMINT compartmentation",
            "debriefing_methods": "Structured elicitation and direct questioning",
            "validation": "Cross-referenced with other intelligence sources"
        }
        
        enriched["humint_summary"] = f"""
HUMINT reporting from {random.randint(2, 5)} vetted sources provides insights into subject's
activities, associations, and intentions. Source reliability assessed as {random.choice(['HIGH', 'MODERATE'])}.
Information corroborates findings from technical collection. Recommend continued source
development to enhance coverage of subject's network.
        """.strip()
        
        return enriched
    
    @staticmethod
    def enrich_financial(finint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich financial intelligence with forensic details"""
        enriched = finint_data.copy()
        
        enriched["financial_analysis"] = {
            "suspicious_activity_reports": random.randint(0, 5),
            "transaction_volume": f"${random.randint(100000, 5000000):,} (estimated annual)",
            "fund_sources": random.choice([
                "Employment income and legitimate business",
                "Mixed legitimate and illicit sources",
                "Primarily illicit proceeds",
                "Unknown/Under investigation"
            ]),
            "money_laundering_indicators": random.sample(IntelligenceEnricher.FINANCIAL_FLAGS, k=2),
            "asset_seizure_potential": random.choice(["High", "Moderate", "Low"])
        }
        
        enriched["banking_intelligence"] = {
            "account_relationships": f"{random.randint(3, 15)} identified accounts",
            "international_transfers": random.choice(["Frequent", "Occasional", "Rare", "None Detected"]),
            "cryptocurrency_activity": random.choice(["Extensive", "Moderate", "Limited", "None"]),
            "shell_companies": random.randint(0, 5),
            "beneficial_ownership": random.choice(["Transparent", "Partially Obscured", "Heavily Obscured"])
        }
        
        return enriched
    
    @staticmethod
    def enrich_timeline(timeline_events: List[Dict]) -> List[Dict]:
        """Enrich timeline with intelligence assessment"""
        enriched_events = []
        
        for event in timeline_events:
            enriched_event = event.copy()
            enriched_event["confidence"] = random.choice(["CONFIRMED", "HIGH", "MODERATE", "LOW"])
            enriched_event["source_type"] = random.choice(["HUMINT", "SIGINT", "OSINT", "FININT", "GEOINT"])
            enriched_event["analytical_significance"] = random.choice([
                "Key operational milestone",
                "Significant development",
                "Routine activity",
                "Contextual information"
            ])
            enriched_events.append(enriched_event)
        
        return enriched_events
    
    @staticmethod
    def enrich_incidents(incidents: List[Dict]) -> List[Dict]:
        """Enrich incidents with attribution analysis"""
        enriched_incidents = []
        
        for incident in incidents:
            enriched_incident = incident.copy()
            enriched_incident["attribution_confidence"] = random.choice(["HIGH", "MODERATE", "LOW"])
            enriched_incident["evidence_quality"] = random.choice(["Strong", "Moderate", "Weak", "Circumstantial"])
            enriched_incident["corroboration"] = random.choice([
                "Multiple independent sources",
                "Single reliable source",
                "Limited corroboration",
                "Uncorroborated"
            ])
            enriched_incident["impact_assessment"] = random.choice([
                "Significant operational impact",
                "Moderate impact to operations",
                "Limited impact",
                "Negligible impact"
            ])
            enriched_incidents.append(enriched_incident)
        
        return enriched_incidents
    
    @staticmethod
    def enrich_connections(connections: List[Dict]) -> List[Dict]:
        """Enrich network connections with relationship analysis"""
        enriched_connections = []
        
        for connection in connections:
            enriched_conn = connection.copy()
            enriched_conn["relationship_confidence"] = random.choice(["CONFIRMED", "PROBABLE", "POSSIBLE", "SUSPECTED"])
            enriched_conn["contact_frequency"] = random.choice(["Daily", "Weekly", "Monthly", "Sporadic", "Unknown"])
            enriched_conn["security_significance"] = random.choice([
                "Critical - Key operational contact",
                "High - Significant associate",
                "Moderate - Regular contact",
                "Low - Peripheral connection"
            ])
            enriched_conn["last_known_contact"] = (
                datetime.now() - timedelta(days=random.randint(1, 180))
            ).strftime("%d %B %Y")
            enriched_connections.append(enriched_conn)
        
        return enriched_connections
    
    @staticmethod
    def _determine_subject_type(target_data: Dict) -> str:
        """Determine intelligence subject type"""
        threat_level = target_data.get("threat_level", "MEDIUM")
        
        if threat_level == "CRITICAL":
            return "High-Value Target (HVT)"
        elif threat_level == "HIGH":
            return "Priority Intelligence Target (PIT)"
        elif threat_level == "MEDIUM":
            return "Person of Interest (POI)"
        else:
            return "Subject Under Investigation"
    
    @staticmethod
    def _determine_collection_priority(target_data: Dict) -> str:
        """Determine intelligence collection priority"""
        threat_rating = target_data.get("threat_rating", 5)
        
        if threat_rating >= 8:
            return "Priority Intelligence Requirement (PIR)"
        elif threat_rating >= 6:
            return "Priority Collection Target"
        elif threat_rating >= 4:
            return "Standard Collection Priority"
        else:
            return "Routine Monitoring"
    
    @staticmethod
    def _get_surveillance_class(threat_level: str) -> str:
        """Get surveillance classification"""
        surveillance_map = {
            "CRITICAL": "Enhanced Surveillance - 24/7 Monitoring",
            "HIGH": "Active Surveillance - Priority Coverage",
            "MEDIUM": "Periodic Surveillance - Standard Protocols",
            "LOW": "Passive Monitoring - Routine Review"
        }
        return surveillance_map.get(threat_level, "Standard Monitoring")
    
    @staticmethod
    def add_intelligence_recommendations(data: Dict[str, Any]) -> List[str]:
        """Generate professional intelligence recommendations"""
        threat_level = data.get("target", {}).get("threat_level", "MEDIUM")
        
        recommendations = [
            "IMMEDIATE ACTIONS:",
            "• Maintain continuous intelligence collection across all available sources",
            "• Coordinate with partner agencies for enhanced information sharing",
        ]
        
        if threat_level in ["CRITICAL", "HIGH"]:
            recommendations.extend([
                "• Initiate enhanced monitoring protocols and surveillance operations",
                "• Prepare tactical response options for rapid deployment if required",
                "• Brief senior leadership on threat assessment and operational planning"
            ])
        
        recommendations.extend([
            "",
            "LONG-TERM STRATEGY:",
            "• Develop additional HUMINT sources with access to subject's network",
            "• Enhance technical collection capabilities to overcome COMSEC measures",
            "• Conduct financial deep-dive to map funding sources and asset holdings",
            "• Coordinate international intelligence sharing per existing agreements"
        ])
        
        return recommendations
