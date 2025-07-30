# Eion Python SDK

Python SDK for Eion - Shared memory storage and collaborative intelligence for AI agent systems.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Cluster Management](#cluster-management)
- [Agent Memory Operations](#agent-memory-operations)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Configuration](#configuration)
- [Features](#features)
- [License](#license)

## Prerequisites

Before using this SDK, you need to have an **Eion server running**. This SDK is a client that connects to your Eion server instance.

### Docker

```bash
# 1. Create a docker-compose.yml file
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  eion-server:
    image: eiondb/eion:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgres://eion:password@postgres:5432/eion
      - CLUSTER_API_KEY=my-secret-api-key-123  # You choose this!
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=eion
      - POSTGRES_USER=eion
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOF

# 2. Start the Eion server
docker-compose up -d

# 3. Verify it's running
curl http://localhost:8080/health
```

## Installation

```bash
pip install eiondb
```

Or install from source:
```bash
git clone https://github.com/eiondb/eion-sdk-python.git
cd eion-sdk-python
pip install -e .
```

## Quick Start

### 1. Setup Eion Server (One-time)

```python
from eiondb import EionClient

# Setup server infrastructure (downloads ~3GB on first run)
client = EionClient()
client.setup()  # Downloads Docker images, Python packages, AI models
```

### 2. Run the Server

```python
# Option A: Run in background (recommended for development)
client.run(detached=True)

# Option B: Run in foreground (blocks terminal)
client.run()  # Press Ctrl+C to stop
```

### 3. Use Cluster Management

```python
# Create users and agents
client.create_user("user1", "John Doe")
client.register_agent("agent1", "Assistant", permission="crud")
client.create_session("session1", "user1")

# Check server health
if client.server_health():
    print("✅ Server is ready!")
```

### 4. Agent Memory Operations

Agents use HTTP endpoints directly for memory operations:

```bash
# Agent stores memory
curl -X POST "http://localhost:8080/sessions/v1/session1/memories?agent_id=agent1&user_id=user1" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "I like pizza"}]}'

# Agent retrieves shared memory  
curl "http://localhost:8080/sessions/v1/session1/memories?agent_id=agent1&user_id=user1&last_n=10"

# Agent searches knowledge
curl "http://localhost:8080/sessions/v1/session1/memories/search?agent_id=agent1&user_id=user1&query=pizza"
```

## Cluster Management

The SDK provides cluster-level management for developers:

### User Management

```python
# Create user
user = client.create_user(
    user_id="user123",
    name="John Doe"  # Optional
)

# Delete user
client.delete_user("user123")
```

### Agent Management

```python
# Register agent
agent = client.register_agent(
    agent_id="agent123",
    name="Assistant Agent",
    permission="crud",  # c=create, r=read, u=update, d=delete
    description="AI assistant for customer support"
)

# Update agent
client.update_agent("agent123", "permission", "r")

# Delete agent  
client.delete_agent("agent123")

# List agents
agents = client.list_agents()
```

### Session Management

```python
# Create session
session = client.create_session(
    session_id="session123",
    user_id="user123",
    session_name="Support Chat"  # Optional
)

# Delete session
client.delete_session("session123")
```

### Agent Groups

```python
# Create agent group
group = client.register_agent_group(
    group_id="support_team",
    name="Support Team",
    agent_ids=["agent1", "agent2"],
    description="Customer support agents"
)

# Update group
client.update_agent_group("support_team", "agent_ids", ["agent1", "agent2", "agent3"])
```

## Agent Memory Operations

**Important**: Agents use HTTP endpoints directly, not Python SDK methods.

### Memory Storage

```bash
# Store conversation memory with automatic knowledge extraction
curl -X POST "http://localhost:8080/sessions/v1/{session_id}/memories?agent_id={agent_id}&user_id={user_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I want to order pizza"},
      {"role": "assistant", "content": "What toppings would you like?"}
    ]
  }'
```

### Memory Retrieval

```bash
# Get recent conversation history
curl "http://localhost:8080/sessions/v1/{session_id}/memories?agent_id={agent_id}&user_id={user_id}&last_n=20"
```

### Knowledge Search

```bash
# Search shared knowledge across agents
curl "http://localhost:8080/sessions/v1/{session_id}/memories/search?agent_id={agent_id}&user_id={user_id}&query=pizza+order"
```

### Multi-Agent Memory Sharing

All agents in the same session share memory and knowledge:

```python
# Setup shared session
client.create_session("shared_session", "user1")

# Agent 1 stores memory → automatically shared
# Agent 2 can retrieve Agent 1's memory
# Agent 3 can search across all agents' knowledge
```

## API Reference

### EionClient

#### Server Management
- `setup(force_reset=False)` - Setup server infrastructure
- `run(detached=False)` - Run the server
- `stop()` - Stop the server  
- `reset()` - Reset to clean state
- `server_health()` - Check server health

#### Cluster Management
- `create_user(user_id, name=None)`
- `delete_user(user_id)`
- `register_agent(agent_id, name, permission='r', description=None)`
- `update_agent(agent_id, field, value)`
- `delete_agent(agent_id)`
- `list_agents(permission=None)`
- `create_session(session_id, user_id, session_name=None)`
- `delete_session(session_id)`
- `register_agent_group(group_id, name, agent_ids=[], description=None)`

## Configuration

### Default Configuration

On first setup, `eion.yaml` is created with defaults:

```yaml
common:
  http:
    host: "0.0.0.0" 
    port: 8080
  postgres:
    user: "eion"
    password: "eion_pass"
    host: "localhost"
    port: 5432
    database: "eion"
  neo4j:
    uri: "bolt://localhost:7687"
    username: "neo4j"
    password: "password"
```

### Custom Configuration

Edit `eion.yaml` to customize:

```yaml
common:
  http:
    port: 8090  # Change server port
  postgres:
    password: "my_secure_password"  # Change database password
```

### Environment Variables

```bash
export EION_CLUSTER_API_KEY="your-secret-key"
export EION_BASE_URL="http://localhost:8080"
```

## Troubleshooting

### Setup Issues

**"Docker not found"**
```bash
# Install Docker Desktop
# macOS: brew install --cask docker
# Or download from https://docker.com
```

**"Port 8080 already in use"**
```bash
# Find process using port
lsof -i :8080

# Kill process or change port in eion.yaml
```

**"Insufficient disk space"**
- Need at least 3GB free space for all dependencies

### Runtime Issues

**"Server not responding"**
```python
# Check if server is running
client.server_health()

# Restart server
client.stop()
client.run(detached=True)
```

**"Authentication failed"**
- Make sure `cluster_api_key` is set correctly
- Check `eion.yaml` configuration

### Reset and Clean Start

```python
# Complete reset
client.reset()
client.setup()
client.run(detached=True)
```

## System Requirements

- **Python**: 3.7 or higher
- **Docker**: Latest version with Docker Compose
- **Disk Space**: 3GB free space
- **Memory**: 4GB RAM recommended
- **Ports**: 5432, 7474, 7687, 8080 available

## Architecture

Eion provides:

- **🗄️ PostgreSQL + pgvector**: Message storage and vector search
- **🕸️ Neo4j + APOC**: Knowledge graph with temporal reasoning  
- **🤖 Real Embeddings**: `all-MiniLM-L6-v2` model (384 dimensions)
- **🧠 Knowledge Extraction**: Automatic entity/relationship extraction
- **⚡ Multi-Agent Memory**: Shared memory across agent sessions
- **🔄 Conflict Resolution**: Automatic temporal conflict handling

## Features

- **Cluster Management**: User, agent, and session management
- **Agent Registration**: Register and manage AI agents with permissions
- **Session Management**: Create and manage conversation sessions
- **Agent Groups**: Organize agents into teams
- **Session Types**: Define session templates with agent group assignments
- **Monitoring & Analytics**: Track agent performance and collaboration
- **Health Checks**: Monitor system health and connectivity
- **Structured Error Handling**: Comprehensive exception types
- **Authentication**: Multiple authentication methods
- **Type Hints**: Full type annotation support

## Documentation

- **Full API Documentation**: [docs/openapi.yaml](docs/openapi.yaml)
- **Agent API Guide**: [docs/agent-api-guide.json](docs/agent-api-guide.json)
- **Examples**: [example/](example/)

## Support

- **Issues**: [GitHub Issues](https://github.com/eiondb/eion-sdk-python/issues)

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details.

---

Happy building with Eion! 🚀 