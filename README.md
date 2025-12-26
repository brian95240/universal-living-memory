# Universal Living Memory

Standalone, hardware-agnostic, zero-cost AI memory orchestrator with hyper-dynamic capabilities.

## 🚀 Features (v1.0.1)

### Core Capabilities
- **Hardware Discovery**: Automatically detects system resources and configures optimal settings
- **Multi-Provider Support**: Integrates with Grok, Anthropic, Gemini, and local models
- **Vector Memory**: Persistent memory using Qdrant vector database
- **Resource Management**: Dynamic client hydration and collapse for efficient memory usage
- **Docker-Based**: Easy deployment with Docker Compose

### v1.0.1 Enhancements
- **🔥 Runtime Provider Registration**: Add new AI providers without restarting (`POST /v1/providers`)
- **💰 Cloud Spot Pricing Discovery**: Monitor cheapest GPU options across providers (`GET /v1/cloud/pricing`)
- **⏱️ Self-Termination**: Automatic shutdown after 30 minutes of inactivity (configurable)
- **🔄 Dynamic Configuration**: Mutable provider registry with hot-reload
- **📊 Health Monitoring**: Enhanced health endpoint with idle time tracking

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

The system now supports **runtime provider registration**. You can add providers dynamically via API:

```bash
curl -X POST http://localhost:8000/v1/providers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "together",
    "base_url": "https://api.together.xyz/v1",
    "auth_header": "Authorization",
    "auth_prefix": "Bearer",
    "api_key_value": "your_api_key_here",
    "models": ["mistralai/Mixtral-8x7B-Instruct-v0.1"]
  }'
```

Or edit `config/providers.json` directly:

```json
{
  "providers": {
    "grok": {
      "base_url": "https://api.x.ai/v1",
      "auth_header": "Authorization",
      "auth_prefix": "Bearer",
      "api_key_env": "GROK_API_KEY",
      "models": ["grok-beta"]
    }
  }
}
```

### Lifecycle Configuration

To disable auto-shutdown (for production):

```bash
# Add to .env
DISABLE_LIFECYCLE=true
```

## Architecture

- **FastAPI Orchestrator**: Main API server with dynamic routing
- **PostgreSQL**: Relational data storage
- **Qdrant**: Vector database for semantic memory
- **Dynamic Provider Manager**: Runtime provider registration with TTL-based collapse
- **Memory Engine**: FastEmbed-based semantic memory with automatic hydration/collapse
- **Cloud Delta Engine**: Spot pricing aggregation across cloud providers
- **Lifecycle Monitor**: Automatic resource cleanup and self-termination

## API Endpoints

### Chat Completion
```bash
POST /v1/chat/completions
```

### Provider Management
```bash
POST /v1/providers        # Register new provider
GET /v1/providers         # List all providers
```

### Cloud Pricing
```bash
GET /v1/cloud/pricing     # Get spot pricing data
GET /v1/cloud/cheapest    # Get cheapest GPU option
```

### Health & Status
```bash
GET /health               # System health with idle time
GET /                     # API info and features
```

## API Usage Example

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

## Changelog

### v1.0.1 (Hyper-Dynamic)
- Added runtime provider registration
- Added cloud spot pricing discovery
- Added self-termination for idle systems
- Enhanced dynamic configuration system
- Improved health monitoring

### v1.0.0 (Golden Master)
- Initial release
- Multi-provider AI integration
- Vector memory with Qdrant
- Docker containerization
