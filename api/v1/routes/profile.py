"""
User profile query endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from graphiti_core import Graphiti

from models.schemas import (
    ProfileQuery,
    ProfileQueryResponse,
    CenterNodeQuery,
    ErrorResponse,
)
from services.profile_service import ProfileService
from utils.database import get_graphiti
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/profile", tags=["profile"])


async def get_profile_service(
    graphiti: Graphiti = Depends(get_graphiti),
) -> ProfileService:
    """Dependency to get profile service"""
    return ProfileService(graphiti)


@router.post(
    "/search",
    response_model=ProfileQueryResponse,
    responses={400: {"model": ErrorResponse}},
)
async def search_profile(
    query_data: ProfileQuery,
    profile_service: ProfileService = Depends(get_profile_service),
):
    """
    Search the user's profile using natural language queries.
    
    This endpoint performs hybrid search (semantic + BM25) to find
    relevant insights about the user's psychological profile.
    """
    logger.info(f"Profile search for user {query_data.user_id}: '{query_data.query[:50]}...'")
    try:
        results = await profile_service.search_profile(
            query=query_data.query,
        )
        
        logger.info(f"Profile search completed: {len(results)} results found for user {query_data.user_id}")
        
        return ProfileQueryResponse(
            query=query_data.query,
            results=results,
            count=len(results),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile search failed for user {query_data.user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to search profile: {str(e)}"
        )


@router.post(
    "/search/center-node",
    response_model=ProfileQueryResponse,
    responses={400: {"model": ErrorResponse}},
)
async def search_with_center_node(
    query_data: CenterNodeQuery,
    profile_service: ProfileService = Depends(get_profile_service),
):
    """
    Search the user's profile with center node reranking.
    
    This endpoint uses a center node to rerank results based on
    graph distance, providing more contextually relevant results.
    """
    logger.info(
        f"Center node search for user {query_data.user_id}: "
        f"'{query_data.query[:50]}...' (Center: {query_data.center_node_uuid[:8]}...)"
    )
    try:
        results = await profile_service.search_profile(
            query=query_data.query,
            center_node_uuid=query_data.center_node_uuid,
        )
        
        logger.info(
            f"Center node search completed: {len(results)} results found for user {query_data.user_id}"
        )
        
        return ProfileQueryResponse(
            query=query_data.query,
            results=results,
            count=len(results),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Center node search failed for user {query_data.user_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=400,
            detail=f"Failed to search profile: {str(e)}"
        )

