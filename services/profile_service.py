"""
Profile service for querying user profiles
"""

from typing import List
from graphiti_core import Graphiti

from models.schemas import ProfileResult
from utils.logger import get_logger

logger = get_logger(__name__)


class ProfileService:
    """Service for profile query operations"""
    
    def __init__(self, graphiti: Graphiti):
        self.graphiti = graphiti
    
    async def search_profile(
        self,
        query: str,
        center_node_uuid: str | None = None,
    ) -> List[ProfileResult]:
        """
        Search the user profile.
        
        Args:
            query: Natural language query
            center_node_uuid: Optional center node UUID for reranking
        
        Returns:
            List of ProfileResult objects
        """
        if center_node_uuid:
            results = await self.graphiti.search(
                query,
                center_node_uuid=center_node_uuid,
            )
        else:
            results = await self.graphiti.search(query)
        
        profile_results = []
        for result in results:
            profile_results.append(
                ProfileResult(
                    uuid=result.uuid,
                    fact=result.fact,
                    valid_at=getattr(result, 'valid_at', None),
                    invalid_at=getattr(result, 'invalid_at', None),
                )
            )
        
        return profile_results

