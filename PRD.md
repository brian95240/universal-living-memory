# Vertex Genesis v1.1.0 - Product & Engineering Requirements Document

**Version**: 1.1.0 Apex Release  
**Date**: December 26, 2024  
**Status**: Production Ready  
**License**: AGPL-3.0 + Commercial Dual License

---

## Table of Contents

1. [System Vision & Philosophy](#system-vision--philosophy)
2. [Architecture Overview](#architecture-overview)
3. [Component Specifications](#component-specifications)
4. [Dependency Graph](#dependency-graph)
5. [Data Flow Diagram](#data-flow-diagram)
6. [End-to-End Engineering Workflow](#end-to-end-engineering-workflow)
7. [Symbiosis Library Specifications](#symbiosis-library-specifications)
8. [Voice Command Confirmation Flow](#voice-command-confirmation-flow)
9. [Deployment Instructions](#deployment-instructions)
10. [Extension Points](#extension-points)
11. [Security & Credentials](#security--credentials)
12. [Testing & Validation](#testing--validation)

---

## System Vision & Philosophy

### Core Philosophy

**Vertex Genesis** is a hyper-dynamic, universal AI connection framework embodying four cardinal principles:

1. **Hyper-Dynamic**: Add, modify, or remove connections without code changes or system restart
2. **Universal**: Connect to ANY AI model, tool, or platform through three symbiotic libraries
3. **Zero-Cost Seeking**: Optimize for spot pricing, auto-collapse idle resources, minimize operational costs
4. **Evanescent**: Self-terminating when idle, ephemeral by design, no persistent overhead

### System Vision

Create a **symbiotic AI orchestration ecosystem** where:
- **Any AI model** can be integrated via natural language voice commands
- **Any automation tool** can be triggered via webhooks
- **Any capability** can be extended via MCP servers
- **Zero engineering overhead** for adding new services
- **Voice-first interface** with AI confirmation for accuracy
- **Future-proof architecture** requiring no code changes for new technologies

### Design Principles

1. **Symbiosis Over Integration**: Three libraries (API, Webhook, MCP) work together organically
2. **Voice Over Forms**: Natural language as primary interface, forms as fallback
3. **Confirmation Over Assumption**: AI validates all user inputs before execution
4. **Collapse Over Persistence**: Resources hydrate on-demand and collapse when idle
5. **JSON Over Database**: Human-readable configuration files over opaque databases
6. **Hot-Reload Over Restart**: All changes apply immediately without downtime

---

## Architecture Overview

### System Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                        VERTEX GENESIS v1.1.0                     │
│                   Universal Connection Framework                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────────────┐
│   Genesis Studio     │◄────────┤  Universal Living Memory     │
│   (Client Layer)     │  HTTP   │  (Orchestrator Layer)        │
│                      │         │                              │
│  - Gradio UI         │         │  - FastAPI Server            │
│  - Voice Input       │         │  - Connection Libraries      │
│  - AI Parser         │         │  - Universal Adapter         │
│  - Whisper STT       │         │  - Memory Engine             │
└──────────────────────┘         └──────────────────────────────┘
         │                                    │
         │                                    ├─────────────────┐
         │                                    │                 │
         └────────────────┬───────────────────┘                 │
                          │                                     │
              ┌───────────▼──────────┐                          │
              │  Three Symbiotic     │                          │
              │  Connection Libraries│                          │
              └──────────────────────┘                          │
                          │                                     │
         ┌────────────────┼────────────────┐                    │
         │                │                │                    │
    ┌────▼─────┐    ┌────▼─────┐    ┌────▼─────┐         ┌────▼─────┐
    │   API    │    │ Webhook  │    │   MCP    │         │ Qdrant   │
    │ Library  │    │ Library  │    │ Library  │         │ Vector   │
    │          │    │          │    │          │         │ Memory   │
    └────┬─────┘    └────┬─────┘    └────┬─────┘         └──────────┘
         │               │               │
    ┌────▼─────────┐┌───▼──────────┐┌───▼──────────┐
    │ AI Providers ││  Automation  ││ Tool Servers │
    │ (OpenAI,     ││  (Zapier,    ││ (Filesystem, │
    │  Anthropic,  ││   n8n,       ││  PostgreSQL, │
    │  Grok, etc.) ││   Slack)     ││  GitHub)     │
    └──────────────┘└──────────────┘└──────────────┘
```

### Repository Structure

**Repository A: universal-living-memory** (Core Orchestrator)
- FastAPI-based orchestration server
- Three symbiotic connection libraries
- Universal adapter for dynamic connections
- Vector memory with Qdrant
- Cloud spot pricing engine
- Lifecycle management (self-termination)

**Repository B: genesis-studio** (Client)
- Gradio web interface
- Voice input with Faster-Whisper
- AI-powered connection parser
- Multi-agent project creation workflow
- Connection management UI

---

## Component Specifications

### 1. Core Orchestrator (universal-living-memory)

#### 1.1 FastAPI Server (main.py)

**Version**: FastAPI 0.104.1  
**Purpose**: HTTP API server for orchestration  
**Port**: 8000  
**Endpoints**: 19 total

**Core Endpoints**:
- `POST /v1/chat/completions` - Universal chat completion
- `GET /health` - Health check with statistics
- `GET /` - API information

**Connection Management Endpoints**:
- `POST /v1/connections/api` - Add API connection
- `GET /v1/connections/api` - List API connections
- `DELETE /v1/connections/api/{id}` - Remove API connection
- `POST /v1/connections/webhook` - Add webhook
- `GET /v1/connections/webhook` - List webhooks
- `DELETE /v1/connections/webhook/{id}` - Remove webhook
- `POST /v1/connections/mcp` - Add MCP server
- `GET /v1/connections/mcp` - List MCP servers
- `DELETE /v1/connections/mcp/{id}` - Remove MCP server
- `GET /v1/connections/all` - Get all connections
- `GET /v1/connections/search?q=` - Search connections
- `GET /v1/connections/stats` - Connection statistics
- `POST /v1/connections/confirm` - AI confirmation

**Legacy Endpoints** (v1.0.1 compatibility):
- `POST /v1/providers` - Register provider
- `GET /v1/providers` - List providers
- `GET /v1/cloud/pricing` - Spot pricing
- `GET /v1/cloud/cheapest` - Cheapest GPU

#### 1.2 Connection Library Manager (connection_library.py)

**Lines of Code**: 421  
**Purpose**: Manages three symbiotic connection libraries

**Classes**:
- `ConnectionType(Enum)`: API, WEBHOOK, MCP
- `ConnectionLibrary`: Main manager class

**Storage**:
- `config/api_library.json` - API connections
- `config/webhook_library.json` - Webhooks
- `config/mcp_library.json` - MCP servers

**API Connection Schema**:
```json
{
  "connections": {
    "connection_id": {
      "name": "string",
      "base_url": "string",
      "auth_type": "bearer|api_key|custom",
      "api_key_env": "string|null",
      "api_key_value": "string|null",
      "auth_header": "string|null",
      "auth_prefix": "string|null",
      "models": ["string"],
      "capabilities": ["string"],
      "headers": {},
      "enabled": true,
      "added_at": 1234567890.0
    }
  }
}
```

**Webhook Schema**:
```json
{
  "webhooks": {
    "webhook_id": {
      "name": "string",
      "url": "string",
      "method": "POST|GET|PUT",
      "headers": {},
      "events": ["completion", "error", "all"],
      "enabled": true,
      "added_at": 1234567890.0
    }
  }
}
```

**MCP Server Schema**:
```json
{
  "servers": {
    "server_id": {
      "name": "string",
      "command": "string",
      "args": ["string"],
      "capabilities": ["string"],
      "enabled": true,
      "added_at": 1234567890.0
    }
  }
}
```

**Methods**:
- `add_api_connection(conn_id, config)` - Add/update API connection
- `remove_api_connection(conn_id)` - Remove API connection
- `list_api_connections(enabled_only)` - List API connections
- `add_webhook(webhook_id, config)` - Add/update webhook
- `remove_webhook(webhook_id)` - Remove webhook
- `list_webhooks(enabled_only)` - List webhooks
- `trigger_webhook(webhook_id, payload)` - Trigger webhook
- `add_mcp_server(server_id, config)` - Add/update MCP server
- `remove_mcp_server(server_id)` - Remove MCP server
- `list_mcp_servers(enabled_only)` - List MCP servers
- `get_all_connections()` - Get all connections
- `search_connections(query)` - Search across libraries
- `get_stats()` - Get statistics

#### 1.3 Universal Adapter (universal_adapter.py)

**Lines of Code**: 226  
**Purpose**: Dynamic connection handling for any API format

**Classes**:
- `UniversalAdapter`: Main adapter class

**Supported API Formats**:
- OpenAI-compatible (default)
- Anthropic Claude
- Google Gemini
- Auto-detection based on base URL

**Methods**:
- `get_client(conn_id, conn_type)` - Get/create HTTP client
- `call_api(conn_id, endpoint, method, data, params)` - Universal API call
- `chat_completion(conn_id, messages, model, **kwargs)` - Universal chat
- `trigger_webhooks(event, payload)` - Trigger all subscribed webhooks
- `list_available_models(conn_id)` - List models for connection
- `validate_connection(conn_id, conn_type)` - Test connection
- `close_all_clients()` - Cleanup

**Authentication Types**:
- `bearer`: Authorization: Bearer {token}
- `api_key`: x-api-key: {token}
- `custom`: Custom header with prefix

#### 1.4 Memory Engine (memory.py)

**Purpose**: Vector memory with Qdrant  
**Model**: fastembed (BAAI/bge-small-en-v1.5)  
**Embedding Dimension**: 384

**Methods**:
- `memorize(query, response)` - Store interaction
- `recall(query, top_k=3)` - Retrieve relevant context

**Storage**:
- Qdrant vector database
- Collection: "vertex_memory"
- Distance metric: Cosine

#### 1.5 Dynamic Provider Manager (dynamic_manager.py)

**Purpose**: Legacy provider management (v1.0.1 compatibility)  
**TTL**: 300 seconds (5 minutes)

**Methods**:
- `register_provider(name, config_dict)` - Register provider
- `get_client(provider)` - Get/hydrate client
- `mark_used(provider)` - Update last used timestamp
- `reload_config()` - Reload configuration

#### 1.6 Cloud Delta Engine (cloud_delta.py)

**Purpose**: Spot pricing discovery  
**Refresh Interval**: 900 seconds (15 minutes)

**Methods**:
- `get_pricing()` - Get cached pricing (auto-refresh if stale)
- `get_cheapest_gpu(min_vram_gb)` - Find cheapest GPU option

**Data Sources** (stubbed for FOSS):
- TensorDock API
- Vast.ai API
- RunPod API

#### 1.7 Lifecycle Monitor (lifecycle.py)

**Purpose**: Self-termination when idle  
**Idle Threshold**: 1800 seconds (30 minutes)  
**Check Interval**: 60 seconds

**Methods**:
- `touch()` - Mark activity
- `get_idle_time()` - Get current idle time
- `_monitor()` - Background monitoring thread

**Behavior**:
- Warning at 80% threshold (24 minutes)
- Graceful shutdown via SIGTERM at 100% threshold (30 minutes)
- Disabled via `DISABLE_LIFECYCLE=true` environment variable

#### 1.8 Genesis Hardware Discovery (genesis.py)

**Purpose**: Hardware detection and configuration generation

**Detection**:
- OS: `platform.system()`
- CPU cores: `psutil.cpu_count(logical=False)`
- RAM: `psutil.virtual_memory().total`
- GPU: `torch.cuda.is_available()`, `torch.cuda.get_device_properties()`

**Output**:
- `.env` file with hardware-optimized settings
- `config/providers.json` initialization

#### 1.9 Docker Infrastructure (docker-compose.yml)

**Services**:

1. **orchestrator**
   - Image: Custom (built from orchestrator/Dockerfile)
   - Port: 8000
   - Depends on: postgres, qdrant
   - Restart: unless-stopped

2. **postgres**
   - Image: postgres:16-alpine
   - Port: 5432
   - Volume: postgres_data
   - Environment: POSTGRES_PASSWORD

3. **qdrant**
   - Image: qdrant/qdrant:v1.7.4
   - Port: 6333
   - Volume: qdrant_data
   - Restart: unless-stopped

**Volumes**:
- `postgres_data`: PostgreSQL data
- `qdrant_data`: Qdrant vector storage

### 2. Genesis Studio (genesis-studio)

#### 2.1 Studio Interface (genesis_studio.py)

**Framework**: Gradio 4.x  
**Port**: 7860  
**Theme**: Monochrome

**Tabs**:

1. **🚀 Create Tab**
   - Project vision input
   - AI provider selection
   - Initialize swarm button
   - Mute/unmute voice button
   - Swarm log output
   - Hidden microphone component (streaming)

2. **🔌 Connections Tab**
   - Connection statistics dashboard
   - Three sub-tabs:
     - **🔑 API Connections**: Voice + manual input
     - **🪝 Webhooks**: Voice + manual input
     - **🔧 MCP Servers**: Voice + manual input
   - Add/Remove/List operations for each type

3. **🔧 Matrix Tab**
   - Cloud spot pricing monitor
   - Whisper model unloading
   - System health check

4. **ℹ️ About Tab**
   - Feature documentation
   - Voice command examples
   - Architecture overview
   - Version history

#### 2.2 Voice Input System

**Model**: faster-whisper (distil-large-v3)  
**Device**: Auto-detect (CUDA if available, else CPU)  
**Compute Type**: int8

**Components**:
- `lazy_load()` - Load Whisper on first use
- `unload_whisper()` - Free memory
- `listen_loop(audio)` - Process streaming audio
- `toggle_mute()` - Mute/unmute control

**State Management**:
```python
class State:
    listening: bool      # Build in progress
    interrupt: bool      # Voice interrupt flag
    muted: bool          # Mute state
    voice_command_mode: bool  # Connection command mode
```

#### 2.3 Voice Command Parser

**Purpose**: Parse natural language connection commands

**Function**: `parse_connection_from_voice(voice_input, connection_type)`

**AI Prompt Template**:
```
Parse this voice command to add a {connection_type} connection.
Extract the following details and respond in JSON format:

Voice input: "{voice_input}"

For API connections, extract:
- conn_id (short identifier, lowercase with underscores)
- name (full name)
- base_url (API endpoint URL)
- auth_type (bearer, api_key, or custom)
- api_key (if mentioned)
- models (comma-separated list if mentioned)

[Similar for Webhooks and MCP Servers]

Respond ONLY with valid JSON. If information is missing, use null.
```

**Confirmation Flow**:
1. Parse voice input via AI
2. Extract JSON from response
3. Format confirmation message
4. Display to user for review
5. User confirms or corrects manually

#### 2.4 Multi-Agent Workflow

**Function**: `project_manager(prompt, provider, history)`

**Agents**:
1. **Architect**: Outlines files and structure
2. **Engineer**: Generates implementation code

**Flow**:
```
User Prompt → Architect (design) → Engineer (code) → Output
              ↑
              └─ Voice Interrupt Capability
```

**Provider Selection**:
- Architect: Prefers Anthropic if available, else user-selected
- Engineer: User-selected provider

---

## Dependency Graph

### Core Orchestrator Dependencies

**Python Version**: 3.11+

**requirements.txt** (orchestrator/requirements.txt):
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
httpx==0.25.1
psycopg2-binary==2.9.9
qdrant-client==1.7.0
fastembed==0.1.3
psutil==5.9.6
torch==2.1.1
```

**Pinned Versions Rationale**:
- `fastapi==0.104.1`: Stable release with all needed features
- `uvicorn==0.24.0`: Production-grade ASGI server
- `pydantic==2.5.0`: Data validation with v2 performance
- `httpx==0.25.1`: Async HTTP client for API calls
- `psycopg2-binary==2.9.9`: PostgreSQL adapter
- `qdrant-client==1.7.0`: Matches Qdrant server version
- `fastembed==0.1.3`: Lightweight embedding model
- `psutil==5.9.6`: System resource monitoring
- `torch==2.1.1`: GPU detection (CPU-only install acceptable)

**Docker Images**:
- `python:3.11-slim`: Base image for orchestrator
- `postgres:16-alpine`: PostgreSQL database
- `qdrant/qdrant:v1.7.4`: Vector database

### Genesis Studio Dependencies

**Python Version**: 3.11+

**requirements.txt** (studio/requirements.txt):
```
gradio==4.8.0
faster-whisper==0.10.0
requests==2.31.0
torch==2.1.1
```

**Pinned Versions Rationale**:
- `gradio==4.8.0`: Latest stable with streaming audio
- `faster-whisper==0.10.0`: Optimized Whisper implementation
- `requests==2.31.0`: HTTP client for orchestrator API
- `torch==2.1.1`: Required for Whisper (GPU optional)

**System Dependencies**:
- `ffmpeg`: Audio processing (install via apt/brew)
- Microphone access: Browser permissions required

### Dependency Installation Order

**For Orchestrator**:
```bash
# 1. System dependencies
apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl

# 2. Python dependencies
pip3 install --no-cache-dir -r orchestrator/requirements.txt

# 3. Docker images (pulled automatically by docker-compose)
docker-compose pull
```

**For Studio**:
```bash
# 1. System dependencies
apt-get update && apt-get install -y ffmpeg

# 2. Python dependencies
pip3 install --no-cache-dir -r studio/requirements.txt
```

---

## Data Flow Diagram

### Complete System Data Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION LAYER                        │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              ┌─────▼─────┐   ┌────▼────┐   ┌─────▼─────┐
              │   Voice   │   │  Text   │   │    API    │
              │   Input   │   │  Input  │   │   Call    │
              └─────┬─────┘   └────┬────┘   └─────┬─────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
┌──────────────────────────────────────────────────────────────────────┐
│                        GENESIS STUDIO (Client)                        │
│                                                                       │
│  ┌────────────┐   ┌──────────────┐   ┌─────────────────┐           │
│  │  Whisper   │──▶│  AI Parser   │──▶│  Confirmation   │           │
│  │    STT     │   │  (Connection)│   │     Dialog      │           │
│  └────────────┘   └──────────────┘   └─────────────────┘           │
│                                                │                     │
│                                                ▼                     │
│                                    ┌───────────────────┐            │
│                                    │  HTTP Request to  │            │
│                                    │   Orchestrator    │            │
│                                    └───────────────────┘            │
└──────────────────────────────────────────┬───────────────────────────┘
                                           │
                                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│              UNIVERSAL LIVING MEMORY (Orchestrator)                   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      FastAPI Router                          │    │
│  │  /v1/chat/completions  /v1/connections/*  /health           │    │
│  └──────────────┬──────────────────────┬─────────────┬─────────┘    │
│                 │                      │             │               │
│        ┌────────▼────────┐   ┌────────▼────────┐   ▼               │
│        │   Universal     │   │   Connection    │  Lifecycle         │
│        │    Adapter      │   │    Library      │  Monitor           │
│        └────────┬────────┘   └────────┬────────┘                    │
│                 │                      │                             │
│        ┌────────▼────────┐   ┌────────▼────────┐                    │
│        │  Memory Engine  │   │  Cloud Delta    │                    │
│        │   (Qdrant +     │   │    Engine       │                    │
│        │   FastEmbed)    │   └─────────────────┘                    │
│        └────────┬────────┘                                           │
│                 │                                                    │
│        ┌────────▼──────────────────────────────────┐                │
│        │        Three Symbiotic Libraries          │                │
│        │  ┌──────────┐ ┌──────────┐ ┌──────────┐  │                │
│        │  │   API    │ │ Webhook  │ │   MCP    │  │                │
│        │  │ Library  │ │ Library  │ │ Library  │  │                │
│        │  └────┬─────┘ └────┬─────┘ └────┬─────┘  │                │
│        └───────┼────────────┼────────────┼─────────┘                │
└────────────────┼────────────┼────────────┼──────────────────────────┘
                 │            │            │
        ┌────────▼────┐  ┌────▼────┐  ┌───▼────┐
        │ AI Provider │  │ Webhook │  │  MCP   │
        │   (OpenAI,  │  │ Endpoint│  │ Server │
        │  Anthropic, │  │ (Zapier,│  │ (File, │
        │   Grok)     │  │  Slack) │  │  DB)   │
        └────────┬────┘  └────┬────┘  └───┬────┘
                 │            │            │
                 └────────────┼────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   AI Response /   │
                    │  Webhook Result / │
                    │   MCP Output      │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Memory Storage   │
                    │  (Qdrant Vector)  │
                    └───────────────────┘
```

### Connection Addition Flow

```
User Voice: "Add Together AI at api.together.xyz with bearer token abc123"
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Genesis Studio: Whisper STT                                     │
│ Output: "Add Together AI at api.together.xyz with bearer        │
│          token abc123"                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Genesis Studio: AI Parser (via Orchestrator)                   │
│ Prompt: "Parse this voice command to add an API connection...  │
│          Extract: conn_id, name, base_url, auth_type, etc."    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ AI Response (JSON):                                             │
│ {                                                               │
│   "conn_id": "together_ai",                                     │
│   "name": "Together AI",                                        │
│   "base_url": "https://api.together.xyz/v1",                    │
│   "auth_type": "bearer",                                        │
│   "api_key": "abc123"                                           │
│ }                                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Genesis Studio: Confirmation Dialog                            │
│ "🤖 AI Parsed the following API connection:                     │
│  - conn_id: together_ai                                         │
│  - name: Together AI                                            │
│  - base_url: https://api.together.xyz/v1                        │
│  - auth_type: bearer                                            │
│  ✅ Please review. If correct, click Add."                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼ (User confirms)
┌─────────────────────────────────────────────────────────────────┐
│ POST /v1/connections/api                                        │
│ Body: {parsed JSON + models, capabilities, enabled}            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Orchestrator: ConnectionLibrary.add_api_connection()           │
│ - Load config/api_library.json                                 │
│ - Add new connection                                            │
│ - Save config/api_library.json                                 │
│ - Return success                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Connection Available Immediately (No Restart Required)          │
│ User can now use "together_ai" as provider in chat completions │
└─────────────────────────────────────────────────────────────────┘
```

### Chat Completion Flow

```
User: "Use together_ai to write a poem"
    │
    ▼
POST /v1/chat/completions
Body: {
  "provider": "together_ai",
  "messages": [{"role": "user", "content": "write a poem"}],
  "use_memory": true
}
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. Lifecycle.touch() - Mark activity                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Memory.recall("write a poem") - Retrieve context            │
│    - Embed query with FastEmbed                                │
│    - Search Qdrant for similar past interactions               │
│    - Return top 3 relevant memories                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. UniversalAdapter.chat_completion("together_ai", messages)   │
│    - Load connection from api_library.json                     │
│    - Detect API format (OpenAI-compatible)                     │
│    - Create HTTP client with auth headers                      │
│    - POST to https://api.together.xyz/v1/chat/completions      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. AI Provider Response                                         │
│    {"choices": [{"message": {"content": "Roses are red..."}}]} │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Background Tasks (Async)                                     │
│    a) Memory.memorize("write a poem", "Roses are red...")      │
│       - Embed both query and response                          │
│       - Store in Qdrant                                        │
│    b) UniversalAdapter.trigger_webhooks("completion", payload) │
│       - Find all webhooks subscribed to "completion" event     │
│       - POST payload to each webhook URL                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Return Response to Client                                    │
│    {                                                            │
│      "content": "Roses are red...",                             │
│      "provider": "together_ai",                                 │
│      "memory_injected": true                                    │
│    }                                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## End-to-End Engineering Workflow

### Phase 1: Initial Deployment

**Prerequisites**:
- Docker & Docker Compose installed
- Python 3.11+ installed
- Git installed
- Microphone access (for Studio)

**Steps**:

1. **Clone Repositories**
```bash
git clone https://github.com/brian95240/universal-living-memory.git
git clone https://github.com/brian95240/genesis-studio.git
```

2. **Configure Credentials**
```bash
cd universal-living-memory
cp .env.example .env
```

Edit `.env` and add API keys (retrieve from Vaultwarden):
```bash
POSTGRES_PASSWORD=your_secure_password
GROK_API_KEY=your_grok_key
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key
```

3. **Run Genesis Hardware Discovery**
```bash
python genesis.py
```

Expected output:
```
[GENESIS v1.0.1] Initializing Hardware Discovery...
[INFO] Detected: 8 cores, 16.0GB RAM, GPU: NVIDIA RTX 3090
[✓] .env generated. Storage: /mnt/seagate
[✓] providers.json initialized
[✓] Genesis configuration complete!
```

4. **Launch Infrastructure**
```bash
docker compose up -d
```

Wait for services to be ready:
```bash
# Check orchestrator health
curl http://localhost:8000/health

# Expected response:
{
  "status": "online",
  "version": "1.1.0",
  "connection_stats": {...}
}
```

5. **Install Studio Dependencies**
```bash
cd ../genesis-studio
pip install -r studio/requirements.txt
```

6. **Launch Studio**
```bash
python studio/genesis_studio.py
```

Access at: http://localhost:7860

### Phase 2: Adding Connections

**Method 1: Voice Command**

1. Go to Connections tab → API Connections
2. Click microphone or type:
   > "Add Together AI at api.together.xyz with bearer token abc123 supporting Mixtral model"
3. Click "Parse Voice Command"
4. Review AI-parsed details
5. Confirm or correct manually
6. Click "Add API Connection"

**Method 2: Manual Form**

1. Go to Connections tab → API Connections
2. Fill in fields:
   - Connection ID: `together_ai`
   - Name: `Together AI`
   - Base URL: `https://api.together.xyz/v1`
   - Auth Type: `bearer`
   - API Key: `abc123`
   - Models: `mixtral-8x7b`
3. Click "Add API Connection"

**Method 3: API Call**

```bash
curl -X POST http://localhost:8000/v1/connections/api \
  -H "Content-Type: application/json" \
  -d '{
    "conn_id": "together_ai",
    "name": "Together AI",
    "base_url": "https://api.together.xyz/v1",
    "auth_type": "bearer",
    "api_key_value": "abc123",
    "models": ["mixtral-8x7b"],
    "capabilities": ["chat", "completion"],
    "enabled": true
  }'
```

**Verification**:
```bash
# List all connections
curl http://localhost:8000/v1/connections/api

# Test connection
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "together_ai",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Phase 3: Project Creation

1. Go to Create tab
2. Enter project vision:
   > "Create a Python CLI tool for managing TODO lists with SQLite backend"
3. Select AI provider (e.g., `grok` or `together_ai`)
4. Click "Initialize Swarm"
5. Watch multi-agent workflow:
   - Architect designs structure
   - Engineer generates code
6. Review output in Swarm Log

**Voice Interrupt**:
- Speak during build to interrupt
- System will stop current phase
- Use mute button in noisy environments

### Phase 4: Resource Collapse

**Automatic Collapse**:
- After 30 minutes of inactivity, system self-terminates
- Warning at 24 minutes (80% threshold)
- Graceful shutdown via SIGTERM

**Manual Collapse**:
```bash
# Stop all services
docker compose down

# Unload Whisper in Studio
# Go to Matrix tab → Click "Unload Whisper"
```

**Restart**:
```bash
# Restart orchestrator
docker compose up -d

# Restart studio
python studio/genesis_studio.py
```

### Phase 5: Extension

**Adding New Connection Types** (Future):

1. Create new library file: `config/new_type_library.json`
2. Add methods to `ConnectionLibrary`:
   - `add_new_type(id, config)`
   - `remove_new_type(id)`
   - `list_new_types()`
3. Add endpoints to `main.py`:
   - `POST /v1/connections/new_type`
   - `GET /v1/connections/new_type`
   - `DELETE /v1/connections/new_type/{id}`
4. Add UI tab to `genesis_studio.py`
5. No changes needed to Universal Adapter (auto-adapts)

---

## Symbiosis Library Specifications

### API Connection Library

**Purpose**: Direct API connections to AI models and services

**Storage**: `config/api_library.json`

**Schema**:
```json
{
  "connections": {
    "connection_id": {
      "name": "Human-readable name",
      "base_url": "https://api.example.com/v1",
      "auth_type": "bearer|api_key|custom",
      "api_key_env": "ENV_VAR_NAME",
      "api_key_value": "direct_value",
      "auth_header": "Authorization",
      "auth_prefix": "Bearer",
      "models": ["model-1", "model-2"],
      "capabilities": ["chat", "completion", "embedding"],
      "headers": {"Custom-Header": "value"},
      "enabled": true,
      "added_at": 1234567890.0
    }
  }
}
```

**Field Specifications**:

- `connection_id` (string, required): Unique identifier (lowercase, underscores)
- `name` (string, required): Display name
- `base_url` (string, required): API base URL (with protocol)
- `auth_type` (enum, required): Authentication method
  - `bearer`: Authorization: Bearer {token}
  - `api_key`: x-api-key: {token}
  - `custom`: Custom header with prefix
- `api_key_env` (string, optional): Environment variable name for API key
- `api_key_value` (string, optional): Direct API key value (use with caution)
- `auth_header` (string, optional): Custom auth header name (for `custom` type)
- `auth_prefix` (string, optional): Prefix for auth value (e.g., "Bearer ")
- `models` (array, optional): List of available models
- `capabilities` (array, optional): Supported capabilities
- `headers` (object, optional): Additional HTTP headers
- `enabled` (boolean, required): Enable/disable connection
- `added_at` (float, required): Unix timestamp of creation

**Supported Providers**:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- X.AI (Grok)
- Together AI (Mixtral, Llama)
- Mistral AI
- Cohere
- Replicate
- OpenRouter
- Local (Ollama, LM Studio)
- Any OpenAI-compatible API

**API Operations**:

1. **Add Connection**:
```bash
POST /v1/connections/api
Content-Type: application/json

{
  "conn_id": "string",
  "name": "string",
  "base_url": "string",
  "auth_type": "bearer|api_key|custom",
  "api_key_value": "string",
  "models": ["string"],
  "enabled": true
}
```

2. **List Connections**:
```bash
GET /v1/connections/api?enabled_only=true
```

3. **Remove Connection**:
```bash
DELETE /v1/connections/api/{conn_id}
```

### Webhook Library

**Purpose**: Event-driven integrations for automation

**Storage**: `config/webhook_library.json`

**Schema**:
```json
{
  "webhooks": {
    "webhook_id": {
      "name": "Human-readable name",
      "url": "https://hooks.example.com/webhook",
      "method": "POST|GET|PUT",
      "headers": {"Authorization": "Bearer token"},
      "events": ["completion", "error", "all"],
      "enabled": true,
      "added_at": 1234567890.0
    }
  }
}
```

**Field Specifications**:

- `webhook_id` (string, required): Unique identifier
- `name` (string, required): Display name
- `url` (string, required): Webhook endpoint URL
- `method` (enum, required): HTTP method (POST, GET, PUT)
- `headers` (object, optional): HTTP headers (e.g., auth)
- `events` (array, required): Event types to trigger on
  - `completion`: After successful chat completion
  - `error`: On error
  - `all`: All events
- `enabled` (boolean, required): Enable/disable webhook
- `added_at` (float, required): Unix timestamp of creation

**Event Payload Format**:
```json
{
  "event": "completion",
  "timestamp": 1234567890.0,
  "provider": "together_ai",
  "query": "user query",
  "response": "AI response",
  "metadata": {
    "model": "mixtral-8x7b",
    "memory_injected": true
  }
}
```

**Supported Services**:
- Zapier
- n8n
- Make (Integromat)
- IFTTT
- Slack webhooks
- Discord webhooks
- Custom webhooks

**API Operations**:

1. **Add Webhook**:
```bash
POST /v1/connections/webhook
Content-Type: application/json

{
  "webhook_id": "string",
  "name": "string",
  "url": "string",
  "method": "POST",
  "events": ["completion"],
  "enabled": true
}
```

2. **List Webhooks**:
```bash
GET /v1/connections/webhook?enabled_only=true
```

3. **Remove Webhook**:
```bash
DELETE /v1/connections/webhook/{webhook_id}
```

**Triggering**:
- Automatic: Triggered by orchestrator on events
- Manual: Not exposed (internal only)

### MCP Server Library

**Purpose**: Model Context Protocol integrations for extended capabilities

**Storage**: `config/mcp_library.json`

**Schema**:
```json
{
  "servers": {
    "server_id": {
      "name": "Human-readable name",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
      "capabilities": ["read", "write", "list"],
      "enabled": true,
      "added_at": 1234567890.0
    }
  }
}
```

**Field Specifications**:

- `server_id` (string, required): Unique identifier
- `name` (string, required): Display name
- `command` (string, required): Executable command
- `args` (array, required): Command arguments
- `capabilities` (array, optional): Supported capabilities
- `enabled` (boolean, required): Enable/disable server
- `added_at` (float, required): Unix timestamp of creation

**Supported MCP Servers**:
- @modelcontextprotocol/server-filesystem
- @modelcontextprotocol/server-postgres
- @modelcontextprotocol/server-sqlite
- @modelcontextprotocol/server-github
- Custom MCP servers

**API Operations**:

1. **Add MCP Server**:
```bash
POST /v1/connections/mcp
Content-Type: application/json

{
  "server_id": "string",
  "name": "string",
  "command": "string",
  "args": ["string"],
  "capabilities": ["string"],
  "enabled": true
}
```

2. **List MCP Servers**:
```bash
GET /v1/connections/mcp?enabled_only=true
```

3. **Remove MCP Server**:
```bash
DELETE /v1/connections/mcp/{server_id}
```

**Note**: MCP server invocation is not yet implemented in v1.1.0. The library provides storage and management; execution will be added in future versions.

---

## Voice Command Confirmation Flow

### Overview

Voice commands are parsed by AI, confirmed with user, then executed. This ensures accuracy and prevents errors from misheard commands.

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: User Voice Input                                    │
│ User speaks: "Add Together AI at api.together.xyz with      │
│               bearer token abc123"                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Whisper STT (Speech-to-Text)                        │
│ Model: faster-whisper (distil-large-v3)                     │
│ Output: "Add Together AI at api.together.xyz with bearer    │
│          token abc123"                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: AI Parsing (via Orchestrator)                       │
│ Function: parse_connection_from_voice(voice_input, "api")   │
│                                                             │
│ Prompt to AI:                                               │
│ "Parse this voice command to add an API connection.         │
│  Extract: conn_id, name, base_url, auth_type, api_key,     │
│           models                                            │
│  Voice input: '{voice_input}'                               │
│  Respond ONLY with valid JSON."                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: AI Response (JSON Extraction)                       │
│ Raw response: "Based on your input, here's the JSON:        │
│                {\"conn_id\": \"together_ai\", ...}"          │
│                                                             │
│ Regex extraction: r'\{.*\}'                                 │
│                                                             │
│ Parsed JSON:                                                │
│ {                                                           │
│   "conn_id": "together_ai",                                 │
│   "name": "Together AI",                                    │
│   "base_url": "https://api.together.xyz/v1",                │
│   "auth_type": "bearer",                                    │
│   "api_key": "abc123",                                      │
│   "models": null                                            │
│ }                                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Confirmation Dialog (User Review)                   │
│                                                             │
│ Display in UI:                                              │
│ "🤖 AI Parsed the following API connection:                 │
│                                                             │
│  - conn_id: together_ai                                     │
│  - name: Together AI                                        │
│  - base_url: https://api.together.xyz/v1                    │
│  - auth_type: bearer                                        │
│  - api_key: abc123                                          │
│                                                             │
│  ✅ Please review the details above.                        │
│  ❓ If anything is wrong, correct it manually below."       │
│                                                             │
│ [Manual form fields populated with parsed values]           │
│ [Add API Connection button]                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ (User reviews and confirms)
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Manual Correction (Optional)                        │
│ User can edit any field in the manual form:                 │
│ - Fix spelling errors                                       │
│ - Correct URLs                                              │
│ - Add missing models                                        │
│ - Adjust auth type                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ (User clicks "Add API Connection")
┌─────────────────────────────────────────────────────────────┐
│ Step 7: API Call to Orchestrator                            │
│ POST /v1/connections/api                                    │
│ Body: {                                                     │
│   "conn_id": "together_ai",                                 │
│   "name": "Together AI",                                    │
│   "base_url": "https://api.together.xyz/v1",                │
│   "auth_type": "bearer",                                    │
│   "api_key_value": "abc123",                                │
│   "models": ["mixtral-8x7b"],  # Added by user              │
│   "capabilities": ["chat", "completion"],                   │
│   "enabled": true                                           │
│ }                                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 8: Connection Storage                                  │
│ ConnectionLibrary.add_api_connection("together_ai", config) │
│                                                             │
│ 1. Load config/api_library.json                             │
│ 2. Add/update connection entry                              │
│ 3. Save config/api_library.json                             │
│ 4. Return success response                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 9: Immediate Availability                              │
│ Connection "together_ai" is now available for use:          │
│ - No restart required                                       │
│ - No code changes needed                                    │
│ - Hot-reloaded from JSON                                    │
│                                                             │
│ User can immediately use in chat completions:               │
│ POST /v1/chat/completions                                   │
│ {"provider": "together_ai", ...}                            │
└─────────────────────────────────────────────────────────────┘
```

### Error Handling

**Scenario 1: AI Parsing Fails**
```
User: "Add some AI thing"
AI: Unable to extract sufficient details
UI: "❌ Could not parse voice input. Please use manual form."
```

**Scenario 2: Missing Required Fields**
```
User: "Add Together AI"
AI: {"conn_id": "together_ai", "name": "Together AI", "base_url": null}
UI: "⚠️ Missing base_url. Please provide manually."
```

**Scenario 3: Invalid URL**
```
User: "Add Together AI at together dot xyz"
AI: {"base_url": "together.xyz"}
UI: "⚠️ URL should include protocol (https://). Please correct."
```

### Confirmation Strategies

**1. Full Confirmation** (Default)
- Display all parsed fields
- User reviews and confirms
- Manual correction available

**2. Auto-Confirm** (Future Enhancement)
- If all required fields present and valid
- User can enable "auto-confirm" mode
- Still logs confirmation for audit

**3. Partial Confirmation** (Future Enhancement)
- Only confirm ambiguous fields
- Auto-accept clear fields (e.g., well-formed URLs)

---

## Deployment Instructions

### Prerequisites

**System Requirements**:
- OS: Linux (Ubuntu 22.04+), macOS (12+), Windows (WSL2)
- RAM: 8GB minimum, 16GB recommended
- Disk: 10GB free space
- CPU: 4+ cores recommended
- GPU: Optional (CUDA for faster Whisper)

**Software Requirements**:
- Docker 24.0+
- Docker Compose 2.20+
- Python 3.11+
- Git 2.30+
- ffmpeg (for Studio)

**Network Requirements**:
- Ports 8000 (orchestrator), 7860 (studio) available
- Internet access for AI provider APIs
- Microphone access (for voice input)

### Installation Steps

#### 1. Clone Repositories

```bash
# Create project directory
mkdir -p ~/vertex-genesis
cd ~/vertex-genesis

# Clone repositories
git clone https://github.com/brian95240/universal-living-memory.git
git clone https://github.com/brian95240/genesis-studio.git
```

#### 2. Configure Orchestrator

```bash
cd universal-living-memory

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required Environment Variables**:
```bash
# PostgreSQL
POSTGRES_PASSWORD=your_secure_password_here

# AI Provider API Keys (retrieve from Vaultwarden)
GROK_API_KEY=your_grok_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OPENAI_API_KEY=your_openai_api_key_here
DISABLE_LIFECYCLE=false  # Set to true to disable auto-shutdown
```

#### 3. Run Genesis Hardware Discovery

```bash
python genesis.py
```

**Expected Output**:
```
[GENESIS v1.0.1] Initializing Hardware Discovery...
[INFO] Detected: 8 cores, 16.0GB RAM, GPU: NVIDIA RTX 3090
[✓] .env generated. Storage: /mnt/seagate
[✓] providers.json initialized
[✓] Genesis configuration complete!
```

**Troubleshooting**:
- If GPU not detected: Install PyTorch with CUDA support
- If storage not found: Check `TARGET_VOLUME_LABEL` in genesis.py
- If Python errors: Ensure Python 3.11+ is installed

#### 4. Launch Orchestrator

```bash
# Pull Docker images
docker compose pull

# Start services
docker compose up -d

# Check logs
docker compose logs -f orchestrator
```

**Expected Logs**:
```
orchestrator-1  | INFO:     Started server process [1]
orchestrator-1  | INFO:     Waiting for application startup.
orchestrator-1  | INFO:     Application startup complete.
orchestrator-1  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "online",
  "version": "1.1.0",
  "connection_stats": {
    "api_connections": {"total": 4, "enabled": 4},
    "webhooks": {"total": 1, "enabled": 0},
    "mcp_servers": {"total": 1, "enabled": 0}
  },
  "ram_mb": 256.5,
  "idle_time_seconds": 0.5
}
```

#### 5. Install Studio Dependencies

```bash
cd ../genesis-studio

# Install system dependencies (Linux)
sudo apt-get update && sudo apt-get install -y ffmpeg

# Install system dependencies (macOS)
brew install ffmpeg

# Install Python dependencies
pip3 install -r studio/requirements.txt
```

**Troubleshooting**:
- If torch installation fails: Use CPU-only version
  ```bash
  pip3 install torch --index-url https://download.pytorch.org/whl/cpu
  ```
- If gradio fails: Ensure Python 3.11+
- If faster-whisper fails: Install with `--no-deps` and manually install dependencies

#### 6. Launch Studio

```bash
python studio/genesis_studio.py
```

**Expected Output**:
```
[GENESIS STUDIO v1.1.0] Starting Universal Connection Framework...
[INFO] Orchestrator: http://localhost:8000
Running on local URL:  http://127.0.0.1:7860
```

**Access**:
- Open browser: http://localhost:7860
- Allow microphone access when prompted

#### 7. Verify Installation

**Test 1: Orchestrator Health**
```bash
curl http://localhost:8000/health | jq
```

**Test 2: List Connections**
```bash
curl http://localhost:8000/v1/connections/all | jq
```

**Test 3: Chat Completion**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "grok",
    "messages": [{"role": "user", "content": "Hello!"}]
  }' | jq
```

**Test 4: Studio UI**
- Go to Create tab
- Enter: "Create a hello world Python script"
- Select provider: grok
- Click "Initialize Swarm"
- Verify output in Swarm Log

### Production Deployment

#### Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  orchestrator:
    build: ./orchestrator
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - GROK_API_KEY=${GROK_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DISABLE_LIFECYCLE=true  # Disable auto-shutdown in production
    depends_on:
      - postgres
      - qdrant
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  qdrant:
    image: qdrant/qdrant:v1.7.4
    volumes:
      - qdrant_data:/qdrant/storage
    restart: always

  studio:
    build: ./studio
    ports:
      - "7860:7860"
    environment:
      - ORCHESTRATOR_URL=http://orchestrator:8000
    depends_on:
      - orchestrator
    restart: always

volumes:
  postgres_data:
  qdrant_data:
```

**Deploy**:
```bash
docker compose -f docker-compose.prod.yml up -d
```

#### Kubernetes Deployment (Future)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vertex-orchestrator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vertex-orchestrator
  template:
    metadata:
      labels:
        app: vertex-orchestrator
    spec:
      containers:
      - name: orchestrator
        image: vertex-genesis/orchestrator:1.1.0
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: vertex-secrets
              key: postgres-password
        - name: GROK_API_KEY
          valueFrom:
            secretKeyRef:
              name: vertex-secrets
              key: grok-api-key
```

### Troubleshooting

**Issue 1: Orchestrator won't start**
```bash
# Check logs
docker compose logs orchestrator

# Common causes:
# - Missing environment variables
# - PostgreSQL not ready
# - Port 8000 already in use

# Solutions:
# - Verify .env file
# - Wait for postgres: docker compose logs postgres
# - Change port in docker-compose.yml
```

**Issue 2: Studio can't connect to orchestrator**
```bash
# Check orchestrator health
curl http://localhost:8000/health

# Check Studio environment
echo $ORCHESTRATOR_URL

# Solution:
export ORCHESTRATOR_URL=http://localhost:8000
python studio/genesis_studio.py
```

**Issue 3: Voice input not working**
```bash
# Check microphone permissions in browser
# Check Whisper model download
# Check ffmpeg installation

# Solution:
# - Allow microphone in browser settings
# - Manually download Whisper model:
python -c "from faster_whisper import WhisperModel; WhisperModel('distil-large-v3')"
```

**Issue 4: Memory issues**
```bash
# Check memory usage
docker stats

# Solutions:
# - Reduce DB_MEM_LIMIT in .env
# - Unload Whisper in Studio (Matrix tab)
# - Use smaller Whisper model (medium, small)
```

---

## Extension Points

### Adding New Connection Types

**Example**: Adding a "Database" connection type

**Step 1**: Create library file
```bash
touch config/database_library.json
```

**Step 2**: Add methods to `connection_library.py`
```python
DATABASE_LIBRARY = CONFIG_DIR / "database_library.json"

def add_database(self, db_id: str, config: Dict) -> bool:
    """Add or update a database connection"""
    try:
        library = self._load_library_from_file(DATABASE_LIBRARY)
        if "databases" not in library:
            library["databases"] = {}
        
        config["added_at"] = config.get("added_at", time.time())
        config["enabled"] = config.get("enabled", True)
        library["databases"][db_id] = config
        
        self._save_library_to_file(DATABASE_LIBRARY, library)
        logger.info(f"➕ Database connection added: {db_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to add database: {e}")
        return False
```

**Step 3**: Add endpoints to `main.py`
```python
class DatabaseConfig(BaseModel):
    db_id: str
    name: str
    type: str  # postgres, mysql, sqlite
    host: str
    port: int
    database: str
    username: str
    password: str
    enabled: bool = True

@app.post("/v1/connections/database")
async def add_database(config: DatabaseConfig):
    """Add a new database connection"""
    lifecycle.touch()
    try:
        db_config = config.dict(exclude={"db_id"})
        success = connection_lib.add_database(config.db_id, db_config)
        if success:
            return {"status": "added", "db_id": config.db_id}
        else:
            raise HTTPException(500, detail="Failed to add database")
    except Exception as e:
        raise HTTPException(500, detail=str(e))
```

**Step 4**: Add UI tab to `genesis_studio.py`
```python
with gr.Tab("🗄️ Databases"):
    gr.Markdown("**Voice Command Example:** *'Add PostgreSQL database at localhost port 5432'*")
    
    voice_db_input = gr.Textbox(label="Voice Command")
    voice_db_btn = gr.Button("🎤 Parse Voice Command")
    voice_db_out = gr.Markdown()
    
    # Manual input fields
    with gr.Row():
        db_id = gr.Textbox(label="Database ID")
        db_name = gr.Textbox(label="Name")
    # ... more fields
    
    add_db_btn = gr.Button("➕ Add Database")
    db_result = gr.JSON(label="Result")
    
    voice_db_btn.click(lambda x: voice_add_connection(x, "database"), 
                       inputs=voice_db_input, outputs=voice_db_out)
    add_db_btn.click(add_database_connection, 
                     inputs=[db_id, db_name, ...], outputs=db_result)
```

**Step 5**: No changes needed to Universal Adapter (auto-adapts)

### Adding New AI Provider Formats

**Example**: Adding Cohere API format

**Edit `universal_adapter.py`**:
```python
def _detect_api_format(self, base_url: str) -> str:
    """Detect API format from base URL"""
    if "anthropic.com" in base_url:
        return "anthropic"
    elif "generativelanguage.googleapis.com" in base_url:
        return "google"
    elif "cohere.ai" in base_url:  # NEW
        return "cohere"
    elif "openai.com" in base_url or "x.ai" in base_url:
        return "openai"
    else:
        return "openai"

def _chat_cohere_format(self, conn_id: str, messages: List[Dict], 
                       model: Optional[str], **kwargs) -> str:
    """Cohere API format"""
    # Cohere uses 'message' field instead of 'messages'
    message = messages[-1]["content"]
    
    payload = {
        "model": model or "command-r-plus",
        "message": message,
        **kwargs
    }
    resp = self.call_api(conn_id, "/chat", "POST", payload)
    return resp["text"]
```

### Adding New Webhook Events

**Edit `main.py`**:
```python
# After memory storage
if req.use_memory:
    background_tasks.add_task(memory.memorize, user_query, ai_text)
    
    # Trigger completion webhook
    background_tasks.add_task(
        universal_adapter.trigger_webhooks, 
        "completion", 
        {"provider": req.provider, "query": user_query, "response": ai_text}
    )

# NEW: Trigger custom event
background_tasks.add_task(
    universal_adapter.trigger_webhooks,
    "custom_event_name",
    {"custom": "payload"}
)
```

### Adding New MCP Server Invocation

**Future Enhancement** (not in v1.1.0):

```python
# In universal_adapter.py
def invoke_mcp_server(self, server_id: str, tool: str, args: Dict) -> Any:
    """Invoke an MCP server tool"""
    servers = self.library.list_mcp_servers(enabled_only=True)
    if server_id not in servers:
        raise ValueError(f"MCP server not found: {server_id}")
    
    server = servers[server_id]
    
    # Start MCP server process
    import subprocess
    import json
    
    cmd = [server["command"]] + server["args"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    # Send MCP protocol request
    request = {
        "jsonrpc": "2.0",
        "method": f"tools/{tool}",
        "params": args,
        "id": 1
    }
    proc.stdin.write(json.dumps(request).encode() + b'\n')
    proc.stdin.flush()
    
    # Read response
    response = json.loads(proc.stdout.readline())
    proc.terminate()
    
    return response.get("result")
```

---

## Security & Credentials

### Credential Storage

**Recommended**: Store all credentials in **Vaultwarden** (self-hosted Bitwarden)

**Hierarchy**:
1. Vaultwarden (primary storage)
2. Environment variables (deployment)
3. Runtime injection (temporary connections)

**Never**:
- Hard-code credentials in source code
- Commit credentials to git
- Store credentials in plain text files

### Environment Variables

**Orchestrator** (.env):
```bash
# Database
POSTGRES_PASSWORD=<retrieve_from_vaultwarden>

# AI Providers
GROK_API_KEY=<retrieve_from_vaultwarden>
ANTHROPIC_API_KEY=<retrieve_from_vaultwarden>
GEMINI_API_KEY=<retrieve_from_vaultwarden>
OPENAI_API_KEY=<retrieve_from_vaultwarden>

# System
DISABLE_LIFECYCLE=false
```

**Studio** (.env):
```bash
ORCHESTRATOR_URL=http://localhost:8000
STUDIO_PORT=7860
```

### .gitignore

**Both repositories include**:
```
# Environment
.env
.env.local
.env.production

# Configuration
config/*.json
!config/.gitkeep

# Credentials
*.key
*.pem
*.crt

# Logs
*.log
logs/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/

# Docker
docker-compose.override.yml
```

### API Key Injection Methods

**Method 1**: Environment Variable (Recommended)
```json
{
  "conn_id": "openai",
  "api_key_env": "OPENAI_API_KEY"
}
```

**Method 2**: Runtime Value (Temporary)
```json
{
  "conn_id": "temp_provider",
  "api_key_value": "sk-..."
}
```

**Method 3**: Voice Command (Parsed)
> "Add OpenAI with API key sk-..."

**Security Notes**:
- `api_key_value` is stored in JSON (encrypted filesystem recommended)
- `api_key_env` is more secure (not stored in JSON)
- Voice commands with keys should be used in private environments

### Network Security

**Firewall Rules**:
```bash
# Allow orchestrator (internal only)
ufw allow from 172.16.0.0/12 to any port 8000

# Allow studio (public or internal)
ufw allow 7860/tcp

# Block external access to orchestrator
ufw deny 8000/tcp
```

**Reverse Proxy** (Production):
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name vertex.example.com;
    
    ssl_certificate /etc/ssl/certs/vertex.crt;
    ssl_certificate_key /etc/ssl/private/vertex.key;
    
    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Testing & Validation

### Unit Tests (Future)

```python
# tests/test_connection_library.py
import pytest
from connection_library import ConnectionLibrary

def test_add_api_connection():
    lib = ConnectionLibrary()
    config = {
        "name": "Test API",
        "base_url": "https://api.test.com",
        "auth_type": "bearer",
        "enabled": True
    }
    assert lib.add_api_connection("test_api", config) == True
    
    connections = lib.list_api_connections()
    assert "test_api" in connections
    assert connections["test_api"]["name"] == "Test API"

def test_remove_api_connection():
    lib = ConnectionLibrary()
    lib.add_api_connection("test_api", {...})
    assert lib.remove_api_connection("test_api") == True
    
    connections = lib.list_api_connections()
    assert "test_api" not in connections
```

### Integration Tests

```bash
# tests/integration_test.sh
#!/bin/bash

# Test 1: Health check
echo "Test 1: Health check"
curl -f http://localhost:8000/health || exit 1

# Test 2: Add connection
echo "Test 2: Add connection"
curl -X POST http://localhost:8000/v1/connections/api \
  -H "Content-Type: application/json" \
  -d '{"conn_id": "test", "name": "Test", "base_url": "https://api.test.com", "auth_type": "bearer", "enabled": true}' \
  || exit 1

# Test 3: List connections
echo "Test 3: List connections"
curl -f http://localhost:8000/v1/connections/api | grep "test" || exit 1

# Test 4: Remove connection
echo "Test 4: Remove connection"
curl -X DELETE http://localhost:8000/v1/connections/api/test || exit 1

echo "All tests passed!"
```

### Manual Validation Checklist

**Orchestrator**:
- [ ] Health endpoint responds
- [ ] Can add API connection
- [ ] Can list connections
- [ ] Can remove connection
- [ ] Chat completion works with default provider
- [ ] Chat completion works with added provider
- [ ] Memory stores and recalls interactions
- [ ] Webhooks trigger on events
- [ ] Lifecycle monitor tracks idle time
- [ ] Cloud pricing returns data

**Studio**:
- [ ] UI loads at http://localhost:7860
- [ ] Create tab accepts input
- [ ] Provider dropdown populates
- [ ] Initialize Swarm starts workflow
- [ ] Architect phase completes
- [ ] Engineer phase completes
- [ ] Voice input works (microphone)
- [ ] Mute button toggles state
- [ ] Connections tab loads
- [ ] Voice command parsing works
- [ ] AI confirmation displays
- [ ] Manual forms work
- [ ] Add/Remove/List operations work
- [ ] Matrix tab shows pricing
- [ ] Whisper unload works
- [ ] About tab displays

---

## Appendix

### File Tree (Complete)

```
vertex-genesis/
├── universal-living-memory/
│   ├── config/
│   │   ├── .gitkeep
│   │   ├── api_library.json          [Runtime generated]
│   │   ├── webhook_library.json      [Runtime generated]
│   │   ├── mcp_library.json          [Runtime generated]
│   │   └── providers.json            [Runtime generated]
│   ├── orchestrator/
│   │   ├── Dockerfile
│   │   ├── cloud_delta.py            [421 lines]
│   │   ├── connection_library.py     [421 lines]
│   │   ├── dynamic_manager.py        [158 lines]
│   │   ├── lifecycle.py              [67 lines]
│   │   ├── main.py                   [347 lines]
│   │   ├── memory.py                 [89 lines]
│   │   ├── requirements.txt
│   │   └── universal_adapter.py      [226 lines]
│   ├── scripts/
│   │   └── .gitkeep
│   ├── .env                          [User created]
│   ├── .env.example
│   ├── .gitignore
│   ├── CONTRIBUTING.md
│   ├── LICENSE
│   ├── PRD.md
│   ├── README.md
│   ├── SECURITY.md
│   ├── docker-compose.yml
│   └── genesis.py                    [127 lines]
└── genesis-studio/
    ├── scripts/
    │   └── deploy-symbiotic.ps1
    ├── studio/
    │   ├── genesis_studio.py         [487 lines]
    │   └── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── PRD.md
    ├── README.md
    └── SECURITY.md
```

### Version Matrix

| Component | Version | Purpose |
|-----------|---------|---------|
| **System** |
| Vertex Genesis | 1.1.0 | Overall system version |
| Python | 3.11+ | Runtime environment |
| Docker | 24.0+ | Containerization |
| Docker Compose | 2.20+ | Multi-container orchestration |
| **Orchestrator** |
| FastAPI | 0.104.1 | Web framework |
| Uvicorn | 0.24.0 | ASGI server |
| Pydantic | 2.5.0 | Data validation |
| httpx | 0.25.1 | HTTP client |
| psycopg2-binary | 2.9.9 | PostgreSQL adapter |
| qdrant-client | 1.7.0 | Vector database client |
| fastembed | 0.1.3 | Embedding model |
| psutil | 5.9.6 | System monitoring |
| torch | 2.1.1 | GPU detection |
| PostgreSQL | 16-alpine | Relational database |
| Qdrant | 1.7.4 | Vector database |
| **Studio** |
| Gradio | 4.8.0 | Web UI framework |
| faster-whisper | 0.10.0 | Speech-to-text |
| requests | 2.31.0 | HTTP client |
| torch | 2.1.1 | Whisper backend |
| **Models** |
| Whisper | distil-large-v3 | Speech recognition |
| FastEmbed | bge-small-en-v1.5 | Text embedding |

### Glossary

- **Hyper-Dynamic**: Ability to add/modify/remove connections without code changes or restart
- **Universal**: Compatible with any AI model, tool, or platform
- **Evanescent**: Self-terminating when idle, ephemeral by design
- **Symbiotic**: Three libraries (API, Webhook, MCP) working together organically
- **Collapse**: Resource dehydration when idle (opposite of hydration)
- **TTL**: Time-To-Live, duration before automatic collapse
- **Hot-Reload**: Configuration changes apply immediately without restart
- **MCP**: Model Context Protocol, standard for AI tool integrations
- **Orchestrator**: Core server managing connections and AI interactions
- **Studio**: Client interface for user interaction
- **Genesis**: Hardware discovery and configuration generation script
- **Lifecycle**: Self-termination monitor
- **Cloud Delta**: Spot pricing discovery engine
- **Universal Adapter**: Dynamic connection handler for any API format

---

## Document Metadata

**Version**: 1.1.0  
**Last Updated**: December 26, 2024  
**Authors**: Vertex Genesis Team  
**Status**: Production Ready  
**Maintainer**: brian95240  

**Repositories**:
- Core: https://github.com/brian95240/universal-living-memory
- Studio: https://github.com/brian95240/genesis-studio

**License**: AGPL-3.0 + Commercial Dual License

---

**END OF PRODUCT & ENGINEERING REQUIREMENTS DOCUMENT**
