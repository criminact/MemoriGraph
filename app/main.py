"""
FastAPI application main file
"""

from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from utils.database import graphiti_manager
from utils.neo4j_driver import neo4j_driver
from utils.logger import setup_logging, get_logger
from api.v1.routes import users, sessions, profile

# Setup logging first
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    try:
        logger.info("=" * 60)
        logger.info("Starting application...")
        logger.info(f"Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
        logger.info(f"Log Level: {settings.log_level.upper()}")
        
        logger.info("Initializing Graphiti...")
        await graphiti_manager.initialize()
        logger.info("✓ Graphiti initialized successfully")
        
        logger.info("Initializing Neo4j driver...")
        await neo4j_driver.get_driver()
        logger.info("✓ Neo4j driver initialized successfully")
        
        logger.info("Application startup complete")
        logger.info("=" * 60)
    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    try:
        logger.info("=" * 60)
        logger.info("Shutting down application...")
        
        # Close Graphiti first
        logger.info("Closing Graphiti connection...")
        try:
            await graphiti_manager.close()
            logger.info("✓ Graphiti connection closed")
        except Exception as e:
            logger.warning(f"Error closing Graphiti: {e}")
        
        # Close Neo4j driver
        logger.info("Closing Neo4j driver...")
        try:
            await neo4j_driver.close()
            logger.info("✓ Neo4j driver closed")
        except Exception as e:
            logger.warning(f"Error closing Neo4j driver: {e}")
        
        logger.info("Application shutdown complete")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    MemoriGraph - Knowledge Graph Memory API for AI Applications
    
    Build AI applications with persistent, contextual memory using knowledge graphs.
    
    MemoriGraph enables developers to add sophisticated memory capabilities to their AI applications.
    It transforms unstructured conversations and interactions into a rich knowledge graph that evolves over time.
    
    Features:
    - Create and manage user nodes
    - Add conversations/sessions with automatic entity extraction
    - Query user profiles with natural language
    - Extract insights about relationships, patterns, and context
    - Semantic search across user history
    - Dynamic profile building that evolves over time
    
    Perfect for AI chatbots, therapeutic applications, personalized systems, and any app that needs to "remember" users.
    """,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API version routers
api_v1 = APIRouter(prefix="/api/v1", tags=["v1"])
api_v1.include_router(users.router)
api_v1.include_router(sessions.router)
api_v1.include_router(profile.router)

app.include_router(api_v1)


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}",
        extra={"status_code": exc.status_code, "path": request.url.path}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(
        f"Validation error: {exc.errors()} - Path: {request.url.path}",
        extra={"errors": exc.errors(), "path": request.url.path}
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation error", "details": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(
        f"Unhandled exception: {str(exc)} - Path: {request.url.path}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred" if not settings.debug else str(exc)
        }
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests"""
    import time
    
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} - "
            f"Error: {str(e)} - Time: {process_time:.3f}s",
            exc_info=True
        )
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    logger.debug("Root endpoint accessed")
    return {
        "message": "MemoriGraph - Knowledge Graph Memory API",
        "version": settings.app_version,
        "description": "Build AI applications with persistent, contextual memory",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint accessed")
    try:
        # Check if connections are alive
        graphiti = await graphiti_manager.get_graphiti()
        neo4j = await neo4j_driver.get_driver()
        
        return {
            "status": "healthy",
            "graph-engine": "connected",
            "graph-storage": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

