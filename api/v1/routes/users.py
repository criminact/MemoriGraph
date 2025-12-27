"""
User management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from graphiti_core import Graphiti
from graphiti_core.helpers import parse_db_date

from models.schemas import UserCreate, UserResponse, ErrorResponse, DeleteUserResponse
from services.user_service import UserService
from utils.database import get_graphiti
from utils.neo4j_driver import get_neo4j_driver, Neo4jDriver
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


async def get_user_service(
    graphiti: Graphiti = Depends(get_graphiti),
) -> UserService:
    """Dependency to get user service"""
    return UserService(graphiti)


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    responses={400: {"model": ErrorResponse}},
)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    """
    Create or retrieve a user node in the knowledge graph.
    
    This endpoint creates a User node that serves as the parent for all
    therapy sessions and extracted entities.
    """
    logger.info(f"Creating/retrieving user: {user_data.user_id} ({user_data.user_name})")
    try:
        user_node = await user_service.create_or_get_user(
            user_name=user_data.user_name,
            user_id=user_data.user_id,
        )
        
        logger.info(f"User created/retrieved successfully: {user_data.user_id} (UUID: {user_node.uuid})")
        
        return UserResponse(
            user_id=user_data.user_id,
            user_name=user_data.user_name,
            uuid=user_node.uuid,
            created_at=user_node.created_at,
            summary=user_node.summary,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user {user_data.user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    graphiti: Graphiti = Depends(get_graphiti),
):
    """
    Get user information by user_id.
    """
    logger.info(f"Retrieving user: {user_id}")
    try:
        # Try to find existing user node
        # In Neo4j, labels are node labels, not properties - use labels() function
        find_user_query = """
            MATCH (user:Entity {group_id: $group_id})
            WHERE 'User' IN labels(user)
            RETURN user.uuid AS uuid, user.name AS name, labels(user) AS labels,
                   user.created_at AS created_at, user.summary AS summary
            LIMIT 1
        """
        
        records, _, _ = await graphiti.driver.execute_query(
            find_user_query,
            group_id=user_id,
        )
        
        if not records:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )
        
        record = records[0]
        logger.info(f"User retrieved successfully: {user_id}")
        
        # Convert Neo4j DateTime to Python datetime using Graphiti's helper
        created_at = parse_db_date(record.get('created_at'))
        
        return UserResponse(
            user_id=user_id,
            user_name=record.get('name', 'Unknown'),
            uuid=record.get('uuid'),
            created_at=created_at,
            summary=record.get('summary'),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=404,
            detail=f"User not found: {str(e)}"
        )


@router.delete(
    "/{user_id}",
    response_model=DeleteUserResponse,
    status_code=200,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    neo4j_driver: Neo4jDriver = Depends(get_neo4j_driver),
):
    """
    Delete all data associated with a user from the knowledge graph.
    
    This endpoint permanently deletes:
    - The User node
    - All therapy sessions (Episodic nodes)
    - All extracted entities and relationships
    - All connections and edges
    
    **Warning**: This operation is irreversible!
    """
    logger.warning(f"DELETE request for user: {user_id} - This will permanently delete all user data")
    try:
        result = await user_service.delete_user(
            user_id=user_id,
            neo4j_driver=neo4j_driver,
        )
        
        if result["status"] == "no_data_found":
            logger.warning(f"No data found to delete for user: {user_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No data found for user {user_id}"
            )
        
        logger.info(
            f"User data deleted successfully: {user_id} - "
            f"Nodes: {result['deleted_nodes']}, Relationships: {result['deleted_relationships']}"
        )
        
        return DeleteUserResponse(
            user_id=result["user_id"],
            deleted_nodes=result["deleted_nodes"],
            deleted_relationships=result["deleted_relationships"],
            status=result["status"],
            message=f"Successfully deleted all data for user {user_id}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user data for {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete user data: {str(e)}"
        )

