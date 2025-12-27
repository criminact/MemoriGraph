"""
Database initialization and Graphiti setup
"""

from openai import AsyncOpenAI
from graphiti_core import Graphiti
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.llm_client.config import LLMConfig

from app.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class GraphitiManager:
    """Manages Graphiti instance and connections"""
    
    def __init__(self):
        self._graphiti: Graphiti | None = None
        self._openai_client: AsyncOpenAI | None = None
    
    async def initialize(self) -> Graphiti:
        """Initialize and return Graphiti instance"""
        if self._graphiti is None:
            # Initialize OpenAI client
            self._openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            # Create LLM and Embedder clients
            llm_client = OpenAIClient(
                client=self._openai_client,
                config=LLMConfig(
                    model=settings.openai_model,
                    small_model=settings.openai_model
                ),
                reasoning=None,  # Disable reasoning for models that don't support it
            )
            
            embedder_client = OpenAIEmbedder(
                client=self._openai_client,
                config=OpenAIEmbedderConfig(embedding_model=settings.openai_embedding_model)
            )
            
            # Initialize Graphiti
            self._graphiti = Graphiti(
                settings.neo4j_url,
                settings.neo4j_username,
                settings.neo4j_password,
                llm_client=llm_client,
                embedder=embedder_client,
            )
            
            logger.info("Graphiti initialized successfully")
        
        return self._graphiti
    
    async def get_graphiti(self) -> Graphiti:
        """Get or initialize Graphiti instance"""
        if self._graphiti is None:
            return await self.initialize()
        return self._graphiti
    
    async def close(self):
        """Close Graphiti connection"""
        if self._graphiti is not None:
            await self._graphiti.close()
            self._graphiti = None
            logger.info("Graphiti connection closed")


# Global instance
graphiti_manager = GraphitiManager()


async def get_graphiti() -> Graphiti:
    """FastAPI dependency to get Graphiti instance"""
    return await graphiti_manager.get_graphiti()

