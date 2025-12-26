# Contributing to Universal Living Memory

Thank you for your interest in contributing to the Vertex Genesis project!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/universal-living-memory.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Commit with clear messages: `git commit -m "Add feature: description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# 1. Install dependencies
pip install -r orchestrator/requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Run genesis configuration
python genesis.py

# 4. Start services
docker compose up -d

# 5. Test the API
curl http://localhost:8000/health
```

## Code Standards

- Follow PEP 8 for Python code
- Add docstrings to functions and classes
- Keep functions focused and modular
- Write tests for new features
- Ensure `.gitignore` is comprehensive

## Security Guidelines

- **Never commit credentials** or API keys
- Store all secrets in environment variables
- Use Vaultwarden for credential management
- Follow the security policy in SECURITY.md

## Pull Request Guidelines

- Provide a clear description of changes
- Reference related issues
- Include tests if applicable
- Update documentation as needed
- Ensure CI checks pass

## Code Review Process

1. Maintainers will review PRs within 7 days
2. Address feedback and requested changes
3. Once approved, maintainers will merge

## Questions?

Open an issue for questions or discussions.

## License

By contributing, you agree that your contributions will be licensed under the AGPL-3.0 license.
