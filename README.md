# Universal Living Memory

Standalone, hardware-agnostic, zero-cost AI memory orchestrator.

## Features

- **Hardware Discovery**: Automatically detects system resources and configures optimal settings
- **Multi-Provider Support**: Integrates with Grok, Anthropic, Gemini, and local models
- **Vector Memory**: Persistent memory using Qdrant vector database
- **Resource Management**: Dynamic client hydration and collapse for efficient memory usage
- **Docker-Based**: Easy deployment with Docker Compose

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/brian95240/universal-living-memory.git
cd universal-living-memory

# 2. Configure credentials
cp .env.example .env
# Edit .env with your API keys (store them in Vaultwarden first!)

# 3. Run genesis to configure system
python genesis.py

# 4. Launch infrastructure
docker compose up -d

# 5. Check health
curl http://localhost:8000/health
```

## Configuration

### Required Credentials

Store all credentials securely in **Vaultwarden** or your password manager before adding them to `.env`:

- **POSTGRES_PASSWORD**: Database password
- **GROK_API_KEY**: X.AI Grok API key
- **ANTHROPIC_API_KEY**: Anthropic Claude API key
- **GEMINI_API_KEY**: Google Gemini API key

See [SECURITY.md](SECURITY.md) for detailed credential management guidelines.

### Provider Configuration

Edit `config/providers.json` to enable/disable AI providers:

```json
{
  "providers": {
    "grok": {
      "enabled": true,
      "api_key_env": "GROK_API_KEY"
    },
    "anthropic": {
      "enabled": true,
      "api_key_env": "ANTHROPIC_API_KEY"
    },
    "gemini": {
      "enabled": true,
      "api_key_env": "GEMINI_API_KEY",
      "model": "gemini-1.5-pro"
    }
  }
}
```

## Architecture

- **FastAPI Orchestrator**: Main API server
- **PostgreSQL**: Relational data storage
- **Qdrant**: Vector database for semantic memory
- **Provider Manager**: Dynamic AI provider client management with TTL-based collapse
- **Memory Engine**: FastEmbed-based semantic memory with automatic hydration/collapse

## API Usage

```bash
# Chat completion with memory
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "grok",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"}
    ],
    "use_memory": true
  }'
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## Security

See [SECURITY.md](SECURITY.md) for security policies and credential management.

## License

AGPL-3.0 + Commercial (see [LICENSE](LICENSE))

## Related Projects

- [Genesis Studio](https://github.com/brian95240/genesis-studio) - Voice-guided AI project creation client
