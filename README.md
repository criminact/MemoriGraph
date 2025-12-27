# MemoriGraph

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**Build AI applications with persistent, contextual memory using knowledge graphs.**

MemoriGraph is an open-source API that enables developers to add sophisticated memory capabilities to their AI applications. Built on Neo4j and Graphiti, it transforms unstructured conversations and interactions into a rich knowledge graph that evolves over time.

## 🚀 Why MemoriGraph?

Unlike simple vector databases, MemoriGraph builds a **true knowledge graph** that understands relationships, patterns, and context. Your AI doesn't just retrieve facts—it understands the connections between them.

### Key Differentiators

- **Relationship Understanding**: Models connections between entities, not just similarity
- **Contextual Memory**: Tracks patterns and evolution over time
- **Semantic Search**: Hybrid search combining vector similarity and keyword matching
- **Automatic Extraction**: Uses GPT-4 to extract entities and relationships from text
- **Developer-Friendly**: RESTful API with FastAPI, Docker-ready deployment

## 🎯 Perfect For

- **AI Chatbots & Assistants** - Give your chatbots persistent memory across conversations
- **Therapeutic AI Applications** - Build personalized therapeutic agents with deep user understanding
- **Personalized Recommendation Systems** - Understand user preferences and relationships
- **Customer Support Automation** - Remember customer history and context
- **Any AI App** - That needs to "remember" users and understand their context

## ✨ Features

- **Automatic Entity Extraction**: Extracts people, places, emotions, beliefs, and more from text
- **Relationship Mapping**: Automatically connects entities to build a rich knowledge graph
- **Semantic Search**: Query user profiles with natural language
- **Dynamic Profile Building**: Continuously updates as new data is added
- **Multi-Tenant Support**: Isolated user data with group partitioning
- **Temporal Awareness**: Tracks when insights were discovered and how they evolve
- **RESTful API**: Clean, well-documented API with FastAPI
- **Docker-Ready**: Deploy in minutes with Docker Compose
- **Open Source**: Free, self-hosted, and community-driven

## 🏗️ Architecture

MemoriGraph uses a knowledge graph architecture:

```
Conversations/Text
         ↓
    [Graphiti Processing]
         ↓
   Knowledge Graph (Neo4j)
         ↓
  Dynamic User Profile
         ↓
  Contextual AI Responses
```

### How It Works

1. **Add Conversations**: Send text/conversations via the API
2. **Entity Extraction**: GPT-4 automatically extracts entities and relationships
3. **Graph Building**: Entities are stored in Neo4j with their relationships
4. **Query Memory**: Use natural language to query the knowledge graph
5. **Get Insights**: Receive contextual, relationship-aware responses

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose (recommended)
- Neo4j (included in Docker Compose)
- OpenAI API key

### Docker Deployment (Recommended)

The easiest way to get started:

```bash
# Clone the repository
git clone https://github.com/criminact/memorigraph.git
cd memorigraph

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start all services (API + Neo4j)
docker-compose up -d

# View logs
docker-compose logs -f api
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export NEO4J_URL=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=your_password
export OPENAI_API_KEY=your_openai_api_key

# Run the server
python run.py
```

## 📖 Usage Examples

### 1. Create a User

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "Alex",
    "user_id": "user_001"
  }'
```

### 2. Add a Conversation/Session

```bash
curl -X POST "http://localhost:8000/api/v1/sessions/user_001" \
  -H "Content-Type: application/json" \
  -d '{
    "session_summary": "User discussed feeling overwhelmed at work. They mentioned that criticism from their manager triggers intense anxiety and self-doubt.",
    "session_date": "2025-01-15T14:00:00Z"
  }'
```

### 3. Query User Memory

```bash
curl -X POST "http://localhost:8000/api/v1/profile/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What triggers anxiety for the user?",
    "user_id": "user_001"
  }'
```

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create user
user = requests.post(
    f"{BASE_URL}/users",
    json={"user_name": "Alex", "user_id": "user_001"}
).json()

# Add conversation
session = requests.post(
    f"{BASE_URL}/sessions/user_001",
    json={
        "session_summary": "User discussed work anxiety...",
        "session_date": "2025-01-15T14:00:00Z"
    }
).json()

# Query memory
memory = requests.post(
    f"{BASE_URL}/profile/search",
    json={
        "query": "What are the user's main concerns?",
        "user_id": "user_001"
    }
).json()

print(memory)
```

## 📚 Documentation

- **[API Documentation](API_README.md)** - Complete API reference
- **[Architecture Guide](ARCHITECTURE.md)** - System architecture and design
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions

## 🛠️ Built With

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Neo4j](https://neo4j.com/)** - Graph database
- **[Graphiti](https://github.com/getzep/graphiti)** - Knowledge graph framework
- **[OpenAI](https://openai.com/)** - GPT-4 for entity extraction and embeddings
- **[Docker](https://www.docker.com/)** - Containerization

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Graphiti](https://github.com/getzep/graphiti) for knowledge graph operations
- Inspired by the need for better AI memory systems
- Community-driven development

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/criminact/memorigraph/issues)
- **Discussions**: [GitHub Discussions](https://github.com/criminact/memorigraph/discussions)
- **Documentation**: See the [docs](API_README.md) folder

## 🌟 Use Cases

### Therapeutic AI
Build personalized therapeutic agents that understand user psychology, track progress over time, and provide personalized interventions.

### AI Chatbots
Give your chatbots persistent memory across conversations. Remember user preferences, past interactions, and context to provide more personalized responses.

### Customer Support
Remember customer history, past issues, and preferences to provide better, more contextual support.

### Personalized Systems
Build recommendation systems that understand user relationships, preferences, and patterns over time.

## 🔄 Roadmap

- [ ] Support for additional LLM providers (Anthropic, Cohere, etc.)
- [ ] More query types and search capabilities
- [ ] Performance optimizations
- [ ] Graph visualization tools
- [ ] Batch processing capabilities
- [ ] Export/import functionality
- [ ] Community-driven features

## ⚙️ Configuration

See [API_README.md](API_README.md) for complete configuration options.

Key environment variables:
- `NEO4J_URL` - Neo4j connection URI
- `NEO4J_USERNAME` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `OPENAI_MODEL` - OpenAI model (default: `gpt-4`)
- `OPENAI_EMBEDDING_MODEL` - Embedding model (default: `text-embedding-3-small`)

---

**Made with ❤️ for developers building AI with memory**
