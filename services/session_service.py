"""
Session service for managing therapy sessions
"""

from datetime import datetime
from graphiti_core import Graphiti

from utils.graph_operations import add_session_to_graph
from utils.logger import get_logger

logger = get_logger(__name__)


class SessionService:
    """Service for session-related operations"""
    
    def __init__(self, graphiti: Graphiti):
        self.graphiti = graphiti
    
    async def add_session(
        self,
        session_summary: str,
        session_date: datetime,
        user_id: str,
        user_name: str,
        session_number: int | None = None,
    ) -> tuple[str, int]:
        """
        Add a therapy session to the knowledge graph.
        
        Args:
            session_summary: Text summary of the therapy session
            session_date: Date/time of the session
            user_id: Unique identifier for the user
            user_name: Name of the user
            session_number: Optional session number (auto-generated if not provided)
        
        Returns:
            tuple: (episode_uuid, session_number)
        """
        # Get the next session number if not provided
        if session_number is None:
            session_number = await self._get_next_session_number(user_id)
        
        episode_uuid = await add_session_to_graph(
            self.graphiti,
            session_summary=session_summary,
            session_date=session_date,
            session_number=session_number,
            user_id=user_id,
            user_name=user_name,
        )
        
        return episode_uuid, session_number
    
    async def _get_next_session_number(self, user_id: str) -> int:
        """
        Get the next session number for a user.
        
        Args:
            user_id: The user's ID
        
        Returns:
            int: Next session number
        """
        try:
            query = """
                MATCH (session:Episodic {group_id: $user_id})
                RETURN count(session) as session_count
            """
            
            records, _, _ = await self.graphiti.driver.execute_query(
                query,
                user_id=user_id,
            )
            
            if records:
                count = records[0].get('session_count', 0)
                return int(count) + 1
            return 1
        except Exception as e:
            logger.warning(f"Could not get session count: {e}")
            return 1

