# Universal Living Memory

Universal AI connection framework with three symbiotic libraries: API, Webhook, and MCP.

## 🚀 Features (v1.1.0 - Universal)

### Universal Connection Framework
- **🔑 API Connection Library**: Connect to ANY AI model or API service
  - OpenAI, Anthropic, Google, Grok, Together AI, Mistral, etc.
  - Custom authentication (Bearer, API Key, Custom headers)
  - Multi-model support per connection
  - Dynamic capability detection
  
- **🪝 Webhook Library**: Event-driven integrations
  - Zapier, n8n, Make, custom webhooks
  - Event filtering (completion, error, all)
  - Multiple HTTP methods (POST, GET, PUT)
  - Automatic triggering on events
  
- **🔧 MCP Server Library**: Model Context Protocol integrations
  - Filesystem access
  - Database connections
  - Custom tool servers
  - Extensible capabilities

### Core Capabilities
- **Hardware Discovery**: Automatically detects system resources
- **Vector Memory**: Persistent memory using Qdrant
- **Resource Management**: Dynamic client hydration and collapse
- **Cloud Spot Pricing**: Monitor cheapest GPU options
- **Self-Termination**: Automatic shutdown after inactivity
- **Docker-Based**: Easy deployment

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

## Universal Connection Management

### Add API Connection

```bash
curl -X POST http://localhost:8000/v1/connections/api \
  -H "Content-Type: application/json" \
  -d '{
    "conn_id": "together_ai",
    "name": "Together AI",
    "base_url": "https://api.together.xyz/v1",
    "auth_type": "bearer",
    "api_key_value": "your_api_key_here",
    "models": ["mistralai/Mixtral-8x7B-Instruct-v0.1"],
    "capabilities": ["chat", "completion"],
    "enabled": true
  }'
```

### Add Webhook

```bash
curl -X POST http://localhost:8000/v1/connections/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_id": "zapier_hook",
    "name": "Zapier Integration",
    "url": "https://hooks.zapier.com/hooks/catch/...",
    "method": "POST",
    "events": ["completion", "error"],
    "enabled": true
  }'
```

### Add MCP Server

```bash
curl -X POST http://localhost:8000/v1/connections/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "filesystem",
    "name": "Filesystem MCP",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    "capabilities": ["read", "write", "list"],
    "enabled": true
  }'
```

## Architecture

- **FastAPI Orchestrator**: Main API server with universal routing
- **PostgreSQL**: Relational data storage
- **Qdrant**: Vector database for semantic memory
- **Connection Library Manager**: Three symbiotic libraries (API, Webhook, MCP)
- **Universal Adapter**: Dynamic connection handling for any service
- **Memory Engine**: FastEmbed-based semantic memory
- **Cloud Delta Engine**: Spot pricing aggregation
- **Lifecycle Monitor**: Automatic resource cleanup

## API Endpoints

### Connection Management
```bash
# API Connections
POST /v1/connections/api          # Add API connection
GET /v1/connections/api           # List API connections
DELETE /v1/connections/api/{id}   # Remove API connection

# Webhooks
POST /v1/connections/webhook      # Add webhook
GET /v1/connections/webhook       # List webhooks
DELETE /v1/connections/webhook/{id} # Remove webhook

# MCP Servers
POST /v1/connections/mcp          # Add MCP server
GET /v1/connections/mcp           # List MCP servers
DELETE /v1/connections/mcp/{id}   # Remove MCP server

# Universal Operations
GET /v1/connections/all           # Get all connections
GET /v1/connections/search?q=     # Search connections
GET /v1/connections/stats         # Get statistics
POST /v1/connections/confirm      # AI confirmation
```

### Chat Completion
```bash
POST /v1/chat/completions         # Chat with any provider
```

### Cloud Pricing
```bash
GET /v1/cloud/pricing             # Get spot pricing
GET /v1/cloud/cheapest            # Get cheapest GPU
```

### Health & Status
```bash
GET /health                       # System health
GET /                             # API info
```

## Supported Services

### AI Models (API Library)
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- X.AI (Grok)
- Together AI (Mixtral, Llama)
- Mistral AI
- Cohere
- Replicate
- Any OpenAI-compatible API

### Webhooks (Webhook Library)
- Zapier
- n8n
- Make (Integromat)
- IFTTT
- Custom webhooks
- Slack webhooks
- Discord webhooks

### MCP Servers (MCP Library)
- Filesystem
- PostgreSQL
- SQLite
- GitHub
- Google Drive
- Custom MCP servers

## Configuration Files

Connection libraries are stored in JSON format:
- `config/api_library.json` - API connections
- `config/webhook_library.json` - Webhooks
- `config/mcp_library.json` - MCP servers

All libraries support hot-reload without restart.

## Security

- Store all credentials in **Vaultwarden**
- Use environment variables for API keys
- Never commit credentials to git
- See [SECURITY.md](SECURITY.md) for details

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

AGPL-3.0 + Commercial (see [LICENSE](LICENSE))

## Related Projects

- [Genesis Studio](https://github.com/brian95240/genesis-studio) - Voice-guided client with connection management

## Changelog

### v1.1.0 (Universal)
- Added Universal Connection Framework
- Added API Connection Library
- Added Webhook Library
- Added MCP Server Library
- Added Universal Adapter for dynamic connections
- Enhanced future-proof architecture

### v1.0.1 (Hyper-Dynamic)
- Added runtime provider registration
- Added cloud spot pricing discovery
- Added self-termination for idle systems

### v1.0.0 (Golden Master)
- Initial release
- Multi-provider AI integration
- Vector memory with Qdrant
