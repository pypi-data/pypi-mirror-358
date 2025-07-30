"""
ZapSEA Python SDK - Feedback Resource

Provides interface for submitting feedback and accessing analytics.
"""

from typing import Dict, Any, Optional
import logging

from ..types import FeedbackRequest
from ..exceptions import ValidationError, APIError

logger = logging.getLogger(__name__)


class Feedback:
    """
    Feedback resource for user feedback and analytics.
    
    Provides methods for:
    - Submitting user feedback
    - Accessing feedback analytics
    - Rating API features
    """
    
    def __init__(self, client):
        """Initialize Feedback resource with client reference."""
        self._client = client
    
    async def submit(
        self,
        rating: int,
        page: str,
        comment: Optional[str] = None,
        feedback_type: str = "general",
        feature_used: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit user feedback.
        
        Args:
            rating: Rating from 1-5 stars
            page: Page or feature where feedback was given
            comment: Optional written feedback (max 1000 characters)
            feedback_type: Type of feedback ("general", "bug_report", "feature_request", "support")
            feature_used: Specific feature that was used
            
        Returns:
            Feedback submission confirmation
            
        Raises:
            ValidationError: Invalid parameters
            APIError: API request failed
            
        Example:
            ```python
            response = await client.feedback.submit(
                rating=5,
                page="impact_simulation",
                comment="Great analysis depth and accuracy!",
                feedback_type="general",
                feature_used="comprehensive_analysis"
            )
            
            print(f"Feedback ID: {response['feedback_id']}")
            ```
        """
        
        if rating < 1 or rating > 5:
            raise ValidationError("Rating must be between 1 and 5")
        
        if comment and len(comment) > 1000:
            raise ValidationError("Comment must be 1000 characters or less")
        
        request = FeedbackRequest(
            rating=rating,
            page=page,
            comment=comment,
            feedback_type=feedback_type,
            feature_used=feature_used
        )
        
        response = await self._client.request(
            method="POST",
            path="/v2/feedback/",
            json=request.dict()
        )
        
        logger.info(f"Feedback submitted: {rating} stars for {page}")
        return response
    
    async def get_analytics(
        self,
        page_filter: Optional[str] = None,
        feedback_type_filter: Optional[str] = None,
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Get feedback analytics (admin/enterprise only).
        
        Args:
            page_filter: Filter by specific page
            feedback_type_filter: Filter by feedback type
            date_range: Date range filter {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
            
        Returns:
            Feedback analytics data
            
        Example:
            ```python
            analytics = await client.feedback.get_analytics(
                page_filter="impact_simulation",
                date_range={"start": "2024-01-01", "end": "2024-01-31"}
            )
            
            print(f"Average rating: {analytics['average_rating']}")
            print(f"Total feedback: {analytics['total_count']}")
            ```
        """
        
        params = {}
        
        if page_filter:
            params["page_filter"] = page_filter
        
        if feedback_type_filter:
            params["feedback_type_filter"] = feedback_type_filter
        
        if date_range:
            if "start" in date_range:
                params["start_date"] = date_range["start"]
            if "end" in date_range:
                params["end_date"] = date_range["end"]
        
        response = await self._client.request(
            method="GET",
            path="/v2/feedback/analytics",
            params=params
        )
        
        return response
    
    async def rate_feature(
        self,
        feature_name: str,
        rating: int,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rate a specific API feature.
        
        Args:
            feature_name: Name of the feature to rate
            rating: Rating from 1-5 stars
            comment: Optional comment about the feature
            
        Returns:
            Rating submission confirmation
            
        Example:
            ```python
            response = await client.feedback.rate_feature(
                feature_name="impact_simulation",
                rating=4,
                comment="Very accurate but could be faster"
            )
            ```
        """
        
        return await self.submit(
            rating=rating,
            page="api_feature",
            comment=comment,
            feedback_type="feature_rating",
            feature_used=feature_name
        )
    
    async def report_bug(
        self,
        page: str,
        description: str,
        steps_to_reproduce: Optional[str] = None,
        expected_behavior: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Report a bug or issue.
        
        Args:
            page: Page or feature where bug occurred
            description: Description of the bug
            steps_to_reproduce: Steps to reproduce the issue
            expected_behavior: What should have happened
            
        Returns:
            Bug report submission confirmation
            
        Example:
            ```python
            response = await client.feedback.report_bug(
                page="impact_simulation",
                description="Simulation fails with timeout error",
                steps_to_reproduce="1. Submit large policy text 2. Wait for processing",
                expected_behavior="Should complete within 5 minutes"
            )
            ```
        """
        
        # Combine all bug information into comment
        bug_details = [f"Description: {description}"]
        
        if steps_to_reproduce:
            bug_details.append(f"Steps to reproduce: {steps_to_reproduce}")
        
        if expected_behavior:
            bug_details.append(f"Expected behavior: {expected_behavior}")
        
        comment = "\n\n".join(bug_details)
        
        return await self.submit(
            rating=1,  # Bug reports get 1 star by default
            page=page,
            comment=comment,
            feedback_type="bug_report"
        )
    
    async def request_feature(
        self,
        feature_title: str,
        description: str,
        use_case: Optional[str] = None,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Submit a feature request.
        
        Args:
            feature_title: Title of the requested feature
            description: Detailed description of the feature
            use_case: How the feature would be used
            priority: Priority level ("low", "medium", "high")
            
        Returns:
            Feature request submission confirmation
            
        Example:
            ```python
            response = await client.feedback.request_feature(
                feature_title="Real-time policy monitoring",
                description="Ability to monitor policy changes in real-time",
                use_case="Alert users when tracked policies are updated",
                priority="high"
            )
            ```
        """
        
        # Combine feature request information
        request_details = [f"Feature: {feature_title}", f"Description: {description}"]
        
        if use_case:
            request_details.append(f"Use case: {use_case}")
        
        request_details.append(f"Priority: {priority}")
        
        comment = "\n\n".join(request_details)
        
        return await self.submit(
            rating=3,  # Neutral rating for feature requests
            page="feature_request",
            comment=comment,
            feedback_type="feature_request"
        )
