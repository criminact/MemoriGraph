# Architecture Overview

**This document provides a comprehensive view of the Graphiti User Profile API architecture.**

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        CLIENT[Client Applications<br/>Postman, Web Apps, etc.]
    end

    subgraph "API Gateway Layer"
        FASTAPI[FastAPI Application<br/>app/main.py]
        MIDDLEWARE[CORS Middleware<br/>Request Logging<br/>Exception Handlers]
        VERSIONING[API Versioning<br/>/api/v1]
    end

    subgraph "API Routes Layer (v1)"
        USER_ROUTES[Users Routes<br/>POST /users<br/>GET /users/id<br/>DELETE /users/id]
        SESSION_ROUTES[Sessions Routes<br/>POST /sessions/user_id]
        PROFILE_ROUTES[Profile Routes<br/>POST /profile/search<br/>POST /profile/search/center-node]
    end

    subgraph "Service Layer"
        USER_SERVICE[UserService<br/>- create_or_get_user<br/>- link_user_sessions<br/>- delete_user]
        SESSION_SERVICE[SessionService<br/>- add_session<br/>- _get_next_session_number]
        PROFILE_SERVICE[ProfileService<br/>- search_profile]
    end

    subgraph "Graph Operations Layer"
        GRAPH_OPS[Graph Operations<br/>- create_or_get_user_node<br/>- add_session_to_graph<br/>- link_sessions_to_user<br/>- delete_user_data]
    end

    subgraph "Knowledge Graph Framework"
        GRAPHITI[Graphiti Core<br/>- Entity Extraction<br/>- Relationship Mapping<br/>- Semantic Search]
        GRAPHITI_DRIVER[Graphiti Driver<br/>Cypher Query Interface]
    end

    subgraph "External AI Services"
        OPENAI_LLM[OpenAI GPT-4<br/>LLM for Entity Extraction]
        OPENAI_EMBED[OpenAI Embeddings<br/>text-embedding-3-small<br/>Semantic Search]
    end

    subgraph "Database Layer"
        NEO4J[(Neo4j Graph Database<br/>- User Nodes<br/>- Session Nodes<br/>- Entity Nodes<br/>- Relationships)]
        NEO4J_DRIVER[Neo4j Driver<br/>Direct Cypher Queries]
    end

    subgraph "Utilities"
        LOGGER[Logger<br/>- Console Output<br/>- File Rotation<br/>- Error Logging]
        CONFIG[Configuration<br/>Environment Variables<br/>Settings Management]
    end

    %% Client to API
    CLIENT -->|HTTP Requests| FASTAPI
    FASTAPI --> MIDDLEWARE
    MIDDLEWARE --> VERSIONING

    %% API Routes
    VERSIONING --> USER_ROUTES
    VERSIONING --> SESSION_ROUTES
    VERSIONING --> PROFILE_ROUTES

    %% Routes to Services
    USER_ROUTES --> USER_SERVICE
    SESSION_ROUTES --> SESSION_SERVICE
    PROFILE_ROUTES --> PROFILE_SERVICE

    %% Services to Graph Operations
    USER_SERVICE --> GRAPH_OPS
    SESSION_SERVICE --> GRAPH_OPS
    PROFILE_SERVICE --> GRAPHITI

    %% Graph Operations to Graphiti
    GRAPH_OPS --> GRAPHITI
    GRAPH_OPS --> NEO4J_DRIVER

    %% Graphiti to External Services
    GRAPHITI --> OPENAI_LLM
    GRAPHITI --> OPENAI_EMBED
    GRAPHITI --> GRAPHITI_DRIVER

    %% Drivers to Database
    GRAPHITI_DRIVER --> NEO4J
    NEO4J_DRIVER --> NEO4J

    %% Utilities
    FASTAPI --> LOGGER
    FASTAPI --> CONFIG
    USER_SERVICE --> LOGGER
    SESSION_SERVICE --> LOGGER
    PROFILE_SERVICE --> LOGGER
    GRAPH_OPS --> LOGGER

    style FASTAPI fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style NEO4J fill:#008CC1,stroke:#006699,color:#fff
    style GRAPHITI fill:#FF6B6B,stroke:#CC5555,color:#fff
    style OPENAI_LLM fill:#10A37F,stroke:#0D8A6B,color:#fff
    style OPENAI_EMBED fill:#10A37F,stroke:#0D8A6B,color:#fff
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant UserService
    participant GraphOps
    participant Graphiti
    participant OpenAI
    participant Neo4j

    Note over Client,Neo4j: User Creation Flow
    Client->>FastAPI: POST /api/v1/users
    FastAPI->>UserService: create_or_get_user()
    UserService->>GraphOps: create_or_get_user_node()
    GraphOps->>Neo4j: Query: Find existing user
    Neo4j-->>GraphOps: User node - if exists
    alt User not found
        GraphOps->>Graphiti: Create EntityNode
        Graphiti->>OpenAI: Generate embedding
        OpenAI-->>Graphiti: Embedding vector
        Graphiti->>Neo4j: Save User node
        Neo4j-->>Graphiti: User created
    end
    GraphOps-->>UserService: User node
    UserService-->>FastAPI: UserResponse
    FastAPI-->>Client: 201 Created

    Note over Client,Neo4j: Session Addition Flow
    Client->>FastAPI: POST /api/v1/sessions/{user_id}
    FastAPI->>SessionService: add_session()
    SessionService->>GraphOps: add_session_to_graph()
    GraphOps->>Graphiti: add_episode()
    Graphiti->>OpenAI: Extract entities & relationships
    OpenAI-->>Graphiti: Entities, Relationships
    Graphiti->>Neo4j: Save Episode + Entities + Relationships
    Neo4j-->>Graphiti: Episode UUID
    GraphOps->>GraphOps: link_sessions_to_user()
    GraphOps->>Neo4j: Create HAS_SESSION relationship
    Neo4j-->>GraphOps: Relationship created
    GraphOps-->>SessionService: Episode UUID, Session Number
    SessionService-->>FastAPI: SessionResponse
    FastAPI-->>Client: 201 Created

    Note over Client,Neo4j: Profile Search Flow
    Client->>FastAPI: POST /api/v1/profile/search
    FastAPI->>ProfileService: search_profile()
    ProfileService->>Graphiti: search - query, user_id
    Graphiti->>OpenAI: Generate query embedding
    OpenAI-->>Graphiti: Query embedding
    Graphiti->>Neo4j: Hybrid Search - Semantic + BM25
    Neo4j-->>Graphiti: Matching facts/entities
    Graphiti-->>ProfileService: Search results
    ProfileService-->>FastAPI: ProfileQueryResponse
    FastAPI-->>Client: 200 OK with results
```

## Knowledge Graph Structure

```mermaid
graph LR
    subgraph "User-Centric Knowledge Graph"
        USER[User Node<br/>Labels: User, Person, Entity<br/>Properties: name, user_id, summary]
        
        SESSION1[Session 1<br/>Episode Node<br/>Properties: session_number, date]
        SESSION2[Session 2<br/>Episode Node<br/>Properties: session_number, date]
        SESSION3[Session N<br/>Episode Node<br/>Properties: session_number, date]
        
        ENTITY1[Entity: Manager<br/>Labels: Person, Entity]
        ENTITY2[Entity: Anxiety<br/>Labels: Emotion, Entity]
        ENTITY3[Entity: Work<br/>Labels: Context, Entity]
        ENTITY4[Entity: Sister Sarah<br/>Labels: Person, Family, Entity]
        ENTITY5[Entity: Father<br/>Labels: Person, Family, Entity]
        
        BELIEF1[Core Belief<br/>I am not good enough]
        TRIGGER1[Trigger<br/>Criticism from manager]
        COPING1[Coping Mechanism<br/>Withdrawal and overwork]
        
        USER -->|HAS_SESSION| SESSION1
        USER -->|HAS_SESSION| SESSION2
        USER -->|HAS_SESSION| SESSION3
        
        SESSION1 -->|MENTIONS| ENTITY1
        SESSION1 -->|MENTIONS| ENTITY2
        SESSION1 -->|MENTIONS| ENTITY3
        
        ENTITY1 -->|TRIGGERS| ENTITY2
        ENTITY2 -->|RELATES_TO| BELIEF1
        ENTITY1 -->|CAUSES| TRIGGER1
        ENTITY2 -->|MANAGED_BY| COPING1
        
        USER -->|HAS_RELATIONSHIP| ENTITY4
        USER -->|HAS_RELATIONSHIP| ENTITY5
        ENTITY4 -->|SUPPORTIVE| USER
        ENTITY5 -->|CRITICAL| USER
        
        SESSION2 -->|MENTIONS| ENTITY4
        SESSION2 -->|MENTIONS| ENTITY5
    end

    style USER fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style SESSION1 fill:#FF6B6B,stroke:#CC5555,color:#fff
    style SESSION2 fill:#FF6B6B,stroke:#CC5555,color:#fff
    style SESSION3 fill:#FF6B6B,stroke:#CC5555,color:#fff
    style ENTITY1 fill:#95E1D3,stroke:#6BB8A8,color:#000
    style ENTITY2 fill:#95E1D3,stroke:#6BB8A8,color:#000
    style ENTITY3 fill:#95E1D3,stroke:#6BB8A8,color:#000
    style ENTITY4 fill:#95E1D3,stroke:#6BB8A8,color:#000
    style ENTITY5 fill:#95E1D3,stroke:#6BB8A8,color:#000
    style BELIEF1 fill:#F38181,stroke:#CC6666,color:#fff
    style TRIGGER1 fill:#F38181,stroke:#CC6666,color:#fff
    style COPING1 fill:#F38181,stroke:#CC6666,color:#fff
```

## Component Interaction Diagram

```mermaid
graph TB
    subgraph "Request Processing"
        REQ[HTTP Request]
        VALIDATE[Request Validation<br/>Pydantic Models]
        AUTH[Authentication<br/>Future: API Keys]
    end

    subgraph "Business Logic"
        USER_LOGIC[User Management Logic]
        SESSION_LOGIC[Session Processing Logic]
        PROFILE_LOGIC[Profile Query Logic]
    end

    subgraph "Data Processing"
        ENTITY_EXTRACTION[Entity Extraction<br/>Using GPT-4]
        RELATIONSHIP_MAPPING[Relationship Mapping<br/>Using GPT-4]
        EMBEDDING_GEN[Embedding Generation<br/>text-embedding-3-small]
    end

    subgraph "Storage"
        GRAPH_STORAGE[Graph Storage<br/>Neo4j]
        INDEX[Vector Index<br/>Semantic Search]
    end

    subgraph "Response"
        RESP[HTTP Response<br/>JSON]
        ERROR_HANDLING[Error Handling<br/>Exception Mapping]
    end

    REQ --> VALIDATE
    VALIDATE --> AUTH
    AUTH --> USER_LOGIC
    AUTH --> SESSION_LOGIC
    AUTH --> PROFILE_LOGIC

    USER_LOGIC --> GRAPH_STORAGE
    SESSION_LOGIC --> ENTITY_EXTRACTION
    ENTITY_EXTRACTION --> RELATIONSHIP_MAPPING
    RELATIONSHIP_MAPPING --> EMBEDDING_GEN
    EMBEDDING_GEN --> GRAPH_STORAGE
    EMBEDDING_GEN --> INDEX

    PROFILE_LOGIC --> INDEX
    INDEX --> GRAPH_STORAGE

    USER_LOGIC --> RESP
    SESSION_LOGIC --> RESP
    PROFILE_LOGIC --> RESP
    ERROR_HANDLING --> RESP

    style REQ fill:#E8F4F8,stroke:#4A90E2
    style RESP fill:#E8F4F8,stroke:#4A90E2
    style GRAPH_STORAGE fill:#FFE8E8,stroke:#FF6B6B
    style INDEX fill:#E8F8E8,stroke:#10A37F
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Docker Compose Environment"
        subgraph "API Container"
            API[FastAPI Application<br/>Port: 8000]
            API_LOGS[Logs Volume<br/>./logs]
            API_ENV[Environment Variables<br/>.env file]
        end

        subgraph "Neo4j Container"
            NEO4J[Neo4j Database<br/>Ports: 7474, 7687]
            NEO4J_DATA[Data Volume<br/>neo4j_data]
            NEO4J_LOGS[Logs Volume<br/>neo4j_logs]
            NEO4J_IMPORT[Import Volume<br/>neo4j_import]
        end

        subgraph "Network"
            NETWORK[graphiti-network<br/>Bridge Network]
        end
    end

    subgraph "External Services"
        OPENAI_API[OpenAI API<br/>Cloud Service]
    end

    subgraph "Client Access"
        CLIENT[Client Applications<br/>localhost:8000]
        BROWSER[Browser<br/>localhost:8000/docs]
    end

    API -->|Queries| NEO4J
    API -->|API Calls| OPENAI_API
    API -->|Writes| API_LOGS
    API -->|Reads| API_ENV

    NEO4J -->|Stores| NEO4J_DATA
    NEO4J -->|Writes| NEO4J_LOGS
    NEO4J -->|Imports| NEO4J_IMPORT

    API -.->|Network| NETWORK
    NEO4J -.->|Network| NETWORK

    CLIENT -->|HTTP| API
    BROWSER -->|HTTP| API

    style API fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style NEO4J fill:#008CC1,stroke:#006699,color:#fff
    style OPENAI_API fill:#10A37F,stroke:#0D8A6B,color:#fff
    style NETWORK fill:#F5F5F5,stroke:#999
```

## Key Features

### 1. User-Centric Architecture

- All data is scoped to a user via `**group_id**`
- User node serves as the parent for all sessions and entities
- Enables multi-tenant isolation

### 2. Knowledge Graph Structure

- **User Node**: Central parent node
- **Session Nodes (Episodes)**: Therapy session summaries
- **Entity Nodes**: Extracted people, places, emotions, beliefs
- **Relationship Edges**: Connections between entities

### 3. AI-Powered Extraction

- **GPT-4**: Extracts entities and relationships from session summaries
- **Embeddings**: Enables semantic search across the knowledge graph
- **Hybrid Search**: Combines semantic (vector) and keyword (BM25) search

### 4. Therapeutic Profile Components

- **Personality Traits**: Inferred characteristics
- **Core Beliefs & Schemas**: Deep-seated beliefs
- **Relational Dynamics**: Key relationships
- **Triggers & Vulnerabilities**: Emotional triggers
- **Coping Mechanisms**: Strategies and strengths

### 5. API Design

- RESTful endpoints
- Versioned API (`/api/v1`)
- Comprehensive error handling
- Request/response logging
- Health check endpoints

### 6. Production Ready

- Docker containerization
- Environment-based configuration
- Centralized logging with rotation
- Graceful error handling
- Health checks

### 7. Technology Stack

- **Framework**: FastAPI (Python 3.12)
- **Database**: Neo4j 5.15 (Graph Database)
- **Knowledge Graph**: Graphiti Core
- **AI Services**: OpenAI (GPT-4, text-embedding-3-small)
- **Validation**: Pydantic
- **Deployment**: Docker & Docker Compose
- **Logging**: Python logging with rotation