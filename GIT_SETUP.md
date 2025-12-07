# Git Setup Instructions

Quick guide to initialize Git and push to GitHub.

## Initialize Repository

```bash
# Navigate to project
cd /home/omar/Desktop/Raven_Intel

# Initialize Git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Anubis Intelligence Platform v4.0

- Professional IC-standard intelligence report generation
- Central Intelligence Analytics dashboard
- Advanced PDF encryption and security
- Intelligence enrichment system
- Complete documentation and tests
"
```

## Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `Anubis_Intel` (or your preferred name)
3. Description: `Enterprise-grade intelligence report generation with IC-standard formatting`
4. **Keep it Private** (recommended for security tools)
5. **Do NOT** initialize with README, .gitignore, or license (already included)
6. Click "Create repository"

## Push to GitHub

```bash
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/Anubis_Intel.git

# Push to main branch
git branch -M main
git push -u origin main
```

## Alternative: SSH Setup

If you prefer SSH:

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: Settings → SSH Keys → New SSH Key
cat ~/.ssh/id_ed25519.pub

# Use SSH remote
git remote add origin git@github.com:YOUR_USERNAME/Anubis_Intel.git
git push -u origin main
```

## Repository Settings (Recommended)

After pushing, configure these GitHub settings:

### Security
- Settings → Security → Enable Dependabot alerts
- Settings → Security → Enable secret scanning

### Branch Protection
- Settings → Branches → Add rule for `main`
- ✓ Require pull request reviews before merging
- ✓ Require status checks to pass

### Topics
Add these topics to your repository for discoverability:
- `intelligence`
- `security`
- `pdf-generation`
- `streamlit`
- `python`
- `classification`
- `osint`
- `threat-intelligence`

### About Section
```
Enterprise-grade intelligence report generation system with 
IC-standard formatting, advanced analytics, and professional 
security features
```

## Verify Upload

```bash
# Check remote
git remote -v

# Check status
git status

# View commit history
git log --oneline
```

## Future Updates

When you make changes:

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add: brief description of changes"

# Push to GitHub
git push
```

## .gitignore Already Configured

The following are already excluded:
- `venv/` - Virtual environment
- `*.pyc`, `__pycache__/` - Python bytecode
- `output/*.pdf` - Generated reports
- `assets/*.jpg|png|jpeg` - Uploaded images
- `.env` - Environment secrets
- `*.log` - Log files
- `*.db` - Database files

## Repository Structure on GitHub

```
Anubis_Intel/
├── 📄 README.md          ← Will be shown on main page
├── 📄 LICENSE            ← MIT License visible
├── 📁 src/               ← Source code
├── 📁 templates/         ← Report templates
├── 📁 config/            ← Configuration
└── 📋 requirements.txt   ← Dependencies
```

## Troubleshooting

**Authentication failed?**
```bash
# Use personal access token instead of password
# Generate at: Settings → Developer settings → Personal access tokens
```

**Large files rejected?**
```bash
# Check file sizes
find . -type f -size +50M

# Use Git LFS for large files if needed
git lfs install
```

**Wrong remote URL?**
```bash
# Remove and re-add
git remote remove origin
git remote add origin <correct-url>
```

---

🎉 **You're all set!** Your professional intelligence platform is now on GitHub.
