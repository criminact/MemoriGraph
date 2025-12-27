# Deployment Guide

This guide covers deploying the Graph Based Holistic User Profile API using Docker.

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- OpenAI API key

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   cd /path/to/GraphitiUserHolisticProfile
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   # Edit .env and add your configuration
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Check logs**:
   ```bash
   docker-compose logs -f api
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Neo4j Configuration
NEO4J_PASSWORD=your_secure_password_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
```

## Docker Compose Services

### Neo4j Database

- **Image**: `neo4j:5.15-community`
- **Ports**: 
  - 7474 (HTTP/Browser)
  - 7687 (Bolt protocol)
- **Volumes**: Persistent data storage
- **Health Check**: Automatic connection verification

### API Service

- **Port**: 8000
- **Health Check**: `/health` endpoint
- **Logs**: Mounted to `./logs` directory
- **Dependencies**: Waits for Neo4j to be healthy

## Building the Docker Image

To build the image manually:

```bash
docker build -t graphiti-api:latest .
```

## Running Individual Services

### Start only Neo4j:
```bash
docker-compose up -d neo4j
```

### Start only API:
```bash
docker-compose up -d api
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

## Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f neo4j

# Last 100 lines
docker-compose logs --tail=100 api
```

## Accessing Neo4j Browser

1. Open http://localhost:7474
2. Login with:
   - Username: `neo4j`
   - Password: (from your `.env` file)

## Production Deployment

### Security Considerations

1. **Change default passwords**: Use strong passwords in production
2. **Use secrets management**: Consider using Docker secrets or external secret managers
3. **Enable HTTPS**: Use a reverse proxy (nginx, traefik) with SSL certificates
4. **Network security**: Restrict access to Neo4j ports (7687, 7474) to internal network only
5. **Resource limits**: Set appropriate CPU and memory limits

### Example Production docker-compose.yml

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    restart: always
```

### Using with Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

### Health Checks

- API: `GET http://localhost:8000/health`
- Neo4j: Automatically checked by Docker Compose

### Log Files

Application logs are stored in:
- `./logs/app.log` - All logs
- `./logs/error.log` - Errors only

## Troubleshooting

### API won't start

1. Check Neo4j is running: `docker-compose ps`
2. Check API logs: `docker-compose logs api`
3. Verify environment variables: `docker-compose config`

### Neo4j connection issues

1. Verify Neo4j is healthy: `docker-compose ps neo4j`
2. Check Neo4j logs: `docker-compose logs neo4j`
3. Test connection: `docker-compose exec neo4j cypher-shell -u neo4j -p password`

### Port conflicts

If ports 8000, 7474, or 7687 are already in use:

1. Edit `docker-compose.yml` to change port mappings
2. Update `NEO4J_URL` in `.env` if Neo4j port changed

### Data persistence

Data is stored in Docker volumes:
- `neo4j_data` - Database files
- `neo4j_logs` - Neo4j logs
- `neo4j_import` - Import directory

To backup:
```bash
docker run --rm -v graphiti-neo4j_data:/data -v $(pwd):/backup alpine tar czf /backup/neo4j-backup.tar.gz /data
```

## Scaling

To scale the API service:

```bash
docker-compose up -d --scale api=3
```

Note: Ensure your load balancer handles session affinity if needed.

## Updates

To update the application:

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build api
```

## Cleanup

Remove everything (including volumes):

```bash
docker-compose down -v
docker system prune -a
```

⚠️ **Warning**: This will delete all data!

