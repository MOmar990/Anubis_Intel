# Contributing to Anubis Intelligence Platform

Thank you for your interest in contributing to the Anubis Intelligence Platform! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and professional in all interactions
- Focus on constructive feedback
- Help maintain a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the issue template if available
3. Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)
   - Screenshots if applicable

### Suggesting Features

1. Open an issue with the "enhancement" label
2. Describe the feature and its use case
3. Explain why it would benefit users
4. Consider implementation complexity

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/MOmar990/Anubis_Intel.git
   cd Anubis_Intel
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation as needed

5. **Test your changes**
   ```bash
   # Run the application
   streamlit run app.py
   
   # Test imports
   python -c "from src.core.pdf_generator import PDFGenerator; print('OK')"
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request**
   - Provide clear description of changes
   - Reference related issues
   - Include screenshots for UI changes

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8 guidelines
- **Naming**: Use descriptive variable and function names
- **Comments**: Document complex logic and intelligence standards
- **Type Hints**: Use where appropriate for clarity

### Project Structure

```
src/
├── core/           # Core intelligence processing
│   ├── engine.py              # Report generation
│   ├── pdf_generator.py       # PDF creation
│   ├── intelligence_enricher.py   # Data enrichment
│   └── intelligence_formatter.py  # IC formatting
└── utils/          # Utility functions
    ├── database.py     # Database operations
    └── validators.py   # Input validation
```

### Adding New Features

#### New Intelligence Section
1. Update `src/core/intelligence_enricher.py` with enrichment logic
2. Add section to `templates/anubis_dossier.html`
3. Update `app.py` with UI fields
4. Update README.md with feature description

#### New Template
1. Create HTML template in `templates/`
2. Add to `config_settings.json` under `available_templates`
3. Test with sample data
4. Document template features

#### New Classification Level
1. Update `IntelligenceFormatter.CLASSIFICATION_LEVELS`
2. Add color scheme to template CSS
3. Update documentation
4. Test PDF generation

### Testing Checklist

Before submitting a PR, verify:
- [ ] Application starts without errors
- [ ] All imports work correctly
- [ ] New features work as expected
- [ ] PDF generation succeeds
- [ ] No broken links in documentation
- [ ] Code follows project style
- [ ] No sensitive data in commits

## Intelligence Community Standards

When contributing features related to IC standards:

- **Classifications**: Follow EO 13526 guidelines
- **TLP Protocol**: Adhere to FIRST TLP v2.0 specs
- **Terminology**: Use authentic IC terminology
- **Formatting**: Match professional agency standards

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for general questions
- Check existing documentation first
- Be specific about your question or problem

## Recognition

Contributors will be acknowledged in the project documentation. Significant contributions may be highlighted in release notes.

Thank you for helping improve the Anubis Intelligence Platform!
