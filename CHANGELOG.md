# Changelog

All notable changes to MemoriGraph will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release of MemoriGraph
- RESTful API for building and querying dynamic user profiles
- User management endpoints (create, get, delete)
- Session management for adding conversation/session summaries
- Profile search with natural language queries
- Center node search for pattern discovery
- Automatic entity extraction from text using GPT-4
- Relationship mapping between entities
- Semantic search combining vector similarity and BM25
- Knowledge graph storage using Neo4j
- Graphiti integration for knowledge graph operations
- Docker Compose setup for easy deployment
- FastAPI with automatic API documentation
- Comprehensive logging with rotation
- Health check endpoint
- Postman collection for API testing
- Multi-tenant support with user isolation
- Temporal awareness for tracking insights over time

### Technical Details
- Built with FastAPI (Python 3.12+)
- Neo4j 5.15 for graph database
- Graphiti for knowledge graph framework
- OpenAI GPT-4 for entity extraction
- OpenAI text-embedding-3-small for embeddings
- Docker containerization
- Environment-based configuration

### Documentation
- README with setup and usage instructions
- API documentation (API_README.md)
- Architecture documentation (ARCHITECTURE.md)
- Deployment guide (DEPLOYMENT.md)
- Postman setup guide (POSTMAN_SETUP.md)

[1.0.0]: https://github.com/yourusername/memorigraph/releases/tag/v1.0.0

