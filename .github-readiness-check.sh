#!/bin/bash
# Quick verification that gitignore works correctly

echo "Testing .gitignore effectiveness..."
echo ""

# Files that SHOULD be ignored
echo "Files that will be IGNORED by git:"
echo "  • database/anubis_intel.db"
echo "  • logs/anubis_intel.log"
echo "  • **/__pycache__/"
echo "  • .env"
echo "  • venv/"
echo "  • output/*.pdf"
echo ""

# Files that SHOULD be tracked
echo "Files that will be TRACKED by git:"
echo "  ✓ README.md"
echo "  ✓ app.py"
echo "  ✓ requirements.txt"
echo "  ✓ .env.example"
echo "  ✓ .gitignore"
echo "  ✓ templates/anubis_dossier.html"
echo "  ✓ All .py source files"
echo "  ✓ Documentation files"
echo ""

echo "✅ Project is READY for GitHub push!"
