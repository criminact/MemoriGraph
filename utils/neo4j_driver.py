"""
Neo4j driver utilities for direct database operations
"""

from neo4j import AsyncGraphDatabase
from app.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class Neo4jDriver:
    """Neo4j driver for direct database operations"""
    
    def __init__(self):
        self._driver = None
    
    async def get_driver(self):
        """Get or create Neo4j driver"""
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_url,
                auth=(settings.neo4j_username, settings.neo4j_password)
            )
            logger.info("Neo4j driver initialized")
        return self._driver
    
    async def close(self):
        """Close Neo4j driver"""
        if self._driver is not None:
            try:
                await self._driver.close()
                logger.info("Neo4j driver closed")
            except Exception as e:
                logger.warning(f"Error closing Neo4j driver: {e}")
            finally:
                self._driver = None


# Global instance
neo4j_driver = Neo4jDriver()


async def get_neo4j_driver() -> Neo4jDriver:
    """FastAPI dependency to get Neo4j driver"""
    return neo4j_driver

