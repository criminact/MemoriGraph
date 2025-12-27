"""
User service for managing user nodes
"""

from typing import Dict, Any
from graphiti_core import Graphiti
from graphiti_core.nodes import EntityNode

from utils.graph_operations import (
    create_or_get_user_node,
    link_sessions_to_user,
    delete_user_data,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user-related operations"""
    
    def __init__(self, graphiti: Graphiti):
        self.graphiti = graphiti
    
    async def create_or_get_user(
        self,
        user_name: str,
        user_id: str,
    ) -> EntityNode:
        """
        Create or retrieve a user node.
        
        Args:
            user_name: Name of the user
            user_id: Unique identifier for the user
        
        Returns:
            EntityNode: The user entity node
        """
        return await create_or_get_user_node(
            self.graphiti,
            user_name=user_name,
            user_id=user_id,
        )
    
    async def link_user_sessions(
        self,
        user_node: EntityNode,
        user_id: str,
    ) -> int:
        """
        Link all sessions to the user node.
        
        Args:
            user_node: The user entity node
            user_id: The user's ID
        
        Returns:
            int: Number of sessions linked
        """
        return await link_sessions_to_user(
            self.graphiti,
            user_node=user_node,
            user_id=user_id,
        )
    
    async def delete_user(
        self,
        user_id: str,
        neo4j_driver,
    ) -> Dict[str, Any]:
        """
        Delete all data associated with a user.
        
        Args:
            user_id: The user's ID
            neo4j_driver: Neo4j driver instance
        
        Returns:
            Dict with deletion statistics
        """
        return await delete_user_data(
            user_id=user_id,
            neo4j_driver=neo4j_driver,
        )

