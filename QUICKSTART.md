# Quick Start Guide

Get Anubis Intelligence Platform running in under 2 minutes.

## Prerequisites

- Python 3.12 or higher
- pip package manager

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/MOmar990/Anubis_Intel.git
cd Anubis_Intel
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
streamlit run app.py
```

The application will automatically open at `http://localhost:8501`

## First Report

1. Go to **📝 Create Report** tab
2. Fill in basic information:
   - Classification: `SECRET`
   - TLP Level: `AMBER`
   - Report Title: `Test Subject Assessment`
   - Full Name: `John Doe`
3. Add some intelligence data in the text areas
4. Click **Generate Report**

Your first PDF will be in the `output/` folder!

## Directory Structure

After setup, your project will look like:
```
Anubis_Intel/
├── app.py              # Main application
├── database/           # SQLite database
├── output/             # Generated PDFs
├── logs/               # Application logs
├── assets/             # Uploaded images
└── templates/          # Report templates
```

## Troubleshooting

**Port already in use?**
```bash
streamlit run app.py --server.port 8502
```

**Missing dependencies?**
```bash
pip install -r requirements.txt --upgrade
```

**Database locked?**
```bash
rm database/raven_intel.db
# Restart the app to recreate
```

## Next Steps

- Read the full [README.md](README.md) for all features
- Explore the Analytics dashboard
- Try different classification levels
- Test the redaction system with `||redacted||` syntax
- Enable PDF encryption in Settings tab

## Support

Having issues? Check:
- Existing GitHub issues
- Application logs in `logs/raven_intel.log`
- Streamlit community forums

Happy intelligence reporting! ⚱️
