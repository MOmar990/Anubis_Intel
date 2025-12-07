# ⚱️ Anubis Intelligence Platform

<div align="center">

### *Guardian of Secrets, Keeper of Intelligence*

**Enterprise-grade intelligence dossier system with IC-standard formatting**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.51.0-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*"From Packets to Process, Truth Leaves a Trace"*

</div>

---

## 📜 The Legend

In ancient Egypt, **Anubis** stood as the guardian of secrets and judge of souls - weighing hearts against the feather of truth. This platform embodies that sacred duty in the digital realm, serving as the guardian and judge of intelligence, separating truth from deception with the precision of ancient wisdom.

**Anubis Intelligence Platform** is a comprehensive intelligence report generation and management system designed for security researchers, digital forensic analysts, and intelligence professionals. The platform generates professional-grade dossiers with Intelligence Community (IC) standard formatting, complete with classification markings, biometric data integration, and advanced analytics capabilities.

---

---

## 👁️ Visual Intelligence (Interface)

<div align="center">

### 🛡️ Mission Control (Dashboard)
*Real-time monitoring of intelligence assets, threat levels, and operational status*
<br>
<img src="screenshots/Dashboard-1.png" width="100%" alt="Main Dashboard" style="border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);">

<br><br>

### 📊 Divine Analytics & Wisdom
*Advanced visualization of threat matrices, trends, and network correlations*
<p align="center">
  <img src="screenshots/ANALYTICS-1.png" width="48%" alt="Analytics View" style="margin-right: 10px;" />
  <img src="screenshots/ANALYTICS-2.png" width="48%" alt="Threat Matrix" />
</p>

<br>

### ⚖️ The Hall of Judgment (Report Creation)
*IC-Standard data entry with real-time validation and forensic sanitization*
<p align="center">
  <img src="screenshots/Reports_Editing-1.png" width="48%" alt="Editing Interface" style="margin-right: 10px;" />
  <img src="screenshots/Report_ShowCase-1.png" width="48%" alt="Report Preview" />
</p>

<br>

### 🗄️ Sacred Archives (Management)
*Full-text search, version control, and audit trail tracking*
<img src="screenshots/Reports_Management-1.png" width="100%" alt="Report Management" style="border-radius: 10px;">

</div>

---


## 🔱 Sacred Capabilities

### 📋 Intelligence Dossier Generation

- **IC-Standard Classifications** - TOP SECRET, SECRET, CONFIDENTIAL, UNCLASSIFIED with proper caveat handling
- **TLP Protocol** - Traffic Light Protocol (RED/AMBER/GREEN/WHITE) distribution controls
- **14 Sacred Intelligence Sections**:
  - Executive Summary with threat assessment
  - Target Profile with physical descriptors
  - Biometric Data with collection metadata
  - Digital Footprint & OSINT analysis
  - Known Associates & network mapping
  - Financial Intelligence with forensic indicators
  - Communications Intelligence (COMINT/SIGINT)
  - Travel History & geospatial analysis
  - Behavioral Analysis & patterns
  - Threat Assessment with risk matrices
  - Operational History timeline
  - Known Incidents with attribution analysis
  - Intelligence Gaps identification
  - Recommendations & actionable intelligence

### 📊 Central Intelligence Analytics

- **Executive Intelligence Summary** - Real-time KPIs including asset count, high-priority targets, threat scores, compliance rates, and intelligence velocity
- **Threat Intelligence Matrix** - Interactive heatmaps visualizing threat levels by classification and priority
- **Operational Intelligence Center** - Entity status tracking, classification distribution, and agency workload metrics
- **Counterintelligence Metrics** - Redaction rates, encryption compliance, TLP distribution, and security indicators
- **Intelligence Collection Timeline** - Temporal analysis with collection velocity and trend tracking
- **Threat Actor Network Analysis** - Top entities by threat rating with intelligence gap identification
- **Divine Analytics**:
  - Correlation Analysis - Cross-reference patterns between entities
  - Trend Forecasting - Predictive intelligence with time-series analysis
  - Risk Assessment Matrix - Multi-factor threat scoring and prioritization

### 🛡️ Security & Compliance

- **PDF Encryption** - AES-256 password protection with user/owner permissions
- **EXIF Stripping** - Automatic metadata removal from images
- **Redaction System** - Visual black-bar censorship using `||redacted text||` syntax
- **Classification Controls** - Automated handling notices and distribution statements
- **Audit Logging** - Complete operation tracking with JSON-formatted logs
- **Input Validation** - Comprehensive field validation with security checks

### 🗄️ Sacred Database Management

- **SQLAlchemy ORM** - Professional database layer with relationship mapping
- **Report Versioning** - Track changes and maintain eternal history
- **Advanced Search** - Full-text search across all intelligence fields
- **Bulk Operations** - Mass export, batch processing, and data migration
- **Analytics Engine** - Built-in aggregation for metrics and dashboards

---

## ⚡ Quick Start

### Prerequisites

- Python 3.12 or higher
- pip package manager
- 500MB free disk space

### Installation

1. **Clone the sacred repository**
```bash
git clone https://github.com/MOmar990/Anubis_Intel.git
cd Anubis_Intel
```

2. **Set up virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Launch the platform**
```bash
streamlit run app.py
```

5. **Access the platform**
```
Open your browser to: http://localhost:8501
```

---

## 🎯 Usage

### Creating Your First Dossier

1. Navigate to **📋 CREATE REPORT** tab
2. Enter target information:
   - Name, aliases, status
   - Classification level (TOP SECRET → UNCLASSIFIED)
   - TLP marking for distribution control
3. Add intelligence sections:
   - Executive summary
   - Biometric data
   - Digital footprint
   - Known associates
   - Financial intelligence
4. Upload images (automatically stripped of EXIF data)
5. Click **GENERATE INTELLIGENCE REPORT**
6. PDF dossier saved to `output/` directory

### Database Management

- **View Reports** - Browse all generated dossiers
- **Search** - Full-text search across all fields
- **Export** - Download reports individually or in bulk
- **Delete** - Remove reports with audit trail

### Analytics Dashboard

- **Executive Summary** - Key intelligence metrics
- **Threat Matrix** - Visual threat level distribution
- **Trend Analysis** - Intelligence collection over time
- **Network Analysis** - Relationship mapping between entities

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

Key configuration options:

```bash
# Classification & Security
ANUBIS_PDF_ENCRYPT=true
ANUBIS_PDF_PASSWORD=CLASSIFIED
ANUBIS_EXIF_STRIP=true

# Templates
ANUBIS_DEFAULT_TEMPLATE=anubis_dossier

# Database
ANUBIS_DB_PATH=./database/anubis_intel.db

# Logging
ANUBIS_LOG_LEVEL=INFO
```

### Template Customization

Edit `templates/anubis_dossier.html` to customize report appearance:

- Header/footer styling
- Classification banner colors
- Section layouts
- Watermark positioning

---

## 📁 Project Structure

```
Anubis_Intel/
│
├── app.py                         # Main Streamlit application
├── requirements.txt               # Python dependencies
├── config_settings.json           # Application configuration
│
├── config/                        # Configuration module
│   ├── __init__.py               # Centralized config management
│
├── src/                          # Source code
│   ├── core/
│   │   ├── engine.py             # Main intelligence engine
│   │   ├── pdf_generator.py     # PDF generation & encryption
│   │   ├── image_processor.py   # EXIF stripping & validation
│   │   ├── intelligence_enricher.py    # Auto-enrichment
│   │   └── intelligence_formatter.py   # IC-standard formatting
│   │
│   └── utils/
│       ├── database.py           # SQLAlchemy ORM layer
│       └── validators.py         # Input validation utilities
│
├── templates/
│   └── anubis_dossier.html       # Sacred report template
│
├── output/                       # Generated PDF reports
├── database/                     # SQLite database storage
├── logs/                         # Application logs
├── assets/                       # Image uploads
└── data/                         # Temporary data storage
```

---

## 🔧 Technology Stack

- **Backend**: Python 3.12+
- **Web Framework**: Streamlit 1.51.0
- **PDF Generation**: WeasyPrint, ReportLab
- **Database**: SQLAlchemy + SQLite
- **Image Processing**: Pillow (PIL)
- **Data Analysis**: Pandas, NumPy
- **Visualization**: Plotly, Matplotlib

---

## 🎓 Intelligence Classification Guide

### Classification Levels

| Level | Description | Usage |
|-------|-------------|-------|
| TOP SECRET | Exceptionally grave damage to national security | Highest sensitivity |
| SECRET | Serious damage to national security | High sensitivity |
| CONFIDENTIAL | Damage to national security | Moderate sensitivity |
| UNCLASSIFIED | No damage to national security | Public or low sensitivity |

### TLP Markings

| TLP | Distribution | Usage |
|-----|-------------|-------|
| RED | No disclosure beyond specific exchange | Personal for named recipients only |
| AMBER | Limited disclosure | Recipients can share with organization |
| GREEN | Community wide | Share within community |
| WHITE | Unlimited | Public disclosure authorized |

---

## 👨‍💻 About the Creator

**Omar Taher** | Digital Forensics & Network Security Researcher

- 🔐 Security Researcher & Network Forensics Trainee @ **Anubis Security**
- 🎖️ Vice Head of Cybersecurity Committee @ **IEEE**
- 🛡️ Specialization: Network Traffic Analysis, Memory Forensics, Tool Development
- 🌍 Location: Egypt 🇪🇬

### 🎯 Expertise

- **Network Forensics**: Deep-dive PCAP analysis using Wireshark & Zeek
- **Threat Hunting**: Analyzing TTPs of APT groups
- **Tool Development**: Python and Bash automation for forensic artifact collection
- **Infrastructure Security**: Routing protocols (OSPF, BGP) and OT/ICS basics
- **Technical Leadership**: Mentoring and designing workshops on Linux & OS Internals

### 🔗 Connect

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/omartaher990/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MOmar990)
[![GitBook](https://img.shields.io/badge/GitBook-3884FF?style=for-the-badge&logo=gitbook&logoColor=white)](https://app.gitbook.com/o/Zl7vMcNBEX3etk8D9Tnv/s/wZQkLlCq33paDTdF8yVc/)

### 📚 Featured Projects

- **[Anubis-Vault](https://github.com/MOmar990/Anubis-Vault)** - Secret management with AES-256 encryption and steganography
- **[ShadowCourier](https://github.com/MOmar990/ShadowCourier)** - Secure file transfer with AES-256-CBC encryption
- **[Nexlify](https://github.com/MOmar990/Nexlify)** - Peer-to-peer messaging with end-to-end encryption

---

## 🏛️ Philosophy

> *"Like Anubis weighing the heart against Ma'at's feather, this platform weighs data against truth - separating signal from noise, intelligence from information, and revealing what lies hidden in the digital afterlife."*

The Anubis Intelligence Platform embodies:

- **Guardian Principle** - Protecting sensitive intelligence through encryption and access control
- **Judgment Principle** - Objective analysis free from bias
- **Eternal Record** - Maintaining complete audit trails and version history
- **Sacred Precision** - IC-standard formatting and compliance

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Anubis Intelligence Platform | Omar Taher

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code of conduct
- Development setup
- Submission guidelines
- Code style requirements

---

## 🔮 Roadmap

### Planned Features

- [ ] **Multi-language support** - Arabic, French, Spanish
- [ ] **API integration** - RESTful API for external systems
- [ ] **Real-time collaboration** - Multiple analysts working simultaneously
- [ ] **Machine learning** - Automated threat scoring and pattern detection
- [ ] **Blockchain audit trail** - Immutable change history
- [ ] **Mobile companion app** - iOS/Android report viewer
- [ ] **Advanced visualization** - 3D network graphs and timeline analysis

---

## ⚠️ Disclaimer

This tool is designed for **legal and authorized intelligence gathering operations only**. Users are responsible for ensuring compliance with all applicable laws and regulations. The creator assumes no liability for misuse.

---

## 🙏 Acknowledgments

- Intelligence Community for IC-standard formatting guidelines
- **Anubis Security** for training and mentorship
- **IEEE Cybersecurity Committee** for community support
- Open-source community for amazing libraries and tools

---

<div align="center">

### ⚱️ **Anubis Intelligence Platform** ⚱️

*Guardian of Digital Secrets | Keeper of Sacred Intelligence*

**Made with 🖤 in Egypt by [Omar Taher](https://github.com/MOmar990)**

⚖️ *Weighing Truth in the Digital Afterlife* ⚖️

</div>
