# Dynamic User Profile API Documentation

## Overview

This FastAPI application provides a RESTful API for building and querying dynamic user profiles from therapy session summaries using a knowledge graph.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   └── config.py             # Configuration settings
├── api/
│   └── v1/
│       └── routes/
│           ├── users.py          # User management endpoints
│           ├── sessions.py       # Session management endpoints
│           └── profile.py       # Profile query endpoints
├── models/
│   └── schemas.py            # Pydantic models for requests/responses
├── services/
│   ├── user_service.py       # User business logic
│   ├── session_service.py    # Session business logic
│   └── profile_service.py    # Profile query logic
├── utils/
│   ├── database.py           # Graphiti initialization
│   └── graph_operations.py   # Graph database operations
├── run.py                    # Application runner
└── requirements.txt          # Python dependencies
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (create `.env` file):
```env
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DEBUG=False
LOG_LEVEL=INFO
```

**Log Levels**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

3. Ensure Neo4j is running

## Running the Application

```bash
python run.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### Users

#### Create User
```http
POST /users
Content-Type: application/json

{
  "user_name": "John Doe",
  "user_id": "user_001"
}
```

#### Get User
```http
GET /users/{user_id}
```

#### Delete User
```http
DELETE /users/{user_id}
```

**Warning**: This permanently deletes all data associated with the user:
- User node
- All therapy sessions
- All extracted entities and relationships
- All connections and edges

This operation is irreversible!

### Sessions

#### Add Therapy Session
```http
POST /sessions/{user_id}
Content-Type: application/json

{
  "session_summary": "User discussed feeling overwhelmed at work...",
  "session_date": "2025-01-15T14:00:00Z",
  "session_number": 1
}
```

### Profile Queries

#### Search Profile
```http
POST /profile/search
Content-Type: application/json

{
  "query": "What are the user's core beliefs about themselves?",
  "user_id": "user_001"
}
```

#### Search with Center Node
```http
POST /profile/search/center-node
Content-Type: application/json

{
  "query": "What patterns are related to work anxiety?",
  "center_node_uuid": "uuid-of-center-node",
  "user_id": "user_001"
}
```

## Example Usage

### 1. Create a User

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "Alex",
    "user_id": "user_001"
  }'
```

### 2. Add a Therapy Session

```bash
curl -X POST "http://localhost:8000/api/v1/sessions/user_001" \
  -H "Content-Type: application/json" \
  -d '{
    "session_summary": "User discussed feeling overwhelmed at work. They mentioned that criticism from their manager triggers intense anxiety and self-doubt.",
    "session_date": "2025-01-15T14:00:00Z"
  }'
```

### 3. Query User Profile

```bash
curl -X POST "http://localhost:8000/api/v1/profile/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What triggers anxiety for the user?",
    "user_id": "user_001"
  }'
```

### 4. Delete User Data

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/user_001"
```

**Warning**: This permanently deletes all user data from the graph!

## Architecture

### Layers

1. **API Layer** (`api/routes/`): FastAPI route handlers
2. **Service Layer** (`services/`): Business logic
3. **Data Layer** (`utils/`): Database operations and Graphiti management
4. **Models** (`models/`): Pydantic schemas for validation

### Database Operations

All database-related operations are in the `utils/` folder:
- `database.py`: Graphiti initialization and connection management
- `graph_operations.py`: Graph operations (creating nodes, linking relationships)

### Key Features

- **Modular Structure**: Clear separation of concerns
- **Dependency Injection**: FastAPI dependencies for services
- **Background Tasks**: Session linking happens asynchronously
- **Error Handling**: Proper HTTP exceptions and error responses
- **Type Safety**: Pydantic models for request/response validation

## Development

### Adding New Endpoints

1. Create route handler in `api/v1/routes/`
2. Add service method in `services/` if needed
3. Add Pydantic schemas in `models/schemas.py`
4. Register router in `app/main.py` under the v1 API router

### Adding New Services

1. Create service class in `services/`
2. Add business logic methods
3. Use dependency injection in route handlers

## Testing

### Postman Collection (Recommended)

The easiest way to test the API is using the included Postman collection:

1. Import `Graphiti_User_Profile_API.postman_collection.json`
2. Import `Graphiti_API_Environment.postman_environment.json`
3. Select the environment and start testing

See [POSTMAN_SETUP.md](POSTMAN_SETUP.md) for detailed instructions.

### Other Testing Methods

You can also test the API using:
- Interactive docs at `/docs`
- curl commands (examples below)
- Python requests library

### Example Python Test

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create user
response = requests.post(
    f"{BASE_URL}/users",
    json={"user_name": "Test User", "user_id": "test_001"}
)
print(response.json())
```

### Example cURL Commands

```bash
# Create user
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"user_name": "Test User", "user_id": "test_001"}'

# Add session
curl -X POST "http://localhost:8000/api/v1/sessions/test_001" \
  -H "Content-Type: application/json" \
  -d '{"session_summary": "User discussed work anxiety...", "session_date": "2025-01-15T14:00:00Z"}'

# Search profile
curl -X POST "http://localhost:8000/api/v1/profile/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What triggers anxiety?", "user_id": "test_001"}'
```

