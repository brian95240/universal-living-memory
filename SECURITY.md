# Security Policy

## Credential Management

### Best Practices

1. **Never commit credentials**: The `.env` file is excluded from version control via `.gitignore`
2. **Use Vaultwarden**: Store all API keys, passwords, and tokens in Vaultwarden or a secure password manager
3. **Environment Variables**: All sensitive data should be loaded from environment variables
4. **API Key Rotation**: Regularly rotate API keys and update them in your secure storage

### Required Credentials

This project requires the following credentials to be configured:

- **Database Password**: PostgreSQL password for the universal_memory database
- **AI Provider API Keys** (at least one):
  - Grok API Key (X.AI)
  - Anthropic API Key (Claude)
  - Gemini API Key (Google)
  - OpenAI API Key (optional)

### Setup Instructions

1. Copy `.env.example` to `.env`
2. Fill in your credentials from Vaultwarden
3. Run `python genesis.py` to auto-configure system resources
4. Launch with `docker compose up -d`

### Reporting Security Issues

If you discover a security vulnerability, please email the maintainers directly. Do not open a public issue.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Features

- **No Hard-coded Secrets**: All credentials are externalized
- **Docker Isolation**: Services run in isolated containers
- **Memory Limits**: Resource constraints prevent DoS
- **HTTPS Ready**: Orchestrator can be deployed behind reverse proxy with TLS
