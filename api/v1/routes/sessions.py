"""
Therapy session management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from graphiti_core import Graphiti

from models.schemas import SessionCreate, SessionResponse, ErrorResponse
from services.session_service import SessionService
from services.user_service import UserService
from utils.database import get_graphiti
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])


async def get_session_service(
    graphiti: Graphiti = Depends(get_graphiti),
) -> SessionService:
    """Dependency to get session service"""
    return SessionService(graphiti)


async def get_user_service(
    graphiti: Graphiti = Depends(get_graphiti),
) -> UserService:
    """Dependency to get user service"""
    return UserService(graphiti)


@router.post(
    "/{user_id}",
    response_model=SessionResponse,
    status_code=201,
    responses={400: {"model": ErrorResponse}},
)
async def create_session(
    user_id: str,
    session_data: SessionCreate,
    background_tasks: BackgroundTasks,
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
):
    """
    Add a therapy session summary to the knowledge graph.
    
    The session will be processed asynchronously to extract entities,
    relationships, and psychological patterns.
    """
    logger.info(f"Adding session for user: {user_id} (Session #{session_data.session_number or 'auto'})")
    try:
        # Get or create user
        # Try to find existing user first
        from graphiti_core.nodes import EntityNode
        
        find_user_query = """
            MATCH (user:Entity {group_id: $group_id})
            WHERE 'User' IN labels(user)
            RETURN user.uuid AS uuid
            LIMIT 1
        """
        
        records, _, _ = await session_service.graphiti.driver.execute_query(
            find_user_query,
            group_id=user_id,
        )
        
        if records:
            user_uuid = records[0]['uuid']
            user_node = await EntityNode.get_by_uuid(session_service.graphiti.driver, user_uuid)
        else:
            # Create new user with default name
            user_node = await user_service.create_or_get_user(
                user_name=f"User_{user_id}",
                user_id=user_id,
            )
        
        # Add session
        episode_uuid, session_number = await session_service.add_session(
            session_summary=session_data.session_summary,
            session_date=session_data.session_date,
            user_id=user_id,
            user_name=user_node.name,
            session_number=session_data.session_number,
        )
        
        # Link session to user in background
        background_tasks.add_task(
            user_service.link_user_sessions,
            user_node=user_node,
            user_id=user_id,
        )
        
        logger.info(
            f"Session added successfully: User {user_id}, Session {session_number}, "
            f"Episode UUID: {episode_uuid}"
        )
        
        return SessionResponse(
            session_id=f"{user_id}_session_{session_number}",
            session_number=session_number,
            session_date=session_data.session_date,
            episode_uuid=episode_uuid,
            message=f"Session {session_number} added successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add session for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to add session: {str(e)}"
        )

