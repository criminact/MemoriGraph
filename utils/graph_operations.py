"""
Graph operations and database utilities
"""

from datetime import datetime
from typing import Dict, Any
from graphiti_core import Graphiti
from graphiti_core.nodes import EntityNode, EpisodeType

from utils.logger import get_logger

logger = get_logger(__name__)


async def create_or_get_user_node(
    graphiti: Graphiti,
    user_name: str,
    user_id: str,
) -> EntityNode:
    """
    Create or retrieve the User node that serves as the parent for all sessions.
    
    Args:
        graphiti: The Graphiti instance
        user_name: Name of the user
        user_id: Unique identifier for the user (used as group_id)
    
    Returns:
        EntityNode: The User entity node
    """
    group_id = user_id
    
    # Try to find existing User node
    try:
        find_user_query = """
            MATCH (user:Entity {group_id: $group_id})
            WHERE 'User' IN labels(user) OR user.name = $user_name
            RETURN user.uuid AS uuid, user.name AS name, labels(user) AS labels
            LIMIT 1
        """
        
        records, _, _ = await graphiti.driver.execute_query(
            find_user_query,
            group_id=group_id,
            user_name=user_name,
        )
        
        if records:
            user_uuid = records[0]['uuid']
            user_node = await EntityNode.get_by_uuid(graphiti.driver, user_uuid)
            logger.info(f"Retrieved existing User node: {user_name} (UUID: {user_node.uuid})")
            return user_node
    except Exception as e:
        logger.debug(f"Could not find existing user node: {e}")
    
    # Create new User entity node
    user_node = EntityNode(
        name=user_name,
        group_id=group_id,
        labels=['User', 'Person', 'Entity'],
        summary=f"User profile for {user_name}",
        attributes={
            'type': 'User',
            'user_id': user_id,
        }
    )
    
    # Generate embedding for the user node
    await user_node.generate_name_embedding(graphiti.clients.embedder)
    
    # Save the user node to the graph
    await user_node.save(graphiti.driver)
    
    logger.info(f"Created new User node: {user_name} (UUID: {user_node.uuid})")
    return user_node


async def link_sessions_to_user(
    graphiti: Graphiti,
    user_node: EntityNode,
    user_id: str,
) -> int:
    """
    Create explicit relationships between the User node and all therapy sessions.
    
    Args:
        graphiti: The Graphiti instance
        user_node: The User EntityNode
        user_id: The user's group_id
    
    Returns:
        int: Number of sessions linked
    """
    link_query = """
        MATCH (user:Entity {uuid: $user_uuid})
        MATCH (session:Episodic {group_id: $group_id})
        WHERE NOT (user)-[:HAS_SESSION]->(session)
        CREATE (user)-[:HAS_SESSION {
            created_at: datetime(),
            group_id: $group_id
        }]->(session)
        RETURN count(session) as linked_sessions
    """
    
    try:
        records, _, _ = await graphiti.driver.execute_query(
            link_query,
            user_uuid=user_node.uuid,
            group_id=user_id,
        )
        
        if records:
            linked_count = records[0].get('linked_sessions', 0)
            logger.info(f"Linked {linked_count} therapy sessions to User node")
            return linked_count
        return 0
    except Exception as e:
        logger.warning(f"Could not create HAS_SESSION relationships: {e}")
        return 0


async def add_session_to_graph(
    graphiti: Graphiti,
    session_summary: str,
    session_date: datetime,
    session_number: int,
    user_id: str,
    user_name: str,
) -> str:
    """
    Add a therapy session summary to the knowledge graph.
    
    Args:
        graphiti: The Graphiti instance
        session_summary: Text summary of the therapy session
        session_date: Date/time of the session
        session_number: Sequential session number
        user_id: Unique identifier for the user
        user_name: Name of the user
    
    Returns:
        str: Episode UUID
    """
    # Ensure the session summary mentions the user explicitly
    enhanced_summary = f"Session {session_number} for {user_name}: {session_summary}"
    
    result = await graphiti.add_episode(
        name=f'Therapy Session {session_number}',
        episode_body=enhanced_summary,
        source=EpisodeType.text,
        source_description='therapy session summary',
        reference_time=session_date,
        group_id=user_id,
    )
    
    logger.info(f"Added Session {session_number} to knowledge graph")
    return result.episode.uuid if hasattr(result, 'episode') else "unknown"


async def delete_user_data(
    user_id: str,
    neo4j_driver,
) -> Dict[str, Any]:
    """
    Delete all data associated with a user from the Neo4j graph.
    
    This function deletes:
    - User Entity node
    - All Episodic nodes (therapy sessions) for the user
    - All Entity nodes belonging to the user (via group_id)
    - All RelatesToNode_ nodes connected to user entities
    - All relationships (HAS_SESSION, MENTIONS, RELATES_TO, etc.)
    
    Args:
        user_id: The user's group_id
        neo4j_driver: Neo4j driver instance
    
    Returns:
        Dict with deletion statistics
    """
    driver = await neo4j_driver.get_driver()
    
    # First, count nodes and relationships before deletion
    count_query = """
    MATCH (n)
    WHERE n.group_id = $user_id
    OPTIONAL MATCH (n)-[r]-()
    RETURN count(DISTINCT n) as node_count, count(DISTINCT r) as rel_count
    """
    
    # Query to delete all user data
    # Using DETACH DELETE to automatically remove all relationships
    delete_query = """
    MATCH (n)
    WHERE n.group_id = $user_id
    DETACH DELETE n
    RETURN count(n) as deleted_nodes
    """
    
    try:
        async with driver.session() as session:
            # Count before deletion
            count_result = await session.run(count_query, user_id=user_id)
            count_record = await count_result.single()
            
            node_count = count_record.get('node_count', 0) if count_record else 0
            rel_count = count_record.get('rel_count', 0) if count_record else 0
            
            if node_count == 0:
                return {
                    "user_id": user_id,
                    "deleted_nodes": 0,
                    "deleted_relationships": 0,
                    "status": "no_data_found"
                }
            
            # Perform deletion
            delete_result = await session.run(delete_query, user_id=user_id)
            delete_record = await delete_result.single()
            
            deleted_nodes = delete_record.get('deleted_nodes', 0) if delete_record else 0
            
            logger.info(
                f"Deleted user data for {user_id}: "
                f"{deleted_nodes} nodes, {rel_count} relationships"
            )
            
            return {
                "user_id": user_id,
                "deleted_nodes": deleted_nodes,
                "deleted_relationships": rel_count,
                "status": "success"
            }
    except Exception as e:
        logger.error(f"Error deleting user data for {user_id}: {e}")
        raise

