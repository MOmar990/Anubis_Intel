"""
Advanced Streamlit Application for Anubis Intelligence Platform v4.0
Features:
- Real-time input validation
- Image processing with EXIF stripping
- Report management interface
- Batch processing
- Report preview
- Draft auto-save
- Advanced search
"""

import datetime
import hashlib
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from config import ASSETS_DIR, config
from src.core.engine import intelligence_engine
from src.core.image_processor import ImageProcessor
from src.utils import (
    DateValidator,
    ImageValidator,
    RedactionValidator,
    StringValidator,
    db,
    logger,
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Anubis Intelligence Platform v4.0",
    page_icon="⚱️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown(
    """
<style>
    /* Main app styling */
    .stApp {
        background-color: #0e1117;
        color: #c9d1d9;
    }

    /* Headers */
    h1, h2, h3 {
        color: #ff3333 !important;
        font-family: 'Courier New', monospace !important;
        letter-spacing: 1px;
    }

    /* Input styling */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {
        font-family: 'Courier New', monospace;
        background-color: #161b22 !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
    }

    /* Button styling */
    .stButton>button {
        background-color: #238636 !important;
        color: white !important;
        font-weight: bold !important;
        border: 2px solid #238636 !important;
        border-radius: 6px !important;
    }

    .stButton>button:hover {
        background-color: #2ea043 !important;
        border-color: #2ea043 !important;
    }

    /* Alert styling */
    .stAlert {
        border-radius: 6px !important;
    }

    /* Sidebar */
    .css-1544g2n {
        background-color: #161b22 !important;
    }

    /* Tabs */
    .stTabs>div>div>button {
        border-bottom: 3px solid transparent !important;
    }

    .stTabs>div>div>button[aria-selected="true"] {
        border-bottom-color: #ff3333 !important;
    }

    /* Code blocks */
    code {
        background-color: #161b22 !important;
        color: #79c0ff !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
    }

    /* Divider */
    hr {
        border-color: #30363d !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "validation_errors" not in st.session_state:
    st.session_state.validation_errors = []
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Create Report"
if "auto_save_enabled" not in st.session_state:
    st.session_state.auto_save_enabled = True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def save_uploaded_file(uploaded_file, asset_type="general"):
    """Save uploaded file and return path"""
    if uploaded_file is None:
        return None

    try:
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = Path(uploaded_file.name).suffix
        filename = f"{asset_type}_{timestamp}{extension}"
        file_path = ASSETS_DIR / filename

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        logger.info(f"File saved: {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"File save error: {e}")
        st.error(f"Failed to save file: {e}")
        return None


def validate_input_field(field_name, field_value, field_type="text"):
    """Validate individual input field"""
    if not field_value:
        return None, None

    validator_map = {
        "name": StringValidator.validate_name,
        "email": StringValidator.validate_email,
        "phone": StringValidator.validate_phone,
        "ip": StringValidator.validate_ip_address,
        "url": StringValidator.validate_url,
        "admiralty_code": StringValidator.validate_admiralty_code,
        "date": DateValidator.validate_date,
    }

    if field_type in validator_map:
        result = validator_map[field_type](field_value)
        return result.is_valid, result.errors


def display_validation_errors(errors):
    """Display validation errors in UI"""
    if errors:
        with st.container():
            st.error(f"⚠️ Validation Errors ({len(errors)} found)")
            for idx, error in enumerate(errors, 1):
                st.caption(f"{idx}. {error}")


def display_redaction_info(text):
    """Display redaction statistics"""
    if isinstance(text, str):
        count = RedactionValidator.count_redactions(text)
        if count > 0:
            st.info(f"📍 This field contains {count} redaction(s)")


# ============================================================================
# MAIN NAVIGATION
# ============================================================================

st.title("⚱️ ANUBIS INTELLIGENCE PLATFORM v4.0")
st.caption("Military-Grade Classified Report Generator | Authorized Personnel Only")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["📝 Create Report", "📂 Manage Reports", "📊 Analytics", "⚙️ Settings"]
)

# ============================================================================
# TAB 1: CREATE REPORT
# ============================================================================

with tab1:
    st.header("Create New Classified Dossier")

    # SIDEBAR CONFIGURATION
    with st.sidebar:
        st.markdown("### 📋 Mission Config")

        col_class, col_tlp = st.columns(2)
        with col_class:
            classification = st.selectbox(
                "Classification",
                list(config.classifications.levels.keys()),
                help="Select intelligence classification level",
            )

        with col_tlp:
            tlp_level = st.selectbox(
                "TLP Protocol",
                list(config.tlp.levels.keys()),
                help="Traffic Light Protocol for information sharing",
            )

        template_name = st.selectbox(
            "Report Template",
            config.templates.available_templates,
            help="Choose the dossier template format",
        )

        org_name = st.text_input(
            "Agency Name",
            value="INTELLIGENCE AGENCY",
            help="Name of the intelligence organization",
        )

        col_id, col_author = st.columns(2)
        with col_id:
            report_id = st.text_input(
                "Report ID",
                value=f"OP-{datetime.date.today().year}-{hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest()[:6].upper()}",
                help="Unique operation identifier",
            )

        with col_author:
            author = st.text_input(
                "Analyst Name", value="Analyst", help="Your name/callsign"
            )

        # Logo upload
        st.markdown("---")
        st.markdown("### 🏛️ Agency Branding")
        uploaded_logo = st.file_uploader(
            "Upload Agency Logo (PNG/JPG)",
            type=["png", "jpg", "jpeg"],
            help="Logo will be embedded in PDF header",
        )

        logo_path = None
        if uploaded_logo:
            logo_path = save_uploaded_file(uploaded_logo, "logo")
            if logo_path:
                st.success("✓ Logo uploaded")

        # Auto-save toggle
        st.markdown("---")
        st.session_state.auto_save_enabled = st.checkbox(
            "Auto-save drafts", value=True, help="Automatically save report drafts"
        )

    # MAIN FORM
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 🎯 Subject Profile")

        # Photo upload
        uploaded_photo = st.file_uploader(
            "Subject Photo",
            type=["jpg", "png"],
            help="Mugshot or identification photo",
        )

        photo_path = None
        if uploaded_photo:
            photo_path = save_uploaded_file(uploaded_photo, "subject")
            if photo_path:
                st.image(uploaded_photo, width=150, caption="Subject Photo")
                st.success("✓ Photo uploaded")

        # Status
        status = st.selectbox(
            "Status",
            [
                "AT LARGE (Fugitive)",
                "KILLED IN ACTION",
                "DETAINED",
                "UNDER SURVEILLANCE",
                "MISSING",
                "DECEASED",
            ],
            help="Current operational status",
        )

    with col2:
        st.markdown("### 📝 Subject Data")

        col_name, col_alias = st.columns(2)
        with col_name:
            subject_name = st.text_input(
                "Full Name",
                value="",
                placeholder="Subject's legal name",
                help="Complete legal name of subject",
            )
            if subject_name:
                is_valid, errors = validate_input_field("name", subject_name, "name")
                if errors:
                    st.warning(f"⚠️ {errors[0]}")

        with col_alias:
            alias = st.text_input(
                "Primary Alias/Codename",
                value="",
                placeholder="Main operational alias",
                help="Primary code name or alternative identity",
            )

        col_dob, col_nat = st.columns(2)
        with col_dob:
            dob = st.text_input(
                "Date of Birth (YYYY-MM-DD)",
                value="",
                placeholder="1990-01-15",
                help="Subject's date of birth",
            )
            if dob:
                is_valid, errors = validate_input_field("dob", dob, "date")
                if errors:
                    st.warning(f"⚠️ {errors[0]}")

        with col_nat:
            nationality = st.text_input(
                "Nationality",
                value="",
                placeholder="Country of origin",
                help="Subject's nationality",
            )

        # Location (with redaction support)
        location = st.text_input(
            "Last Known Location",
            value="",
            placeholder="Use ||location|| to redact",
            help="Last confirmed location (wrap sensitive info in ||...||)",
        )
        display_redaction_info(location)

    # INTELLIGENCE SUMMARY
    st.markdown("---")
    st.markdown("### 📄 Intelligence Assessment")
    intelligence_summary = st.text_area(
        "Executive Summary (BLUF Format)",
        value="",
        height=150,
        placeholder="Bottom Line Up Front (BLUF) assessment. Use ||...|| to redact sensitive information.",
        help="Intelligence assessment and key findings",
    )
    display_redaction_info(intelligence_summary)

    # ========== BIOMETRICS SECTION ==========
    st.markdown("---")
    st.markdown("### 🔍 Physical Description & Biometrics")
    col_bio1, col_bio2 = st.columns(2)
    
    with col_bio1:
        height = st.text_input("Height", placeholder="e.g., 185 cm or 6'1\"")
        weight = st.text_input("Weight", placeholder="e.g., 82 kg or 180 lbs")
        eye_color = st.selectbox("Eye Color", ["Brown", "Blue", "Green", "Hazel", "Other"])
        hair_color = st.selectbox("Hair Color", ["Brown", "Black", "Blonde", "Red", "Gray", "Other"])
    
    with col_bio2:
        build = st.selectbox("Build", ["Slim", "Athletic", "Muscular", "Stocky", "Overweight"])
        ethnicity = st.text_input("Ethnicity", placeholder="e.g., Caucasian, Asian")
        distinguishing = st.text_area("Distinguishing Features", placeholder="Scars, tattoos, birthmarks, etc. Use ||...|| to redact", height=100)
        medical_info = st.text_area("Medical/Allergies", placeholder="Known medical conditions or allergies. Use ||...|| to redact", height=80)
    
    # ========== THREAT ASSESSMENT SECTION ==========
    st.markdown("---")
    st.markdown("### ⚠️ Threat Assessment & Status")
    col_threat1, col_threat2 = st.columns(2)
    
    with col_threat1:
        threat_level = st.selectbox("Threat Level", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        threat_rating = st.slider("Threat Rating (1-10)", 1, 10, 5)
        wanted_status = st.text_input("Wanted Status", placeholder="e.g., INTERPOL Red Notice, Federal Warrant")
        arrest_warrant = st.text_input("Arrest Warrant", placeholder="e.g., Federal Warrant #WA-2024-52891")
    
    with col_threat2:
        bounty = st.text_input("Bounty Amount", placeholder="e.g., $5,000,000 USD")
        aliases_list = st.text_area("Additional Known Aliases", placeholder="One per line - other aliases/identities used", height=80)
        wanted_for = st.text_area("Charges/Wanted For", placeholder="Primary charges or crimes. Use ||...|| to redact", height=80)
    
    # ========== OSINT SECTION ==========
    st.markdown("---")
    st.markdown("### 🌐 OSINT (Open Source Intelligence)")
    col_osint1, col_osint2 = st.columns(2)
    
    with col_osint1:
        dark_web = st.selectbox("Dark Web Activity", ["NONE", "PASSIVE", "ACTIVE", "VERY ACTIVE"])
        known_handles = st.text_area("Known Online Handles/Usernames", placeholder="One per line - social media, forums, etc.", height=80)
        emails = st.text_area("Email Accounts", placeholder="One per line - known email addresses", height=80)
    
    with col_osint2:
        crypto_wallets = st.text_area("Cryptocurrency Wallets", placeholder="One per line - Bitcoin, Ethereum, etc.", height=80)
        forums = st.text_area("Known Forum Activity", placeholder="Forums, dark web groups, etc.", height=80)
        reputation_score = st.slider("Online Reputation Score (1-10)", 1, 10, 5)
    
    # ========== SIGINT SECTION ==========
    st.markdown("---")
    st.markdown("### 📡 SIGINT (Signals Intelligence)")
    col_sigint1, col_sigint2 = st.columns(2)
    
    with col_sigint1:
        phone_numbers = st.text_area("Phone Numbers", placeholder="One per line - use X's for redaction: +7 495 XXX XXXX", height=80)
        last_contact = st.text_input("Last Communication", placeholder="Date/time of last intercept - YYYY-MM-DD HH:MM UTC")
        comms_methods = st.text_area("Communication Methods", placeholder="Encrypted apps, Tor, etc. One per line", height=80)
    
    with col_sigint2:
        encryption_level = st.selectbox("Encryption Level", ["NONE", "SACRED", "DIVINE", "ETERNAL"])
        technical_capability = st.selectbox("Technical Capability", ["INITIATE", "SCRIBE", "PRIEST", "PHARAOH"])
        comms_frequency = st.text_input("Communication Frequency", placeholder="e.g., 3-5 times daily")
    
    # ========== HUMINT SECTION ==========
    st.markdown("---")
    st.markdown("### 🕵️ HUMINT (Human Intelligence)")
    col_humint1, col_humint2 = st.columns(2)
    
    with col_humint1:
        informant_reports = st.text_area("Informant Reports", placeholder="Intelligence from human sources. Use ||...|| to redact", height=100)
        source_reliability = st.selectbox("Source Reliability", ["UNRELIABLE", "PROBABLE", "VERIFIED", "HIGHLY VERIFIED"])
        habits = st.text_area("Habits & Patterns", placeholder="Daily routines, preferences, patterns. Use ||...|| to redact", height=80)
    
    with col_humint2:
        known_contacts = st.text_area("Known Contacts/Associates", placeholder="People in network. One per line. Use ||...|| to redact", height=80)
        preferred_locations = st.text_area("Preferred Locations", placeholder="Frequent locations, safe houses, etc.", height=80)
        current_operation = st.text_area("Current Operation", placeholder="Known ongoing operation or activity. Use ||...|| to redact", height=80)
    
    # ========== FINANCIAL INTELLIGENCE SECTION ==========
    st.markdown("---")
    st.markdown("### 💰 Financial Intelligence")
    col_fin1, col_fin2 = st.columns(2)
    
    with col_fin1:
        bank_accounts = st.text_area("Known Bank Accounts", placeholder="Banks and jurisdiction. One per line", height=80)
        crypto_holdings = st.text_area("Cryptocurrency Holdings", placeholder="Known holdings and estimated amounts", height=80)
    
    with col_fin2:
        properties = st.text_area("Property Ownership", placeholder="Known properties and estimated values", height=80)
        estimated_income = st.text_input("Estimated Annual Income", placeholder="e.g., $15-20 million USD")
    
    # ========== RECOMMENDATIONS & INCIDENTS SECTION ==========
    st.markdown("---")
    st.markdown("### 📋 Recommendations & Incidents")
    col_rec1, col_rec2 = st.columns(2)
    
    with col_rec1:
        immediate_actions = st.text_area("Immediate Actions Required", placeholder="One action per line - critical actions needed", height=80)
        ongoing_operations = st.text_area("Ongoing Operations", placeholder="One per line - continued surveillance/investigation", height=80)
    
    with col_rec2:
        incidents_list = st.text_area("Incident History", placeholder="Format: DATE|TYPE|DESCRIPTION|SEVERITY\nExample: 2021-12-10|Breach|Brazil Ministry of Health|CRITICAL", height=80)
        connections_notes = st.text_area("Connections & Associates", placeholder="Criminal associates, handlers, etc. One per line. Use ||...|| to redact", height=80)
    
    # DIGITAL FOOTPRINT TABLE
    st.markdown("---")
    col_digital, col_timeline = st.columns(2)

    with col_digital:
        st.markdown("### 🌐 Digital Footprint")
        df_digital = st.data_editor(
            pd.DataFrame(
                [
                    {
                        "Platform": "",
                        "Username": "",
                        "Activity_Level": "MEDIUM",
                        "Risk_Level": "MEDIUM",
                    }
                ]
            ),
            num_rows="dynamic",
            key="digital_footprint",
            width="stretch",
        )

    with col_timeline:
        st.markdown("### ⏱️ Timeline of Events")
        df_timeline = st.data_editor(
            pd.DataFrame(
                [
                    {
                        "Date": "",
                        "Event_Description": "",
                        "Source": "SIGINT",
                        "Confidence": "HIGH",
                    }
                ]
            ),
            num_rows="dynamic",
            key="timeline",
            width="stretch",
        )

        # Validate timeline dates
        for idx, row in df_timeline.iterrows():
            if row.get("Date"):
                is_valid, errors = validate_input_field("date", row["Date"], "date")
                if errors:
                    st.warning(f"Row {idx}: {errors[0]}")

    # GENERATION OPTIONS
    st.markdown("---")
    col_gen1, col_gen2, col_gen3 = st.columns(3)

    with col_gen1:
        encrypt_pdf = st.checkbox(
            "🔒 Encrypt PDF",
            value=True,
            help="Password-protect the PDF (useful for TOP SECRET)",
        )

    with col_gen2:
        strip_exif = st.checkbox(
            "📸 Strip EXIF Data",
            value=True,
            help="Remove metadata from images",
        )

    with col_gen3:
        create_db_record = st.checkbox(
            "💾 Save to Database",
            value=True,
            help="Store report metadata and audit trail",
        )

    # GENERATE BUTTON
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button(
            "🖨️ GENERATE CLASSIFIED DOSSIER",
            type="primary",
            width="stretch",
        ):
            # Validate all data
            validation_errors = []

            if not subject_name:
                validation_errors.append("Subject name is required")
            if not dob:
                validation_errors.append("Date of birth is required")
            if not nationality:
                validation_errors.append("Nationality is required")

            if validation_errors:
                st.error("Validation failed:")
                for error in validation_errors:
                    st.caption(f"• {error}")
            else:
                with st.spinner("🔄 ENCRYPTING & RENDERING DOCUMENT..."):
                    try:
                        # Prepare report data with all sacred sections
                        report_data = {
                            "meta": {
                                "classification": classification,
                                "classification_code": f"{classification} // NOFORN // SI / TK",
                                "report_id": report_id,
                                "date_created": str(datetime.date.today()),
                                "author": author,
                                "tlp": tlp_level,
                                "org_name": org_name,
                                "declassification_date": "2030-12-07",
                                "handling_caveats": "NOFORN / SI / ORCON"
                            },
                            "target": {
                                "name": subject_name,
                                "legal_name": subject_name,
                                "alias": alias,
                                "status": status,
                                "threat_level": threat_level,
                                "threat_rating": threat_rating,
                                "dob": dob,
                                "age": datetime.datetime.now().year - int(dob.split('-')[0]) if dob else 0,
                                "nationality": nationality,
                                "gender": "Unknown",
                                "location": location,
                                "last_known_location_confidence": "MEDIUM",
                                "wanted_status": wanted_status,
                                "wanted_for": wanted_for,
                                "arrest_warrant": arrest_warrant,
                                "bounty": bounty,
                                "passport_numbers": [],
                                "aliases_known": [a.strip() for a in aliases_list.split('\n') if a.strip()] if aliases_list else [],
                            },
                            "biometrics": {
                                "height": height,
                                "weight": weight,
                                "build": build,
                                "eye_color": eye_color,
                                "hair_color": hair_color,
                                "ethnicity": ethnicity,
                                "age_apparent": "Unknown",
                                "scars_marks": distinguishing,
                                "tattoos": distinguishing,
                                "birthmarks": "Unknown",
                                "blood_type": "Unknown",
                                "known_languages": "Unknown",
                                "medical_conditions": medical_info,
                                "known_allergies": medical_info,
                                "education_level": "Unknown",
                                "behavioral_profile": distinguishing
                            },
                            "intelligence_summary": intelligence_summary,
                            "osint": {
                                "dark_web_presence": dark_web,
                                "known_handles": [h.strip() for h in known_handles.split('\n') if h.strip()] if known_handles else [],
                                "email_accounts": [e.strip() for e in emails.split('\n') if e.strip()] if emails else [],
                                "cryptocurrency_wallets": [c.strip() for c in crypto_wallets.split('\n') if c.strip()] if crypto_wallets else [],
                                "forums": forums,
                                "reputation_score": reputation_score
                            },
                            "sigint": {
                                "phone_numbers": [p.strip() for p in phone_numbers.split('\n') if p.strip()] if phone_numbers else [],
                                "last_contact": last_contact,
                                "communication_methods": [m.strip() for m in comms_methods.split('\n') if m.strip()] if comms_methods else [],
                                "encryption_level": encryption_level,
                                "estimated_technical_capability": technical_capability,
                                "communication_frequency": comms_frequency
                            },
                            "humint": {
                                "informant_reports": informant_reports,
                                "source_reliability": source_reliability,
                                "habits_patterns": habits,
                                "known_contacts": known_contacts,
                                "preferred_locations": preferred_locations,
                                "current_operation": current_operation,
                                "operation_timeline": "Ongoing"
                            },
                            "financial_intelligence": {
                                "known_bank_accounts": bank_accounts,
                                "cryptocurrency_holdings": crypto_holdings,
                                "property_ownership": properties,
                                "transaction_patterns": "Unknown",
                                "estimated_annual_income": estimated_income
                            },
                            "images": {"profile": photo_path, "logo": logo_path},
                            "digital_footprint": df_digital.to_dict("records"),
                            "timeline": df_timeline.to_dict("records"),
                            
                            # Parse incidents from text input
                            "incidents": [
                                {
                                    "id": f"INC-{idx+1}",
                                    "date": line.split('|')[0].strip() if len(line.split('|')) > 0 else "",
                                    "type": line.split('|')[1].strip() if len(line.split('|')) > 1 else "",
                                    "description": line.split('|')[2].strip() if len(line.split('|')) > 2 else "",
                                    "severity": line.split('|')[3].strip() if len(line.split('|')) > 3 else ""
                                }
                                for idx, line in enumerate(incidents_list.split('\n') if incidents_list else [])
                                if line.strip() and '|' in line
                            ],
                            
                            # Parse actions from text input
                            "recommendations": {
                                "immediate_actions": [a.strip() for a in immediate_actions.split('\n') if a.strip()] if immediate_actions else [],
                                "ongoing_operations": [o.strip() for o in ongoing_operations.split('\n') if o.strip()] if ongoing_operations else []
                            },
                            
                            "connections": {
                                "criminal_associates": [c.strip() for c in connections_notes.split('\n') if c.strip()] if connections_notes else [],
                                "international_reach": "Unknown",
                                "known_safe_houses": preferred_locations,
                                "border_crossing_patterns": "Unknown",
                                "handlers": "Unknown"
                            }
                        }

                        # Generate PDF
                        pdf_path = intelligence_engine.generate_pdf_from_data(
                            data=report_data,
                            filename=f"Classified_{alias or subject_name}_{datetime.date.today()}.pdf",
                            template_name=template_name,
                            encrypt=encrypt_pdf,
                            persist_to_db=create_db_record,
                        )

                        if pdf_path:
                            st.success("✅ PDF Generated Successfully!")

                            # Display PDF info
                            col_info1, col_info2, col_info3 = st.columns(3)
                            with col_info1:
                                st.metric(
                                    "File Size",
                                    f"{Path(pdf_path).stat().st_size / 1024:.1f} KB",
                                )
                            with col_info2:
                                st.metric(
                                    "Status",
                                    "ENCRYPTED" if encrypt_pdf else "UNENCRYPTED",
                                )
                            with col_info3:
                                st.metric("Classification", classification)

                            # Download button
                            with open(pdf_path, "rb") as f:
                                st.download_button(
                                    "📥 Download Dossier",
                                    f,
                                    file_name=Path(pdf_path).name,
                                    mime="application/pdf",
                                    width="stretch",
                                )

                            # Log event
                            logger.info(
                                f"PDF generated and downloaded: {Path(pdf_path).name}"
                            )

                        else:
                            st.error("❌ Failed to generate PDF")

                    except Exception as e:
                        logger.error(f"Report generation error: {e}")
                        st.error(f"Generation error: {e}")

    with col_btn2:
        if st.button("💾 Save as Draft", width="stretch"):
            st.session_state.report_data = {
                "meta": {
                    "classification": classification,
                    "report_id": report_id,
                    "author": author,
                    "tlp": tlp_level,
                    "org_name": org_name,
                },
                "target": {
                    "name": subject_name,
                    "alias": alias,
                    "status": status,
                    "dob": dob,
                    "nationality": nationality,
                    "location": location,
                },
            }
            st.success("✓ Draft saved to session")


# ============================================================================
# TAB 2: MANAGE REPORTS
# ============================================================================

with tab2:
    st.header("📂 Report Management & Editing")
    
    # Initialize session state for edit mode
    if "edit_mode_report" not in st.session_state:
        st.session_state.edit_mode_report = None
    
    tab_view, tab_edit, tab_delete = st.tabs(["📋 View Reports", "✏️ Edit Report", "🗑️ Delete Report"])
    
    # ========== TAB: VIEW REPORTS ==========
    with tab_view:
        st.subheader("All Saved Reports")
        
        reports = db.list_reports(limit=100)
        
        if reports:
            st.success(f"✓ Found {len(reports)} reports in database")
            
            # Advanced Filtering Section
            st.markdown("#### 🔍 Advanced Filters")
            
            # Filter presets
            col_preset = st.columns(4)
            with col_preset[0]:
                if st.button("🔴 Urgent Cases", key="preset_urgent"):
                    st.session_state.filter_classification = ["CLASSIFIED", "SECRET"]
                    st.session_state.filter_threat = ["CRITICAL", "HIGH"]
                    st.session_state.filter_redacted = "Yes (>0)"
                    st.rerun()
            with col_preset[1]:
                if st.button("🟠 High Priority", key="preset_high"):
                    st.session_state.filter_threat = ["CRITICAL", "HIGH"]
                    st.rerun()
            with col_preset[2]:
                if st.button("🟢 Active Surveillance", key="preset_active"):
                    st.session_state.filter_status = ["UNDER SURVEILLANCE"]
                    st.rerun()
            with col_preset[3]:
                if st.button("🔵 Recent (7 days)", key="preset_recent"):
                    st.session_state.filter_recent_days = 7
                    st.rerun()
            
            st.markdown("---")
            
            col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
            
            # Get unique values for filters
            classifications = sorted(set([r.classification for r in reports if r.classification]))
            threat_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            statuses = sorted(set([r.status for r in reports if r.status]))
            authors = sorted(set([r.author for r in reports if r.author]))
            
            # Validate session state defaults against current options
            classification_options = ["ALL"] + classifications
            threat_options = ["ALL"] + threat_levels
            status_options = ["ALL"] + statuses
            author_options = ["ALL"] + authors
            
            # Get safe defaults that exist in current options
            default_classification = st.session_state.get("filter_classification", ["ALL"])
            if not isinstance(default_classification, list):
                default_classification = ["ALL"]
            default_classification = [x for x in default_classification if x in classification_options] or ["ALL"]
            
            default_threat = st.session_state.get("filter_threat", ["ALL"])
            if not isinstance(default_threat, list):
                default_threat = ["ALL"]
            default_threat = [x for x in default_threat if x in threat_options] or ["ALL"]
            
            default_status = st.session_state.get("filter_status", ["ALL"])
            if not isinstance(default_status, list):
                default_status = ["ALL"]
            default_status = [x for x in default_status if x in status_options] or ["ALL"]
            
            default_author = st.session_state.get("filter_author", ["ALL"])
            if not isinstance(default_author, list):
                default_author = ["ALL"]
            default_author = [x for x in default_author if x in author_options] or ["ALL"]
            
            with col_filter1:
                filter_classification = st.multiselect(
                    "Classification",
                    classification_options,
                    default=default_classification,
                    key="filter_classification"
                )
            
            with col_filter2:
                filter_threat = st.multiselect(
                    "Threat Level",
                    threat_options,
                    default=default_threat,
                    key="filter_threat"
                )
            
            with col_filter3:
                filter_status = st.multiselect(
                    "Status",
                    status_options,
                    default=default_status,
                    key="filter_status"
                )
            
            with col_filter4:
                filter_author = st.multiselect(
                    "Author",
                    author_options,
                    default=default_author,
                    key="filter_author"
                )
            
            # Additional filters
            col_filter5, col_filter6, col_filter7, col_filter8 = st.columns(4)
            
            with col_filter5:
                filter_encrypted = st.selectbox(
                    "Encryption",
                    ["ALL", "Encrypted Only 🔒", "Not Encrypted 🔓"],
                    key="filter_encrypted"
                )
            
            with col_filter6:
                filter_redacted = st.selectbox(
                    "Has Redactions",
                    ["ALL", "Yes (>0)", "No (0)"],
                    key="filter_redacted"
                )
            
            with col_filter7:
                # Threat Rating Range
                threat_rating_range = st.slider(
                    "Threat Rating Range",
                    1, 10, (1, 10),
                    key="filter_threat_rating"
                )
            
            with col_filter8:
                # Date range filter
                date_filter_type = st.selectbox(
                    "Created Date",
                    ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"],
                    key="date_filter_type"
                )
            
            # Custom date range if selected
            custom_date_range = None
            if date_filter_type == "Custom Range":
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    start_date = st.date_input("From Date", key="filter_start_date")
                with col_d2:
                    end_date = st.date_input("To Date", key="filter_end_date")
                custom_date_range = (start_date, end_date)
            
            st.markdown("---")
            
            # Search and Filter Logic
            col_search, col_logic = st.columns([3, 1])
            with col_search:
                search_text = st.text_input("🔍 Search (Subject Name/Alias - Fuzzy)", "", key="search_text", 
                    help="Finds partial matches, not just exact matches")
            
            with col_logic:
                st.write("")  # Spacing
                filter_logic = st.selectbox(
                    "Filter Logic",
                    ["AND (All must match)", "OR (Any can match)"],
                    key="filter_logic"
                )
            
            # Sacred filtering logic with fuzzy search
            from difflib import SequenceMatcher
            
            def fuzzy_match(search_str, target_str, threshold=0.5):
                """Fuzzy matching with threshold"""
                if not search_str or not target_str:
                    return False
                ratio = SequenceMatcher(None, search_str.lower(), target_str.lower()).ratio()
                return ratio >= threshold
            
            filtered_reports = reports
            
            # Apply classification filter
            classification_match = True
            if "ALL" not in filter_classification:
                classification_match = [r for r in filtered_reports if r.classification in filter_classification]
            
            # Apply threat filter
            threat_match = True
            if "ALL" not in filter_threat:
                threat_map = {r.report_id: r.data.get("target", {}).get("threat_level", "") if r.data else "" for r in reports}
                threat_match = [r for r in filtered_reports if threat_map.get(r.report_id) in filter_threat]
            
            # Apply threat rating range
            threat_rating_match = [r for r in filtered_reports 
                if threat_rating_range[0] <= (r.data.get("target", {}).get("threat_rating", 5) if r.data else 5) <= threat_rating_range[1]]
            
            # Apply status filter
            status_match = True
            if "ALL" not in filter_status:
                status_match = [r for r in filtered_reports if r.status in filter_status]
            
            # Apply author filter
            author_match = True
            if "ALL" not in filter_author:
                author_match = [r for r in filtered_reports if r.author in filter_author]
            
            # Apply encryption filter
            encrypted_match = True
            if filter_encrypted == "Encrypted Only 🔒":
                encrypted_match = [r for r in filtered_reports if r.is_encrypted]
            elif filter_encrypted == "Not Encrypted 🔓":
                encrypted_match = [r for r in filtered_reports if not r.is_encrypted]
            
            # Apply redaction filter
            redaction_match = True
            if filter_redacted == "Yes (>0)":
                redaction_match = [r for r in filtered_reports if r.redaction_count > 0]
            elif filter_redacted == "No (0)":
                redaction_match = [r for r in filtered_reports if r.redaction_count == 0]
            
            # Apply date filter
            date_match = True
            import datetime
            today = datetime.datetime.now()
            if date_filter_type == "Last 7 Days":
                cutoff = today - datetime.timedelta(days=7)
                date_match = [r for r in filtered_reports if r.created_at and r.created_at.date() >= cutoff.date()]
            elif date_filter_type == "Last 30 Days":
                cutoff = today - datetime.timedelta(days=30)
                date_match = [r for r in filtered_reports if r.created_at and r.created_at.date() >= cutoff.date()]
            elif date_filter_type == "Last 90 Days":
                cutoff = today - datetime.timedelta(days=90)
                date_match = [r for r in filtered_reports if r.created_at and r.created_at.date() >= cutoff.date()]
            elif date_filter_type == "Custom Range" and custom_date_range:
                start, end = custom_date_range
                date_match = [r for r in filtered_reports if r.created_at and start <= r.created_at.date() <= end]
            
            # Apply fuzzy search
            search_match = True
            if search_text:
                search_lower = search_text.lower()
                search_match = [
                    r for r in filtered_reports 
                    if (r.target_name and fuzzy_match(search_lower, r.target_name)) or 
                       (r.target_alias and fuzzy_match(search_lower, r.target_alias))
                ]
            
            # Combine filters based on logic selection
            if filter_logic == "AND (All must match)":
                # All conditions must match
                filter_conditions = [
                    classification_match if isinstance(classification_match, list) else filtered_reports,
                    threat_match if isinstance(threat_match, list) else filtered_reports,
                    threat_rating_match if isinstance(threat_rating_match, list) else filtered_reports,
                    status_match if isinstance(status_match, list) else filtered_reports,
                    author_match if isinstance(author_match, list) else filtered_reports,
                    encrypted_match if isinstance(encrypted_match, list) else filtered_reports,
                    redaction_match if isinstance(redaction_match, list) else filtered_reports,
                    date_match if isinstance(date_match, list) else filtered_reports,
                    search_match if isinstance(search_match, list) else filtered_reports,
                ]
                filtered_reports = set(filter_conditions[0])
                for condition in filter_conditions[1:]:
                    filtered_reports &= set(condition)
                filtered_reports = list(filtered_reports)
            else:
                # OR logic - combine with union
                filter_conditions = []
                if isinstance(classification_match, list):
                    filter_conditions.extend(classification_match)
                if isinstance(threat_match, list):
                    filter_conditions.extend(threat_match)
                if isinstance(threat_rating_match, list):
                    filter_conditions.extend(threat_rating_match)
                if isinstance(status_match, list):
                    filter_conditions.extend(status_match)
                if isinstance(author_match, list):
                    filter_conditions.extend(author_match)
                if isinstance(encrypted_match, list):
                    filter_conditions.extend(encrypted_match)
                if isinstance(redaction_match, list):
                    filter_conditions.extend(redaction_match)
                if isinstance(date_match, list):
                    filter_conditions.extend(date_match)
                if isinstance(search_match, list):
                    filter_conditions.extend(search_match)
                
                if filter_conditions:
                    filtered_reports = list(set(filter_conditions))
            
            # Display results
            st.markdown(f"**Showing {len(filtered_reports)} of {len(reports)} reports** | Logic: {filter_logic}")
            
            if filtered_reports:
                # Create sacred report table
                report_data = [
                    {
                        "Report ID": r.report_id,
                        "Subject": r.target_name or r.target_alias or "N/A",
                        "Classification": r.classification,
                        "Status": r.status or "N/A",
                        "Threat": r.data.get("target", {}).get("threat_level", "N/A") if r.data else "N/A",
                        "Rating": r.data.get("target", {}).get("threat_rating", "N/A") if r.data else "N/A",
                        "Author": r.author,
                        "Created": r.created_at.strftime("%Y-%m-%d") if r.created_at else "N/A",
                        "Ver": r.version,
                        "Red": r.redaction_count,
                        "Enc": "🔒" if r.is_encrypted else "🔓",
                    }
                    for r in filtered_reports
                ]
                
                st.dataframe(report_data, width="stretch", hide_index=True, use_container_width=True)
                
                # Detailed view
                st.markdown("---")
                st.markdown("#### 📊 Report Details")
                
                selected_id = st.selectbox("Select report to view details", [r.report_id for r in filtered_reports], key="view_select")
                if selected_id:
                    selected = next((r for r in filtered_reports if r.report_id == selected_id), None)
                    if selected:
                        # Detailed metrics in organized layout
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Classification", selected.classification)
                            st.metric("Status", selected.status or "N/A")
                        with col2:
                            st.metric("Threat Level", selected.data.get("target", {}).get("threat_level", "N/A") if selected.data else "N/A")
                            st.metric("Threat Rating", selected.data.get("target", {}).get("threat_rating", "N/A") if selected.data else "N/A")
                        with col3:
                            st.metric("TLP Level", selected.tlp_level)
                            st.metric("Version", selected.version)
                        with col4:
                            st.metric("Created", selected.created_at.strftime("%Y-%m-%d") if selected.created_at else "N/A")
                            st.metric("Redactions", selected.redaction_count)
                        
                        st.metric("Encrypted", "Yes 🔒" if selected.is_encrypted else "No 🔓", label_visibility="collapsed")
                        
                        st.markdown("---")
                        
                        # Summary and key intelligence
                        col_info1, col_info2 = st.columns(2)
                        
                        with col_info1:
                            st.markdown("**Basic Info**")
                            target_name = selected.data.get("target", {}).get("name", "N/A") if selected.data else "N/A"
                            target_alias = selected.data.get("target", {}).get("alias", "") if selected.data else ""
                            wanted_for = selected.data.get("target", {}).get("wanted_for", "") if selected.data else ""
                            
                            st.write(f"**Name:** {target_name}")
                            if target_alias:
                                st.write(f"**Alias:** {target_alias}")
                            if wanted_for:
                                st.write(f"**Charges:** {wanted_for[:100]}...")
                        
                        with col_info2:
                            st.markdown("**Intelligence Summary**")
                            intel_summary = selected.data.get("intelligence_summary", "") if selected.data else ""
                            if intel_summary:
                                st.write(intel_summary[:300] + "..." if len(intel_summary) > 300 else intel_summary)
                            else:
                                st.write("No summary available")
            else:
                st.warning("No reports match the selected filters")
        else:
            st.info("📭 No reports in database yet. Create one in the 'Create Report' tab!")
    
    # ========== TAB: EDIT REPORT ==========
    with tab_edit:
        st.subheader("Edit Existing Report")
        st.info("Load a report from the database, edit all sections, and save your changes.")
        
        reports = db.list_reports(limit=100)
        
        if reports:
            col_load1, col_load2 = st.columns([3, 1])
            with col_load1:
                selected_report_id = st.selectbox("Select report to edit", [r.report_id for r in reports], key="edit_select")
            with col_load2:
                if st.button("📂 Load Report", key="load_btn"):
                    selected_report = next((r for r in reports if r.report_id == selected_report_id), None)
                    if selected_report:
                        st.session_state.edit_mode_report = selected_report
                        st.success("✓ Report loaded! Edit the fields below.")
            
            # If a report is loaded for editing, show all form fields
            if st.session_state.edit_mode_report:
                loaded_report = st.session_state.edit_mode_report
                report_json = loaded_report.data or {}
                
                st.markdown("---")
                st.markdown(f"### Editing: {loaded_report.report_id}")
                
                # Use tabs for organized sections
                edit_tabs = st.tabs([
                    "🎯 Subject", "⚠️ Threat", "📄 Intelligence", "🔍 Biometrics",
                    "🌐 OSINT", "📡 SIGINT", "👥 HUMINT", "💰 Financial",
                    "🔗 Connections", "📋 Recommendations", "📱 Digital Footprint", "⏰ Timeline", "📸 Incidents"
                ])
                
                # Tab 1: Subject Information
                with edit_tabs[0]:
                    st.markdown("#### 🎯 Subject Information")
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        subject_name = st.text_input("Subject Name", value=report_json.get("target", {}).get("name", ""), key="edit_subj_name")
                        alias = st.text_input("Primary Alias", value=report_json.get("target", {}).get("alias", ""), key="edit_alias")
                        dob = st.text_input("Date of Birth (YYYY-MM-DD)", value=report_json.get("target", {}).get("dob", ""), key="edit_dob")
                        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Unknown"], key="edit_gender")
                    with col_s2:
                        nationality = st.text_input("Nationality", value=report_json.get("target", {}).get("nationality", ""), key="edit_nat")
                        location = st.text_input("Last Known Location", value=report_json.get("target", {}).get("location", ""), key="edit_loc")
                        status = st.selectbox("Status", 
                            ["AT LARGE (Fugitive)", "KILLED IN ACTION", "DETAINED", "UNDER SURVEILLANCE", "MISSING", "DECEASED"],
                            index=0 if not report_json.get("target", {}).get("status") else 0,
                            key="edit_status"
                        )
                        passport_nums = st.text_area("Passport Numbers (comma-separated)", 
                            value=", ".join(report_json.get("target", {}).get("passport_numbers", [])) if isinstance(report_json.get("target", {}).get("passport_numbers"), list) else "",
                            key="edit_passport", height=60)
                
                # Tab 2: Threat Assessment
                with edit_tabs[1]:
                    st.markdown("#### ⚠️ Threat Assessment")
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        threat_level = st.selectbox("Threat Level", ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                            key="edit_threat_level", index=3 if report_json.get("target", {}).get("threat_level") == "CRITICAL" else 0)
                        threat_rating = st.slider("Threat Rating", 1, 10, value=report_json.get("target", {}).get("threat_rating", 5), key="edit_threat_rating")
                        wanted_status = st.text_input("Wanted Status", value=report_json.get("target", {}).get("wanted_status", ""), key="edit_wanted_status")
                    with col_t2:
                        arrest_warrant = st.text_input("Arrest Warrant #", value=report_json.get("target", {}).get("arrest_warrant", ""), key="edit_arrest_warrant")
                        bounty = st.text_input("Bounty Amount", value=report_json.get("target", {}).get("bounty", ""), key="edit_bounty")
                    wanted_for = st.text_area("Charges/Wanted For", value=report_json.get("target", {}).get("wanted_for", ""), key="edit_wanted_for", height=80)
                
                # Tab 3: Intelligence Summary
                with edit_tabs[2]:
                    st.markdown("#### 📄 Intelligence Assessment")
                    intelligence_summary = st.text_area("Intelligence Summary", value=report_json.get("intelligence_summary", ""), key="edit_intel_summary", height=150)
                
                # Tab 4: Biometrics
                with edit_tabs[3]:
                    st.markdown("#### 🔍 Biometrics & Physical Description")
                    col_b1, col_b2, col_b3 = st.columns(3)
                    with col_b1:
                        height = st.text_input("Height", value=report_json.get("biometrics", {}).get("height", ""), key="edit_height")
                        weight = st.text_input("Weight", value=report_json.get("biometrics", {}).get("weight", ""), key="edit_weight")
                        build = st.selectbox("Build", ["Slim", "Average", "Athletic", "Heavy", "Unknown"], key="edit_build")
                    with col_b2:
                        eye_color = st.selectbox("Eye Color", ["Brown", "Blue", "Green", "Hazel", "Black", "Gray", "Other"], key="edit_eye_color")
                        hair_color = st.selectbox("Hair Color", ["Brown", "Black", "Blonde", "Red", "Gray", "Other"], key="edit_hair_color")
                        ethnicity = st.text_input("Ethnicity", value=report_json.get("biometrics", {}).get("ethnicity", ""), key="edit_ethnicity")
                    with col_b3:
                        blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"], key="edit_blood_type")
                        known_langs = st.text_input("Known Languages (comma-separated)", 
                            value=", ".join(report_json.get("biometrics", {}).get("known_languages", [])) if isinstance(report_json.get("biometrics", {}).get("known_languages"), list) else "",
                            key="edit_langs")
                        age_apparent = st.text_input("Apparent Age", value=report_json.get("biometrics", {}).get("age_apparent", ""), key="edit_age_apparent")
                    
                    distinguishing = st.text_area("Distinguishing Features (scars, tattoos, marks)", value=report_json.get("biometrics", {}).get("scars_marks", ""), key="edit_distinguishing", height=80)
                    medical_info = st.text_area("Medical Info/Conditions", value="\n".join(report_json.get("biometrics", {}).get("medical_conditions", [])) if isinstance(report_json.get("biometrics", {}).get("medical_conditions"), list) else "", key="edit_medical", height=80)
                
                # Tab 5: OSINT
                with edit_tabs[4]:
                    st.markdown("#### 🌐 Open Source Intelligence (OSINT)")
                    col_o1, col_o2 = st.columns(2)
                    with col_o1:
                        dark_web = st.text_input("Dark Web Presence", value=report_json.get("osint", {}).get("dark_web_presence", ""), key="edit_darkweb")
                        handles = st.text_area("Known Handles/Usernames", 
                            value="\n".join(report_json.get("osint", {}).get("known_handles", [])) if isinstance(report_json.get("osint", {}).get("known_handles"), list) else "",
                            key="edit_handles", height=80)
                    with col_o2:
                        emails = st.text_area("Email Accounts",
                            value="\n".join(report_json.get("osint", {}).get("email_accounts", [])) if isinstance(report_json.get("osint", {}).get("email_accounts"), list) else "",
                            key="edit_emails", height=80)
                        crypto = st.text_area("Cryptocurrency Wallets",
                            value="\n".join(report_json.get("osint", {}).get("cryptocurrency_wallets", [])) if isinstance(report_json.get("osint", {}).get("cryptocurrency_wallets"), list) else "",
                            key="edit_crypto", height=80)
                    forums = st.text_area("Forums/Communities", 
                        value="\n".join(report_json.get("osint", {}).get("forums", [])) if isinstance(report_json.get("osint", {}).get("forums"), list) else "",
                        key="edit_forums", height=60)
                    rep_score = st.text_input("Reputation Score", value=str(report_json.get("osint", {}).get("reputation_score", "")), key="edit_rep")
                
                # Tab 6: SIGINT
                with edit_tabs[5]:
                    st.markdown("#### 📡 Signals Intelligence (SIGINT)")
                    col_si1, col_si2 = st.columns(2)
                    with col_si1:
                        phones = st.text_area("Phone Numbers",
                            value="\n".join(report_json.get("sigint", {}).get("phone_numbers", [])) if isinstance(report_json.get("sigint", {}).get("phone_numbers"), list) else "",
                            key="edit_phones", height=80)
                        last_contact = st.text_input("Last Contact Date", value=report_json.get("sigint", {}).get("last_contact", ""), key="edit_lastcon")
                    with col_si2:
                        comm_methods = st.text_area("Communication Methods",
                            value="\n".join(report_json.get("sigint", {}).get("communication_methods", [])) if isinstance(report_json.get("sigint", {}).get("communication_methods"), list) else "",
                            key="edit_commethods", height=80)
                        encryption = st.text_input("Encryption Level", value=report_json.get("sigint", {}).get("encryption_level", ""), key="edit_encrypt")
                    tech_cap = st.text_input("Technical Capability", value=report_json.get("sigint", {}).get("estimated_technical_capability", ""), key="edit_techcap")
                    comm_freq = st.text_input("Communication Frequency", value=report_json.get("sigint", {}).get("communication_frequency", ""), key="edit_commfreq")
                
                # Tab 7: HUMINT
                with edit_tabs[6]:
                    st.markdown("#### 👥 Human Intelligence (HUMINT)")
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        informant = st.text_area("Informant Reports",
                            value="\n".join(report_json.get("humint", {}).get("informant_reports", [])) if isinstance(report_json.get("humint", {}).get("informant_reports"), list) else "",
                            key="edit_informant", height=100)
                        habits = st.text_area("Habits/Patterns",
                            value="\n".join(report_json.get("humint", {}).get("habits_patterns", [])) if isinstance(report_json.get("humint", {}).get("habits_patterns"), list) else "",
                            key="edit_habits", height=100)
                    with col_h2:
                        contacts = st.text_area("Known Contacts",
                            value="\n".join(report_json.get("humint", {}).get("known_contacts", [])) if isinstance(report_json.get("humint", {}).get("known_contacts"), list) else "",
                            key="edit_contacts", height=100)
                        locations = st.text_area("Preferred Locations",
                            value="\n".join(report_json.get("humint", {}).get("preferred_locations", [])) if isinstance(report_json.get("humint", {}).get("preferred_locations"), list) else "",
                            key="edit_locations", height=100)
                    source_rel = st.text_input("Source Reliability", value=report_json.get("humint", {}).get("source_reliability", ""), key="edit_sourcerel")
                    curr_op = st.text_input("Current Operation", value=report_json.get("humint", {}).get("current_operation", ""), key="edit_currop")
                
                # Tab 8: Financial Intelligence
                with edit_tabs[7]:
                    st.markdown("#### 💰 Financial Intelligence")
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        bank_accounts = st.text_area("Known Bank Accounts",
                            value="\n".join(report_json.get("financial_intelligence", {}).get("known_bank_accounts", [])) if isinstance(report_json.get("financial_intelligence", {}).get("known_bank_accounts"), list) else "",
                            key="edit_bank", height=80)
                        crypto_holdings = st.text_area("Cryptocurrency Holdings",
                            value="\n".join(report_json.get("financial_intelligence", {}).get("cryptocurrency_holdings", [])) if isinstance(report_json.get("financial_intelligence", {}).get("cryptocurrency_holdings"), list) else "",
                            key="edit_cryptoholding", height=80)
                    with col_f2:
                        properties = st.text_area("Property Ownership",
                            value="\n".join(report_json.get("financial_intelligence", {}).get("property_ownership", [])) if isinstance(report_json.get("financial_intelligence", {}).get("property_ownership"), list) else "",
                            key="edit_properties", height=80)
                        income = st.text_input("Estimated Annual Income", value=report_json.get("financial_intelligence", {}).get("estimated_annual_income", ""), key="edit_income")
                    trans_patterns = st.text_area("Transaction Patterns", value=report_json.get("financial_intelligence", {}).get("transaction_patterns", ""), key="edit_trans", height=60)
                
                # Tab 9: Connections
                with edit_tabs[8]:
                    st.markdown("#### 🔗 Connections & Network")
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        associates = st.text_area("Criminal Associates",
                            value="\n".join(report_json.get("connections", {}).get("criminal_associates", [])) if isinstance(report_json.get("connections", {}).get("criminal_associates"), list) else "",
                            key="edit_associates", height=100)
                        safe_houses = st.text_area("Known Safe Houses",
                            value="\n".join(report_json.get("connections", {}).get("known_safe_houses", [])) if isinstance(report_json.get("connections", {}).get("known_safe_houses"), list) else "",
                            key="edit_safehouses", height=100)
                    with col_c2:
                        intl_reach = st.text_input("International Reach", value=report_json.get("connections", {}).get("international_reach", ""), key="edit_intlreach")
                        border_patterns = st.text_area("Border Crossing Patterns",
                            value="\n".join(report_json.get("connections", {}).get("border_crossing_patterns", [])) if isinstance(report_json.get("connections", {}).get("border_crossing_patterns"), list) else "",
                            key="edit_border", height=100)
                    handlers = st.text_area("Handlers/Controllers",
                            value="\n".join(report_json.get("connections", {}).get("handlers", [])) if isinstance(report_json.get("connections", {}).get("handlers"), list) else "",
                            key="edit_handlers", height=100)
                
                # Tab 10: Recommendations
                with edit_tabs[9]:
                    st.markdown("#### 📋 Recommendations & Actions")
                    col_r1, col_r2 = st.columns(2)
                    with col_r1:
                        immediate_actions = st.text_area("Immediate Actions", 
                            value="\n".join(report_json.get("recommendations", {}).get("immediate_actions", [])) if report_json.get("recommendations") else "",
                            key="edit_immediate_actions", height=100)
                    with col_r2:
                        ongoing_operations = st.text_area("Ongoing Operations",
                            value="\n".join(report_json.get("recommendations", {}).get("ongoing_operations", [])) if report_json.get("recommendations") else "",
                            key="edit_ongoing_operations", height=100)
                
                # Tab 10: Digital Footprint
                with edit_tabs[10]:
                    st.markdown("#### 📱 Detailed Digital Footprint Analysis")
                    digital_footprint = report_json.get("digital_footprint", [])
                    
                    # Initialize session state for digital footprint editing
                    if "df_edit_data" not in st.session_state:
                        st.session_state.df_edit_data = [dict(row) for row in digital_footprint] if digital_footprint else []
                    
                    # Create editable dataframe
                    st.write("**Platform Activity & Digital Presence**")
                    col_df1, col_df2 = st.columns([4, 1])
                    
                    with col_df1:
                        df_display = pd.DataFrame(st.session_state.df_edit_data) if st.session_state.df_edit_data else pd.DataFrame(columns=["Platform", "Username", "Activity_Level", "Risk_Level"])
                        edited_df = st.data_editor(df_display, use_container_width=True, key="digital_footprint_editor",
                            num_rows="dynamic", column_config={
                                "Platform": st.column_config.TextColumn("Platform"),
                                "Username": st.column_config.TextColumn("Username/Handle"),
                                "Activity_Level": st.column_config.SelectboxColumn("Activity Level", options=["Low", "Medium", "High", "Very High"]),
                                "Risk_Level": st.column_config.SelectboxColumn("Risk Level", options=["Low", "Medium", "High", "Critical"])
                            })
                        
                        # Update session state with edited data
                        st.session_state.df_edit_data = edited_df.to_dict('records') if not edited_df.empty else []
                    
                    with col_df2:
                        st.write("")
                        if st.button("📥 Add Row", key="add_df_row"):
                            st.session_state.df_edit_data.append({"Platform": "", "Username": "", "Activity_Level": "Low", "Risk_Level": "Low"})
                            st.rerun()
                
                # Tab 11: Timeline
                with edit_tabs[11]:
                    st.markdown("#### ⏰ Timeline of Events")
                    timeline_data = report_json.get("timeline", [])
                    
                    # Initialize session state for timeline editing
                    if "timeline_edit_data" not in st.session_state:
                        st.session_state.timeline_edit_data = [dict(row) for row in timeline_data] if timeline_data else []
                    
                    st.write(f"**{len(st.session_state.timeline_edit_data)} events**")
                    
                    # Create editable dataframe for timeline
                    if st.session_state.timeline_edit_data:
                        timeline_df = pd.DataFrame(st.session_state.timeline_edit_data)
                        edited_timeline = st.data_editor(timeline_df, use_container_width=True, key="timeline_editor",
                            num_rows="dynamic", column_config={
                                "Date": st.column_config.TextColumn("Date"),
                                "Event_Description": st.column_config.TextColumn("Event Description"),
                                "Source": st.column_config.TextColumn("Source"),
                                "Confidence": st.column_config.SelectboxColumn("Confidence", options=["Low", "Medium", "High", "Critical"])
                            })
                        st.session_state.timeline_edit_data = edited_timeline.to_dict('records') if not edited_timeline.empty else []
                    else:
                        st.info("No timeline events. Use the button below to add events.")
                        st.session_state.timeline_edit_data = []
                    
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        if st.button("➕ Add Timeline Event", key="add_timeline_event"):
                            st.session_state.timeline_edit_data.append({
                                "Date": "", 
                                "Event_Description": "", 
                                "Source": "", 
                                "Confidence": "Medium"
                            })
                            st.rerun()
                
                # Tab 12: Incidents
                with edit_tabs[12]:
                    st.markdown("#### 📸 Incidents & Events")
                    incidents_data = report_json.get("incidents", [])
                    
                    # Initialize session state for incidents editing
                    if "incidents_edit_data" not in st.session_state:
                        st.session_state.incidents_edit_data = incidents_data.copy() if incidents_data else []
                    
                    st.write(f"**{len(st.session_state.incidents_edit_data)} incidents**")
                    
                    # Create text area for each incident with delete capability
                    for i, incident in enumerate(st.session_state.incidents_edit_data):
                        col_i1, col_i2 = st.columns([20, 1])
                        with col_i1:
                            st.session_state.incidents_edit_data[i] = st.text_area(
                                f"Incident #{i+1}",
                                value=incident if isinstance(incident, str) else str(incident),
                                key=f"incident_edit_{i}",
                                height=80
                            )
                        with col_i2:
                            if st.button("🗑️", key=f"delete_incident_{i}"):
                                st.session_state.incidents_edit_data.pop(i)
                                st.rerun()
                    
                    if st.button("➕ Add Incident", key="add_incident"):
                        st.session_state.incidents_edit_data.append("")
                        st.rerun()
                
                # Save Changes
                st.markdown("---")
                col_save1, col_save2 = st.columns(2)
                with col_save1:
                    if st.button("💾 Save All Changes", key="save_edit"):
                        # Prepare updated report data
                        updated_data = report_json.copy()
                        
                        # Update target information
                        updated_data["target"] = {
                            "name": subject_name,
                            "legal_name": subject_name,
                            "alias": alias,
                            "status": status,
                            "threat_level": threat_level,
                            "threat_rating": threat_rating,
                            "dob": dob,
                            "gender": gender,
                            "age": datetime.datetime.now().year - int(dob.split('-')[0]) if dob and dob.split('-')[0].isdigit() else 0,
                            "nationality": nationality,
                            "location": location,
                            "wanted_status": wanted_status,
                            "arrest_warrant": arrest_warrant,
                            "bounty": bounty,
                            "wanted_for": wanted_for,
                            "passport_numbers": [p.strip() for p in passport_nums.split(',') if p.strip()] if passport_nums else [],
                            **updated_data.get("target", {})
                        }
                        
                        # Update biometrics
                        updated_data["biometrics"] = {
                            "height": height,
                            "weight": weight,
                            "build": build,
                            "eye_color": eye_color,
                            "hair_color": hair_color,
                            "ethnicity": ethnicity,
                            "scars_marks": distinguishing,
                            "blood_type": blood_type,
                            "known_languages": [l.strip() for l in known_langs.split(',') if l.strip()] if known_langs else [],
                            "age_apparent": age_apparent,
                            "medical_conditions": [m.strip() for m in medical_info.split('\n') if m.strip()] if medical_info else [],
                            **updated_data.get("biometrics", {})
                        }
                        
                        # Update OSINT
                        updated_data["osint"] = {
                            "dark_web_presence": dark_web,
                            "known_handles": [h.strip() for h in handles.split('\n') if h.strip()] if handles else [],
                            "email_accounts": [e.strip() for e in emails.split('\n') if e.strip()] if emails else [],
                            "cryptocurrency_wallets": [c.strip() for c in crypto.split('\n') if c.strip()] if crypto else [],
                            "forums": [f.strip() for f in forums.split('\n') if f.strip()] if forums else [],
                            "reputation_score": rep_score,
                            **updated_data.get("osint", {})
                        }
                        
                        # Update SIGINT
                        updated_data["sigint"] = {
                            "phone_numbers": [p.strip() for p in phones.split('\n') if p.strip()] if phones else [],
                            "last_contact": last_contact,
                            "communication_methods": [c.strip() for c in comm_methods.split('\n') if c.strip()] if comm_methods else [],
                            "encryption_level": encryption,
                            "estimated_technical_capability": tech_cap,
                            "communication_frequency": comm_freq,
                            **updated_data.get("sigint", {})
                        }
                        
                        # Update HUMINT
                        updated_data["humint"] = {
                            "informant_reports": [r.strip() for r in informant.split('\n') if r.strip()] if informant else [],
                            "source_reliability": source_rel,
                            "habits_patterns": [h.strip() for h in habits.split('\n') if h.strip()] if habits else [],
                            "known_contacts": [c.strip() for c in contacts.split('\n') if c.strip()] if contacts else [],
                            "preferred_locations": [l.strip() for l in locations.split('\n') if l.strip()] if locations else [],
                            "current_operation": curr_op,
                            **updated_data.get("humint", {})
                        }
                        
                        # Update Financial Intelligence
                        updated_data["financial_intelligence"] = {
                            "known_bank_accounts": [b.strip() for b in bank_accounts.split('\n') if b.strip()] if bank_accounts else [],
                            "cryptocurrency_holdings": [c.strip() for c in crypto_holdings.split('\n') if c.strip()] if crypto_holdings else [],
                            "property_ownership": [p.strip() for p in properties.split('\n') if p.strip()] if properties else [],
                            "transaction_patterns": trans_patterns,
                            "estimated_annual_income": income,
                            **updated_data.get("financial_intelligence", {})
                        }
                        
                        # Update Connections
                        updated_data["connections"] = {
                            "criminal_associates": [a.strip() for a in associates.split('\n') if a.strip()] if associates else [],
                            "international_reach": intl_reach,
                            "known_safe_houses": [s.strip() for s in safe_houses.split('\n') if s.strip()] if safe_houses else [],
                            "border_crossing_patterns": [b.strip() for b in border_patterns.split('\n') if b.strip()] if border_patterns else [],
                            "handlers": [h.strip() for h in handlers.split('\n') if h.strip()] if handlers else [],
                            **updated_data.get("connections", {})
                        }
                        
                        # Update intelligence and recommendations
                        updated_data["intelligence_summary"] = intelligence_summary
                        updated_data["recommendations"] = {
                            "immediate_actions": [a.strip() for a in immediate_actions.split('\n') if a.strip()],
                            "ongoing_operations": [o.strip() for o in ongoing_operations.split('\n') if o.strip()]
                        }
                        
                        # Update Digital Footprint (from session state)
                        if "df_edit_data" in st.session_state:
                            updated_data["digital_footprint"] = [
                                {k: (v if v and v != "" else None) for k, v in row.items()}
                                for row in st.session_state.df_edit_data
                                if any(row.values())  # Only keep non-empty rows
                            ]
                        
                        # Update Timeline (from session state)
                        if "timeline_edit_data" in st.session_state:
                            updated_data["timeline"] = [
                                {k: (v if v and v != "" else None) for k, v in row.items()}
                                for row in st.session_state.timeline_edit_data
                                if any(row.values())  # Only keep non-empty rows
                            ]
                        
                        # Update Incidents (from session state)
                        if "incidents_edit_data" in st.session_state:
                            updated_data["incidents"] = [
                                inc.strip() for inc in st.session_state.incidents_edit_data
                                if inc and inc.strip()  # Only keep non-empty incidents
                            ]
                        
                        try:
                            # Update in database
                            db.update_report(loaded_report.report_id, data=updated_data)
                            st.success("✅ Report updated successfully!")
                            st.session_state.edit_mode_report = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error saving report: {e}")
                
                with col_save2:
                    if st.button("❌ Cancel Edit", key="cancel_edit"):
                        st.session_state.edit_mode_report = None
                        st.rerun()
        else:
            st.info("📭 No reports available to edit")
    
    # ========== TAB: DELETE REPORT ==========
    with tab_delete:
        st.subheader("🗑️ Delete Report")
        st.warning("⚠️ This action cannot be undone! Use with caution.")
        
        reports = db.list_reports(limit=100)
        
        if reports:
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                delete_report_id = st.selectbox("Select report to delete", [r.report_id for r in reports], key="delete_select")
            with col_del2:
                delete_confirmed = st.checkbox("I confirm deletion", key="delete_confirm")
            
            if delete_confirmed:
                st.error("🚨 Report will be permanently deleted from the database!")
                col_del_btn1, col_del_btn2 = st.columns(2)
                
                with col_del_btn1:
                    if st.button("🗑️ DELETE PERMANENTLY", key="delete_btn", type="secondary"):
                        try:
                            db.delete_report(delete_report_id)
                            st.success(f"✅ Report '{delete_report_id}' has been permanently deleted!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"❌ Error deleting report: {e}")
                
                with col_del_btn2:
                    if st.button("Cancel", key="cancel_delete"):
                        pass
        else:
            st.info("📭 No reports to delete")
    
    # ========== SEARCH REPORTS WITHIN TAB 2 ==========
    st.markdown("---")
    st.subheader("🔍 Search Reports")
    
    search_query = st.text_input(
        "Search by subject name, title, or content",
        placeholder="Enter search term...",
        key="manage_search_input"
    )
    
    if search_query:
        search_results = db.search_reports(search_query, limit=25)
        
        if search_results:
            st.success(f"✅ Found {len(search_results)} matching reports")
            
            search_cols = st.columns(5)
            search_options = [r.report_id for r in search_results]
            selected_search_id = st.selectbox(
                "View search result details",
                search_options,
                key="search_result_select"
            )
            
            if selected_search_id:
                selected_result = next((r for r in search_results if r.report_id == selected_search_id), None)
                if selected_result:
                    with st.container(border=True):
                        col_r1, col_r2, col_r3 = st.columns(3)
                        with col_r1:
                            st.markdown(f"**Report ID:** {selected_result.report_id}")
                            st.markdown(f"**Subject:** {selected_result.target_name}")
                            st.markdown(f"**Alias:** {selected_result.target_alias or 'N/A'}")
                        with col_r2:
                            st.markdown(f"**Classification:** {selected_result.classification}")
                            st.markdown(f"**Author:** {selected_result.author}")
                            st.markdown(f"**TLP Level:** {selected_result.tlp_level}")
                        with col_r3:
                            st.markdown(f"**Created:** {selected_result.created_at.strftime('%Y-%m-%d %H:%M') if selected_result.created_at else 'N/A'}")
                            st.markdown(f"**Version:** {selected_result.version}")
                            st.markdown(f"**Status:** {selected_result.status or 'Active'}")
        else:
            st.info("❌ No results found for your search")


# ============================================================================
# TAB 3: ANALYTICS (ENHANCED)
# ============================================================================

with tab3:
    st.header("🕵️ CENTRAL INTELLIGENCE ANALYTICS COMMAND CENTER")
    
    # Get statistics from database
    stats = db.get_statistics()
    reports = db.list_reports(limit=1000)
    
    if stats and reports:
        # ===== EXECUTIVE SUMMARY DASHBOARD =====
        st.markdown("### 🎯 EXECUTIVE INTELLIGENCE SUMMARY")
        
        exec_col1, exec_col2, exec_col3, exec_col4, exec_col5 = st.columns(5)
        
        with exec_col1:
            st.metric(
                "🕵️ TOTAL ASSETS",
                stats.get("total_reports", 0),
                help="Total intelligence entities tracked"
            )
        with exec_col2:
            active_count = stats.get("active_reports", 0)
            st.metric(
                "🔴 HIGH PRIORITY",
                len([r for r in reports if r.data and r.data.get("target", {}).get("threat_level") == "CRITICAL"]),
                f"+{len([r for r in reports if r.data and r.data.get('target', {}).get('threat_level') == 'CRITICAL'])}",
                help="Critical threat entities requiring immediate attention"
            )
        with exec_col3:
            st.metric(
                "⚠️ THREAT SCORE",
                f"{sum([r.data.get('target', {}).get('threat_rating', 5) for r in reports if r.data]) / len(reports):.1f}/10" if reports else "0/10",
                help="System-wide average threat assessment"
            )
        with exec_col4:
            security_compliant = (stats.get("encrypted_reports", 0) / len(reports)) * 100 if reports else 0
            st.metric(
                "🔒 COMPLIANCE",
                f"{security_compliant:.0f}%",
                help="Encryption/security compliance rate"
            )
        with exec_col5:
            st.metric(
                "📊 INTEL VELOCITY",
                len([r for r in reports if r.version > 1]),
                help="Reports updated in current cycle"
            )
        
        st.markdown("---")
        
        # ===== THREAT INTELLIGENCE HEATMAP =====
        st.markdown("### 🔥 THREAT INTELLIGENCE MATRIX")
        
        threat_matrix_col1, threat_matrix_col2 = st.columns([2, 1])
        
        with threat_matrix_col1:
            # Create threat matrix: threat level vs classification
            threat_data = {}
            for report in reports:
                threat = report.data.get("target", {}).get("threat_level", "UNKNOWN") if report.data else "UNKNOWN"
                classif = report.classification or "UNCLASSIFIED"
                key = f"{threat} | {classif}"
                threat_data[key] = threat_data.get(key, 0) + 1
            
            if threat_data:
                threat_df = pd.DataFrame(list(threat_data.items()), columns=["Classification Level", "Count"])
                threat_df = threat_df.sort_values("Count", ascending=False)
                st.bar_chart(threat_df.set_index("Classification Level"), use_container_width=True)
        
        with threat_matrix_col2:
            st.markdown("**Threat Assessment**")
            critical_count = len([r for r in reports if r.data and r.data.get("target", {}).get("threat_level") == "CRITICAL"])
            high_count = len([r for r in reports if r.data and r.data.get("target", {}).get("threat_level") == "HIGH"])
            medium_count = len([r for r in reports if r.data and r.data.get("target", {}).get("threat_level") == "MEDIUM"])
            
            color_critical = "🔴" if critical_count > 0 else "⚪"
            color_high = "🟠" if high_count > 0 else "⚪"
            color_medium = "🟡" if medium_count > 0 else "⚪"
            
            st.write(f"{color_critical} Critical: {critical_count}")
            st.write(f"{color_high} High: {high_count}")
            st.write(f"{color_medium} Medium: {medium_count}")
        
        st.markdown("---")
        
        # ===== OPERATIONAL INTELLIGENCE CENTER =====
        st.markdown("### 🎖️ OPERATIONAL INTELLIGENCE CENTER")
        
        op_col1, op_col2, op_col3 = st.columns(3)
        
        with op_col1:
            st.markdown("**📍 ENTITY STATUS INTELLIGENCE**")
            status_stats = {}
            for report in reports:
                status = report.status or "Unknown"
                status_stats[status] = status_stats.get(status, 0) + 1
            
            status_df = pd.DataFrame(list(status_stats.items()), columns=["Status", "Count"])
            status_df = status_df.sort_values("Count", ascending=False)
            st.bar_chart(status_df.set_index("Status"), use_container_width=True)
        
        with op_col2:
            st.markdown("**🎓 CLASSIFICATION MATRIX**")
            classif_stats = stats.get("by_classification", {})
            if classif_stats:
                classif_df = pd.DataFrame(list(classif_stats.items()), columns=["Classification", "Count"])
                classif_df = classif_df.sort_values("Count", ascending=False)
                st.bar_chart(classif_df.set_index("Classification"), use_container_width=True)
        
        with op_col3:
            st.markdown("**🏢 AGENCY WORKLOAD DISTRIBUTION**")
            author_stats = {}
            for report in reports:
                author = report.author or "Unknown"
                author_stats[author] = author_stats.get(author, 0) + 1
            
            author_df = pd.DataFrame(list(author_stats.items()), columns=["Agency", "Reports"])
            author_df = author_df.sort_values("Reports", ascending=False).head(8)
            st.bar_chart(author_df.set_index("Agency"), use_container_width=True)
        
        st.markdown("---")
        
        # ===== COUNTERINTELLIGENCE METRICS =====
        st.markdown("### 🛡️ COUNTERINTELLIGENCE & SECURITY METRICS")
        
        ci_col1, ci_col2, ci_col3, ci_col4 = st.columns(4)
        
        with ci_col1:
            redacted_count = len([r for r in reports if r.redaction_count > 0])
            redaction_pct = (redacted_count / len(reports)) * 100 if reports else 0
            st.metric(
                "🔐 REDACTION RATE",
                f"{redaction_pct:.1f}%",
                f"{redacted_count} entities",
                help="Sensitive information redaction compliance"
            )
        
        with ci_col2:
            encryption_pct = (stats.get("encrypted_reports", 0) / len(reports)) * 100 if reports else 0
            st.metric(
                "🔒 ENCRYPTION RATE",
                f"{encryption_pct:.1f}%",
                f"{stats.get('encrypted_reports', 0)} reports",
                help="End-to-end encryption implementation"
            )
        
        with ci_col3:
            avg_redactions = sum([r.redaction_count for r in reports]) / len(reports) if reports else 0
            st.metric(
                "📝 AVG REDACTIONS",
                f"{avg_redactions:.1f}",
                help="Average sensitive items redacted per report"
            )
        
        with ci_col4:
            tlp_distribution = {}
            for report in reports:
                tlp = report.tlp_level or "WHITE"
                tlp_distribution[tlp] = tlp_distribution.get(tlp, 0) + 1
            
            max_tlp = max(tlp_distribution.values()) if tlp_distribution else 0
            st.metric(
                "🚨 TLP CLASSIFICATION",
                max(tlp_distribution.keys()) if tlp_distribution else "NONE",
                help="Highest Traffic Light Protocol level in use"
            )
        
        st.markdown("---")
        
        # ===== INTELLIGENCE COLLECTION TIMELINE =====
        st.markdown("### 📅 INTELLIGENCE COLLECTION TIMELINE")
        
        date_stats = {}
        for report in reports:
            if report.created_at:
                date_key = report.created_at.strftime("%Y-%m-%d")
                date_stats[date_key] = date_stats.get(date_key, 0) + 1
        
        if date_stats:
            date_df = pd.DataFrame(list(date_stats.items()), columns=["Date", "Reports"])
            date_df["Date"] = pd.to_datetime(date_df["Date"])
            date_df = date_df.sort_values("Date")
            
            timeline_col1, timeline_col2 = st.columns([3, 1])
            with timeline_col1:
                st.line_chart(date_df.set_index("Date"), use_container_width=True)
            with timeline_col2:
                st.markdown("**Collection Velocity**")
                total_days = (date_df["Date"].max() - date_df["Date"].min()).days if len(date_df) > 1 else 1
                velocity = len(reports) / max(total_days, 1)
                st.write(f"📊 {velocity:.2f} reports/day")
        
        st.markdown("---")
        
        # ===== THREAT ACTOR NETWORK ANALYSIS =====
        st.markdown("### 🌐 THREAT ACTOR NETWORK ANALYSIS")
        
        network_col1, network_col2 = st.columns(2)
        
        with network_col1:
            st.markdown("**Top Tracked Entities by Threat Rating**")
            threat_ratings = []
            for report in reports:
                if report.data:
                    target_name = report.target_name or report.target_alias or "Unknown"
                    threat_rating = report.data.get("target", {}).get("threat_rating", 5)
                    threat_ratings.append((target_name, threat_rating))
            
            threat_ratings.sort(key=lambda x: x[1], reverse=True)
            top_threats = threat_ratings[:15]
            
            if top_threats:
                threat_df = pd.DataFrame(top_threats, columns=["Entity", "Threat Rating"])
                st.bar_chart(threat_df.set_index("Entity"), use_container_width=True)
        
        with network_col2:
            st.markdown("**Intelligence Gap Analysis**")
            gap_data = {
                "Complete Profile": len([r for r in reports if r.version > 2]),
                "Partial Profile": len([r for r in reports if r.version == 1 or r.version == 2]),
                "Minimal Data": len([r for r in reports if r.redaction_count > 5])
            }
            gap_df = pd.DataFrame(list(gap_data.items()), columns=["Profile Status", "Count"])
            st.bar_chart(gap_df.set_index("Profile Status"), use_container_width=True)
        
        st.markdown("---")
        
        # ===== ADVANCED INTELLIGENCE ANALYTICS =====
        st.markdown("### 🔬 ADVANCED INTELLIGENCE ANALYTICS")
        
        analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs([
            "🎯 Correlation Analysis",
            "📈 Trend Forecasting",
            "⚖️ Risk Assessment Matrix"
        ])
        
        with analytics_tab1:
            st.markdown("**Entity Correlation Matrix**")
            
            # Correlate by classification and threat level
            correlation_data = {}
            for report in reports:
                classif = report.classification
                threat = report.data.get("target", {}).get("threat_level", "UNKNOWN") if report.data else "UNKNOWN"
                key = f"{classif} → {threat}"
                correlation_data[key] = correlation_data.get(key, 0) + 1
            
            if correlation_data:
                corr_df = pd.DataFrame(list(correlation_data.items()), columns=["Correlation", "Count"])
                corr_df = corr_df.sort_values("Count", ascending=False).head(10)
                st.bar_chart(corr_df.set_index("Correlation"), use_container_width=True)
                
                st.markdown("**Key Correlations:**")
                for idx, row in corr_df.head(5).iterrows():
                    st.write(f"• {row['Correlation']}: {row['Count']} entities")
        
        with analytics_tab2:
            st.markdown("**Intelligence Collection Trends**")
            
            if len(date_df) > 1:
                # Calculate trend
                recent_reports = len([r for r in reports if r.created_at and (datetime.datetime.now() - r.created_at).days < 30])
                older_reports = len([r for r in reports if r.created_at and (datetime.datetime.now() - r.created_at).days >= 30])
                
                trend_pct = ((recent_reports - older_reports) / max(older_reports, 1)) * 100
                trend_direction = "📈 INCREASING" if trend_pct > 0 else "📉 DECREASING"
                
                st.metric("Collection Trend", trend_direction, f"{abs(trend_pct):.1f}%")
                
                # Weekly breakdown
                st.markdown("**Weekly Activity**")
                weekly_data = {}
                for report in reports:
                    if report.created_at:
                        week_key = report.created_at.strftime("%Y-W%V")
                        weekly_data[week_key] = weekly_data.get(week_key, 0) + 1
                
                if weekly_data:
                    weekly_df = pd.DataFrame(list(weekly_data.items()), columns=["Week", "Count"])
                    st.bar_chart(weekly_df.set_index("Week"), use_container_width=True)
        
        with analytics_tab3:
            st.markdown("**Comprehensive Risk Assessment Matrix**")
            
            risk_matrix = {}
            for report in reports:
                threat = report.data.get("target", {}).get("threat_level", "UNKNOWN") if report.data else "UNKNOWN"
                status = report.status or "Unknown"
                key = f"{threat} ({status})"
                risk_matrix[key] = risk_matrix.get(key, 0) + 1
            
            if risk_matrix:
                risk_df = pd.DataFrame(list(risk_matrix.items()), columns=["Risk Category", "Count"])
                risk_df = risk_df.sort_values("Count", ascending=False)
                st.bar_chart(risk_df.set_index("Risk Category"), use_container_width=True)
                
                # Risk score calculation
                risk_score = 0
                critical_weight = 10
                high_weight = 7
                medium_weight = 4
                
                for report in reports:
                    threat = report.data.get("target", {}).get("threat_level", "UNKNOWN") if report.data else "UNKNOWN"
                    if threat == "CRITICAL":
                        risk_score += critical_weight
                    elif threat == "HIGH":
                        risk_score += high_weight
                    elif threat == "MEDIUM":
                        risk_score += medium_weight
                
                avg_risk_score = risk_score / len(reports) if reports else 0
                
                col_risk1, col_risk2, col_risk3 = st.columns(3)
                with col_risk1:
                    st.metric("Overall Risk Score", f"{avg_risk_score:.1f}/10")
                with col_risk2:
                    risk_level = "🔴 CRITICAL" if avg_risk_score >= 7 else "🟠 HIGH" if avg_risk_score >= 5 else "🟡 MEDIUM" if avg_risk_score >= 3 else "🟢 LOW"
                    st.metric("Risk Level", risk_level)
                with col_risk3:
                    entities_at_risk = len([r for r in reports if r.data and r.data.get("target", {}).get("threat_level") in ["CRITICAL", "HIGH"]])
                    st.metric("Entities at Risk", entities_at_risk)
        
        st.markdown("---")
        
        # ===== INTELLIGENCE SUMMARY & RECOMMENDATIONS =====
        st.markdown("### 📋 EXECUTIVE INTELLIGENCE BRIEFING")
        
        briefing_col1, briefing_col2 = st.columns(2)
        
        with briefing_col1:
            st.markdown("**Key Findings**")
            findings = [
                f"📊 Total tracked entities: {len(reports)}",
                f"🔴 Critical threats: {len([r for r in reports if r.data and r.data.get('target', {}).get('threat_level') == 'CRITICAL'])}",
                f"🔐 Compliance rate: {(stats.get('encrypted_reports', 0) / len(reports) * 100):.1f}%",
                f"📈 Average entity update rate: {(len([r for r in reports if r.version > 1]) / len(reports) * 100):.1f}%",
                f"🌐 Most common classification: {max(stats.get('by_classification', {}).items(), key=lambda x: x[1])[0] if stats.get('by_classification') else 'N/A'}"
            ]
            
            for finding in findings:
                st.write(finding)
        
        with briefing_col2:
            st.markdown("**Recommended Actions**")
            actions = []
            
            if len([r for r in reports if r.data and r.data.get("target", {}).get("threat_level") == "CRITICAL"]) > 3:
                actions.append("⚠️ Escalate critical threat review to command staff")
            
            if (stats.get("encrypted_reports", 0) / len(reports)) < 0.8:
                actions.append("🔒 Implement encryption on non-compliant reports")
            
            if avg_risk_score >= 7:
                actions.append("🚨 Activate divine monitoring protocols")
            
            if len([r for r in reports if r.version == 1]) > len(reports) * 0.5:
                actions.append("📝 Schedule intelligence refresh cycle")
            
            if not actions:
                actions.append("✅ System operational within normal parameters")
            
            for i, action in enumerate(actions, 1):
                st.write(f"{i}. {action}")



# ============================================================================
# TAB 4: SETTINGS
# ============================================================================

with tab4:
    st.header("Platform Settings")

    st.markdown("### 🔐 Security Settings")
    # We'll use a form so Save is atomic; persist settings to JSON and audit-log the change
    settings_file = Path("config_settings.json")

    def load_settings() -> dict:
        """Load settings from JSON if exists, otherwise from config instance."""
        try:
            if settings_file.exists():
                with open(settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        # Fallback to current config
        return {
            "RAVEN_PDF_ENCRYPT": config.security.enable_pdf_encryption,
            "RAVEN_PDF_PASSWORD": config.security.pdf_password_default,
            "RAVEN_EXIF_STRIP": config.security.enable_exif_stripping,
            "RAVEN_AUDIT_LOGGING": config.security.enable_audit_logging,
        }

    def save_settings_json(values: dict) -> bool:
        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(values, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Failed to save settings: {e}")
            return False

    # Load current values (prefer JSON file if present)
    current_settings = load_settings()

    with st.form("settings_form"):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            enable_pdf_encryption = st.checkbox(
                "Enable PDF Encryption",
                value=current_settings.get("RAVEN_PDF_ENCRYPT", False),
                key="ui_enable_pdf_encryption_form",
            )
            default_pdf_password = st.text_input(
                "Default PDF Password",
                value=current_settings.get("RAVEN_PDF_PASSWORD", ""),
                key="ui_pdf_password_form",
                type="password",
            )
        with col_s2:
            strip_exif = st.checkbox(
                "Strip EXIF Data from Images",
                value=current_settings.get("RAVEN_EXIF_STRIP", True),
                key="ui_strip_exif_form",
            )
            enable_audit_logging = st.checkbox(
                "Enable Audit Logging",
                value=current_settings.get("RAVEN_AUDIT_LOGGING", True),
                key="ui_audit_logging_form",
            )

        submitted = st.form_submit_button("Save Settings")
        cancelled = st.form_submit_button("Cancel Settings")

        if cancelled:
            st.success("Cancelled. No changes applied.")
            st.rerun()

        if submitted:
            # Validate
            errors = []
            if enable_pdf_encryption:
                pwd = default_pdf_password or ""
                if not isinstance(pwd, str) or not pwd.strip():
                    errors.append(
                        "PDF encryption is enabled but the default PDF password is empty."
                    )
                elif len(pwd.strip()) < 6:
                    errors.append(
                        "Default PDF password must be at least 6 characters long."
                    )
            if errors:
                for e in errors:
                    st.error(e)
                st.warning("Fix validation errors before saving.")
            else:
                new_values = {
                    "RAVEN_PDF_ENCRYPT": bool(enable_pdf_encryption),
                    "RAVEN_PDF_PASSWORD": default_pdf_password,
                    "RAVEN_EXIF_STRIP": bool(strip_exif),
                    "RAVEN_AUDIT_LOGGING": bool(enable_audit_logging),
                }
                ok = save_settings_json(new_values)
                if ok:
                    # Update in-memory config
                    config.security.enable_pdf_encryption = bool(enable_pdf_encryption)
                    config.security.pdf_password_default = default_pdf_password
                    config.security.enable_exif_stripping = bool(strip_exif)
                    config.security.enable_audit_logging = bool(enable_audit_logging)

                    # Audit log the change
                    try:
                        db.log_audit_event(
                            event_type="SETTINGS_CHANGE",
                            action="SAVE",
                            user=config.security.pdf_password_default
                            if config.security.pdf_password_default
                            else config.logging.log_file,
                            report_id=None,
                            details=new_values,
                        )
                    except Exception:
                        # Don't block saving if audit logging fails
                        pass

                    st.success(
                        "✓ Settings saved. Changes applied in memory; restart app to ensure all modules reload."
                    )
                    # Rerun to recreate widgets with updated values
                    st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Configuration Info")

    config_info = {
        "Default Template": config.templates.default_template,
        "Log Level": config.logging.log_level,
        "Database Type": config.database.db_type,
        "PDF DPI": config.pdf.dpi,
        "Watermark Enabled": config.pdf.enable_watermark,
    }

    for key, value in config_info.items():
        st.text_input(key, value=str(value), disabled=True)

    st.markdown("---")
    st.markdown("### 📖 About")
    st.info(
        """
        **Anubis Intelligence Platform v4.0**

        Advanced classified report generator with:
        - Real-time validation
        - Image EXIF stripping
        - PDF encryption
        - Database persistence
        - Audit logging
        - Multi-template support
        - Batch processing

        **Status**: Production Ready ✅
        """
    )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption(
    "⚱️ Anubis Intelligence Platform v4.0 | Authorized Personnel Only | Classification: COMPANY CONFIDENTIAL"
)
