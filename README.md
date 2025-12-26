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
# 1. Run genesis to configure system
python genesis.py

# 2. Launch infrastructure
docker compose up -d

# 3. Check health
curl http://localhost:8000/health
```

## Architecture

- **FastAPI Orchestrator**: Main API server
- **PostgreSQL**: Relational data storage
- **Qdrant**: Vector database for semantic memory
- **Provider Manager**: Dynamic AI provider client management
- **Memory Engine**: FastEmbed-based semantic memory with TTL

## License

AGPL-3.0 + Commercial
