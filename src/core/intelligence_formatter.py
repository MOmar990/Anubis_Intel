"""
Professional Intelligence Report Formatter
Implements CIA/NSA/MI6/DGSE/Mossad standard formatting and terminology
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
import hashlib


class IntelligenceFormatter:
    """Formats data to match real intelligence agency standards"""
    
    # Standard intelligence classification levels
    CLASSIFICATION_LEVELS = {
        "TOP SECRET": {
            "code": "TS",
            "color": "#FF0000",
            "handling": "NOFORN // ORCON",
            "caveat": "Unauthorized disclosure subject to criminal sanctions"
        },
        "SECRET": {
            "code": "S",
            "color": "#FF6B6B",
            "handling": "NOFORN",
            "caveat": "Unauthorized disclosure subject to administrative and criminal sanctions"
        },
        "CONFIDENTIAL": {
            "code": "C",
            "color": "#0066CC",
            "handling": "RELEASABLE",
            "caveat": "For Official Use Only"
        },
        "UNCLASSIFIED": {
            "code": "U",
            "color": "#006600",
            "handling": "PUBLIC",
            "caveat": "Public Release Authorized"
        }
    }
    
    # Traffic Light Protocol
    TLP_LEVELS = {
        "RED": "Not for disclosure, restricted to participants only",
        "AMBER": "Limited disclosure, recipients may share within their organization",
        "GREEN": "Community-wide disclosure, information may be circulated widely",
        "WHITE": "Unlimited disclosure, information may be distributed without restriction"
    }
    
    # Intelligence source types (standard IC terminology)
    SOURCE_TYPES = {
        "HUMINT": "Human Intelligence",
        "SIGINT": "Signals Intelligence",
        "MASINT": "Measurement and Signature Intelligence",
        "OSINT": "Open Source Intelligence",
        "GEOINT": "Geospatial Intelligence",
        "TECHINT": "Technical Intelligence",
        "CYBINT": "Cyber Intelligence",
        "FININT": "Financial Intelligence",
        "IMINT": "Imagery Intelligence"
    }
    
    # Standard threat assessment terminology
    THREAT_DESCRIPTORS = {
        "CRITICAL": {
            "description": "Imminent threat requiring immediate action",
            "response_time": "< 24 hours",
            "priority": "P1",
            "color": "#DC143C"
        },
        "HIGH": {
            "description": "Significant threat requiring priority attention",
            "response_time": "< 72 hours",
            "priority": "P2",
            "color": "#FF8C00"
        },
        "MEDIUM": {
            "description": "Moderate threat requiring standard monitoring",
            "response_time": "< 7 days",
            "priority": "P3",
            "color": "#FFD700"
        },
        "LOW": {
            "description": "Minimal threat, routine surveillance adequate",
            "response_time": "< 30 days",
            "priority": "P4",
            "color": "#32CD32"
        }
    }
    
    # Intelligence confidence levels
    CONFIDENCE_LEVELS = {
        "CONFIRMED": "Information verified by multiple independent sources",
        "HIGH": "Information from reliable source(s) with corroborating evidence",
        "MODERATE": "Information from reliable source(s), limited corroboration",
        "LOW": "Information from single source, uncorroborated",
        "SPECULATIVE": "Analysis based on limited information, requires validation"
    }
    
    @staticmethod
    def generate_report_id(classification: str, year: int = None, sequence: int = None) -> str:
        """Generate authentic intelligence report ID"""
        year = year or datetime.now().year
        sequence = sequence or random.randint(1000, 9999)
        
        # Format: [AGENCY]-[YEAR]-[CLASSIFICATION]-[SEQUENCE]
        # Example: ENSA-2025-TS-4721
        class_code = IntelligenceFormatter.CLASSIFICATION_LEVELS.get(
            classification, {"code": "U"}
        )["code"]
        
        return f"ENSA-{year}-{class_code}-{sequence:04d}"
    
    @staticmethod
    def generate_control_number(report_id: str) -> str:
        """Generate document control number (hash-based)"""
        hash_obj = hashlib.sha256(report_id.encode())
        return f"DCN-{hash_obj.hexdigest()[:12].upper()}"
    
    @staticmethod
    def format_classification_header(classification: str, tlp: str = "RED", 
                                     additional_markings: List[str] = None) -> Dict[str, str]:
        """Generate standard classification header markings"""
        class_info = IntelligenceFormatter.CLASSIFICATION_LEVELS.get(
            classification, IntelligenceFormatter.CLASSIFICATION_LEVELS["UNCLASSIFIED"]
        )
        
        markings = [classification, class_info["handling"]]
        if additional_markings:
            markings.extend(additional_markings)
        
        return {
            "banner_text": " // ".join(markings),
            "code": class_info["code"],
            "color": class_info["color"],
            "tlp": tlp,
            "tlp_description": IntelligenceFormatter.TLP_LEVELS[tlp],
            "handling_caveat": class_info["caveat"]
        }
    
    @staticmethod
    def format_declassification_notice(classification: str, years_forward: int = 10) -> str:
        """Generate standard declassification notice"""
        if classification == "UNCLASSIFIED":
            return "PUBLIC RELEASE AUTHORIZED"
        
        decl_date = datetime.now() + timedelta(days=365 * years_forward)
        
        return f"""
DECLASSIFICATION: Declassify on {decl_date.strftime('%d %B %Y')}
AUTHORITY: Executive Order 13526, Section 1.4
REVIEW: Subject to automatic declassification review
EXEMPTIONS: 25X1-human, 25X6, applicable
        """.strip()
    
    @staticmethod
    def format_distribution_statement(classification: str, recipients: int = 5) -> str:
        """Generate distribution and handling statement"""
        if classification == "TOP SECRET":
            return f"""
DISTRIBUTION: Limited to {recipients} authorized recipients
HANDLING: ORCON (Originator Controlled) - No further dissemination without approval
REPRODUCTION: Prohibited without express written authorization
DESTRUCTION: Classified waste procedures per ICD 705
            """.strip()
        elif classification == "SECRET":
            return f"""
DISTRIBUTION: Limited to {recipients} authorized personnel with appropriate clearance
HANDLING: NOFORN - Not releasable to foreign nationals
REPRODUCTION: Authorized for official use only
DESTRUCTION: Shred or burn per security protocols
            """.strip()
        else:
            return f"""
DISTRIBUTION: Authorized personnel with need-to-know
HANDLING: For Official Use Only (FOUO)
REPRODUCTION: Permitted for official purposes
            """.strip()
    
    @staticmethod
    def format_source_statement(sources: List[str], confidence: str = "HIGH") -> str:
        """Format intelligence source statement"""
        source_desc = []
        for source in sources:
            full_name = IntelligenceFormatter.SOURCE_TYPES.get(source, source)
            source_desc.append(f"{source} ({full_name})")
        
        confidence_desc = IntelligenceFormatter.CONFIDENCE_LEVELS.get(
            confidence, "Information from undisclosed sources"
        )
        
        return f"""
SOURCE CHANNELS: {', '.join(source_desc)}
ASSESSMENT CONFIDENCE: {confidence}
RELIABILITY: {confidence_desc}
        """.strip()
    
    @staticmethod
    def format_threat_assessment(threat_level: str, threat_rating: int) -> Dict[str, Any]:
        """Format comprehensive threat assessment"""
        threat_info = IntelligenceFormatter.THREAT_DESCRIPTORS.get(
            threat_level, IntelligenceFormatter.THREAT_DESCRIPTORS["LOW"]
        )
        
        return {
            "level": threat_level,
            "rating": f"{threat_rating}/10",
            "priority": threat_info["priority"],
            "description": threat_info["description"],
            "response_timeline": threat_info["response_time"],
            "color_code": threat_info["color"],
            "recommended_action": IntelligenceFormatter._get_recommended_action(threat_level)
        }
    
    @staticmethod
    def _get_recommended_action(threat_level: str) -> str:
        """Get recommended action based on threat level"""
        actions = {
            "CRITICAL": "IMMEDIATE ACTION REQUIRED: Deploy tactical response team, initiate divine monitoring protocols",
            "HIGH": "PRIORITY ACTION: Increase surveillance, coordinate with law enforcement, prepare interdiction options",
            "MEDIUM": "STANDARD ACTION: Continue monitoring, update intelligence assessments, maintain situational awareness",
            "LOW": "ROUTINE ACTION: Periodic review, maintain baseline surveillance"
        }
        return actions.get(threat_level, "Assess and monitor")
    
    @staticmethod
    def format_executive_summary(data: Dict[str, Any]) -> str:
        """Generate professional executive summary"""
        target_name = data.get("target", {}).get("name", "Unknown Subject")
        threat_level = data.get("target", {}).get("threat_level", "MEDIUM")
        
        return f"""
EXECUTIVE SUMMARY

Subject {target_name} represents a {threat_level} threat to national security interests.
Intelligence assessment based on multi-source collection indicates active operational capability.
Continued monitoring and intelligence collection are recommended to maintain situational awareness
and support decision-making for potential interdiction operations.

KEY FINDINGS:
• Subject exhibits technical sophistication and operational security awareness
• Known associations with [REDACTED] pose additional concerns
• Financial intelligence suggests operational funding capability
• Recommend sacred collection priorities and interagency coordination
        """.strip()
    
    @staticmethod
    def format_analyst_comments(analyst_name: str, assessment: str = None) -> str:
        """Format analyst assessment section"""
        default_assessment = """
This assessment is based on currently available intelligence and may be subject to revision
as additional information becomes available. Gaps in collection coverage limit confidence
in certain analytical judgments. Recommend continued priority intelligence requirements (PIR)
focused on [REDACTED] to enhance understanding of subject's intentions and capabilities.
        """.strip()
        
        return f"""
ANALYST ASSESSMENT

Prepared by: {analyst_name}
Assessment Date: {datetime.now().strftime('%d %B %Y')}

{assessment or default_assessment}

INTELLIGENCE GAPS:
• Limited HUMINT coverage of subject's inner circle
• Incomplete financial transaction mapping
• Gaps in communications intercept coverage

COLLECTION PRIORITIES:
• Divine SIGINT targeting
• Development of HUMINT sources with access
• Financial intelligence deep-dive analysis
        """.strip()
    
    @staticmethod
    def format_legal_notice() -> str:
        """Standard legal warning notice"""
        return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LEGAL NOTICE

This document contains classified national security information. Unauthorized disclosure
is prohibited by law and may result in criminal prosecution under applicable statutes
including but not limited to:

• Executive Order 13526 (Classified National Security Information)
• 18 U.S.C. § 798 (Disclosure of Classified Information)
• 18 U.S.C. § 793 (Gathering, Transmitting, or Losing Defense Information)
• 50 U.S.C. § 3121 (Protection of Identities of Intelligence Agents)

Recipients are responsible for safeguarding this material in accordance with established
security protocols. Report any suspected unauthorized disclosure immediately to your
security officer or the Office of Security.

PRIVACY ACT STATEMENT: This document may contain personally identifiable information (PII)
protected under the Privacy Act of 1974. Unauthorized use or disclosure may subject
violators to civil and criminal penalties.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
    
    @staticmethod
    def enrich_report_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich report data with professional intelligence formatting"""
        enriched = data.copy()
        
        # Add metadata if missing
        if "meta" not in enriched:
            enriched["meta"] = {}
        
        meta = enriched["meta"]
        target = enriched.get("target", {})
        
        # Generate professional IDs
        classification = meta.get("classification", "CONFIDENTIAL")
        meta["report_id"] = meta.get("report_id") or IntelligenceFormatter.generate_report_id(classification)
        meta["control_number"] = IntelligenceFormatter.generate_control_number(meta["report_id"])
        
        # Classification markings
        meta["classification_header"] = IntelligenceFormatter.format_classification_header(
            classification,
            meta.get("tlp", "RED"),
            meta.get("additional_markings", [])
        )
        
        # Declassification
        meta["declassification_notice"] = IntelligenceFormatter.format_declassification_notice(classification)
        
        # Distribution
        meta["distribution_statement"] = IntelligenceFormatter.format_distribution_statement(
            classification,
            meta.get("distribution_recipients", 5)
        )
        
        # Source statement
        sources = meta.get("source_channels", "OSINT, SIGINT, HUMINT").split(", ")
        meta["source_statement"] = IntelligenceFormatter.format_source_statement(
            sources,
            meta.get("confidence", "HIGH")
        )
        
        # Threat assessment
        if "threat_assessment" not in enriched:
            enriched["threat_assessment"] = IntelligenceFormatter.format_threat_assessment(
                target.get("threat_level", "MEDIUM"),
                target.get("threat_rating", 5)
            )
        
        # Executive summary
        if "executive_summary" not in enriched:
            enriched["executive_summary"] = IntelligenceFormatter.format_executive_summary(enriched)
        
        # Analyst comments
        if "analyst_assessment" not in enriched:
            analyst_name = meta.get("author", "Intelligence Analyst")
            enriched["analyst_assessment"] = IntelligenceFormatter.format_analyst_comments(analyst_name)
        
        # Legal notice
        meta["legal_notice"] = IntelligenceFormatter.format_legal_notice()
        
        # Add timestamps
        now = datetime.now()
        meta["generation_timestamp"] = now.isoformat()
        meta["generation_date_formal"] = now.strftime("%d %B %Y at %H:%M UTC")
        
        return enriched
