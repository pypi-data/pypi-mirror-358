"""
ZapSEA Python SDK - Influence Analysis Resource

Provides high-level interface for influence pathfinding and network analysis.
"""

from typing import List, Dict, Any, Optional
import logging

from ..types import InfluencePathRequest, InfluencePathResult
from ..exceptions import ValidationError, APIError

logger = logging.getLogger(__name__)


class Influence:
    """
    Influence Analysis resource for pathfinding and network analysis.
    
    Provides methods for:
    - Finding influence paths between entities
    - Network analysis and statistics
    - Stakeholder influence mapping
    """
    
    def __init__(self, client):
        """Initialize Influence resource with client reference."""
        self._client = client
    
    async def find_path(
        self,
        source_entity: str,
        target_entity: str,
        max_depth: int = 5,
        include_alternatives: bool = False,
        min_confidence: float = 0.5,
        include_network_stats: bool = False,
        auto_wait: Optional[bool] = None,
        poll_interval: Optional[int] = None,
        max_poll_time: Optional[int] = None
    ) -> InfluencePathResult:
        """
        Find the shortest influence path between two entities.
        
        Args:
            source_entity: Starting entity ID or name
            target_entity: Target entity ID or name
            max_depth: Maximum path length to search (1-10)
            include_alternatives: Whether to include alternative paths
            min_confidence: Minimum confidence for relationships (0.0-1.0)
            include_network_stats: Whether to include network statistics
            auto_wait: Whether to automatically wait for completion
            poll_interval: Seconds between status polls
            max_poll_time: Maximum time to wait for completion
            
        Returns:
            InfluencePathResult with path information
            
        Example:
            ```python
            path = await client.influence.find_path(
                source_entity="Congress",
                target_entity="Tech Industry",
                max_depth=4,
                include_alternatives=True
            )
            
            print(f"Path length: {path.path_length}")
            print(f"Influence score: {path.total_influence_score}")
            ```
        """
        
        if max_depth < 1 or max_depth > 10:
            raise ValidationError("max_depth must be between 1 and 10")
        
        if min_confidence < 0.0 or min_confidence > 1.0:
            raise ValidationError("min_confidence must be between 0.0 and 1.0")
        
        auto_wait = auto_wait if auto_wait is not None else self._client.auto_poll
        
        request = InfluencePathRequest(
            source_entity_id=source_entity,
            target_entity_id=target_entity,
            max_depth=max_depth,
            include_alternatives=include_alternatives,
            min_confidence=min_confidence,
            include_network_stats=include_network_stats
        )
        
        logger.info(f"Finding influence path: {source_entity} -> {target_entity}")
        
        if auto_wait:
            result_data = await self._client.submit_and_wait(
                method="POST",
                path="/v2/influence/path",
                json=request.dict(),
                poll_interval=poll_interval,
                max_poll_time=max_poll_time
            )
            
            return InfluencePathResult(**result_data)
        else:
            job_id = await self._client.submit_job(
                method="POST",
                path="/v2/influence/path",
                json=request.dict()
            )
            
            logger.info(f"Influence pathfinding job submitted: {job_id}")
            return job_id
    
    async def analyze_network(
        self,
        entity_ids: List[str],
        include_centrality_metrics: bool = True,
        include_community_detection: bool = False,
        auto_wait: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Analyze influence network for a set of entities.
        
        Args:
            entity_ids: List of entity IDs to analyze
            include_centrality_metrics: Whether to calculate centrality metrics
            include_community_detection: Whether to detect communities
            auto_wait: Whether to automatically wait for completion
            
        Returns:
            Network analysis results
        """
        
        if not entity_ids:
            raise ValidationError("At least one entity ID is required")
        
        if len(entity_ids) > 50:
            raise ValidationError("Maximum 50 entities can be analyzed at once")
        
        auto_wait = auto_wait if auto_wait is not None else self._client.auto_poll
        
        request_data = {
            "entity_ids": entity_ids,
            "include_centrality_metrics": include_centrality_metrics,
            "include_community_detection": include_community_detection
        }
        
        logger.info(f"Analyzing influence network: {len(entity_ids)} entities")
        
        if auto_wait:
            result_data = await self._client.submit_and_wait(
                method="POST",
                path="/v2/influence/network",
                json=request_data
            )
            
            return result_data
        else:
            job_id = await self._client.submit_job(
                method="POST",
                path="/v2/influence/network",
                json=request_data
            )
            
            logger.info(f"Network analysis job submitted: {job_id}")
            return job_id
