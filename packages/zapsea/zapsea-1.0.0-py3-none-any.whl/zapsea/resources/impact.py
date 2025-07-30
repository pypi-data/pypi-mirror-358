"""
ZapSEA Python SDK - Impact Analysis Resource

Provides high-level interface for policy impact simulation and scenario comparison.
"""

from typing import List, Dict, Any, Optional, Union
import logging

from ..types import (
    ImpactSimulationRequest, ImpactSimulationResult, SimulationParameters,
    AnalysisDepth, ImpactDimension, ScenarioType
)
from ..exceptions import ValidationError, APIError

logger = logging.getLogger(__name__)


class Impact:
    """
    Impact Analysis resource for policy simulation and scenario comparison.
    
    Provides methods for:
    - Policy impact simulation
    - Scenario comparison
    - Economic impact analysis
    """
    
    def __init__(self, client):
        """Initialize Impact resource with client reference."""
        self._client = client
    
    async def simulate(
        self,
        policy_description: Optional[str] = None,
        policy_id: Optional[str] = None,
        analysis_depth: Union[str, AnalysisDepth] = AnalysisDepth.STANDARD,
        time_horizon: str = "12_months",
        confidence_threshold: float = 0.7,
        impact_dimensions: Optional[List[Union[str, ImpactDimension]]] = None,
        scenario_types: Optional[List[Union[str, ScenarioType]]] = None,
        include_visualizations: bool = False,
        focus_areas: Optional[List[str]] = None,
        stakeholder_groups: Optional[List[str]] = None,
        include_uncertainty: bool = True,
        auto_wait: Optional[bool] = None,
        poll_interval: Optional[int] = None,
        max_poll_time: Optional[int] = None
    ) -> ImpactSimulationResult:
        """
        Execute comprehensive policy impact simulation.
        
        Args:
            policy_description: Natural language description of the policy
            policy_id: ID of existing policy in the system
            analysis_depth: Depth of analysis ("basic", "standard", "comprehensive", "deep")
            time_horizon: Analysis time frame ("3_months", "6_months", "12_months", "24_months", "5_years")
            confidence_threshold: Minimum confidence for predictions (0.0-1.0)
            impact_dimensions: Dimensions to analyze (economic, regulatory, social, etc.)
            scenario_types: Scenarios to model (optimistic, realistic, pessimistic, etc.)
            include_visualizations: Whether to generate visualization data
            focus_areas: Specific policy areas to focus on
            stakeholder_groups: Specific stakeholder groups to analyze
            include_uncertainty: Whether to include uncertainty analysis
            auto_wait: Whether to automatically wait for completion (uses client default if None)
            poll_interval: Seconds between status polls (uses client default if None)
            max_poll_time: Maximum time to wait for completion (uses client default if None)
            
        Returns:
            ImpactSimulationResult with comprehensive analysis
            
        Raises:
            ValidationError: Invalid parameters
            APIError: API request failed
            JobTimeoutError: Job didn't complete in time
            
        Example:
            ```python
            result = await client.impact.simulate(
                policy_description="Federal AI regulation requiring algorithmic transparency",
                analysis_depth="comprehensive",
                impact_dimensions=["economic", "regulatory", "social"],
                scenario_types=["optimistic", "realistic", "pessimistic"]
            )
            
            print(f"Success Probability: {result.success_probability}")
            print(f"Key Findings: {result.key_findings}")
            ```
        """
        
        # Validate inputs
        if not policy_description and not policy_id:
            raise ValidationError("Either policy_description or policy_id must be provided")
        
        # Set defaults
        if impact_dimensions is None:
            impact_dimensions = [ImpactDimension.ECONOMIC, ImpactDimension.REGULATORY]
        
        if scenario_types is None:
            scenario_types = [ScenarioType.REALISTIC]
        
        auto_wait = auto_wait if auto_wait is not None else self._client.auto_poll
        
        # Build request
        parameters = SimulationParameters(
            time_horizon=time_horizon,
            confidence_threshold=confidence_threshold,
            include_uncertainty=include_uncertainty,
            focus_areas=focus_areas,
            stakeholder_groups=stakeholder_groups
        )
        
        request = ImpactSimulationRequest(
            policy_description=policy_description,
            policy_id=policy_id,
            analysis_depth=analysis_depth,
            parameters=parameters,
            impact_dimensions=impact_dimensions,
            scenario_types=scenario_types,
            include_visualizations=include_visualizations
        )
        
        logger.info(f"Submitting impact simulation: {analysis_depth} analysis")
        
        if auto_wait:
            # Submit and wait for completion
            result_data = await self._client.submit_and_wait(
                method="POST",
                path="/v2/impact/simulate",
                json=request.dict(),
                poll_interval=poll_interval,
                max_poll_time=max_poll_time
            )
            
            return ImpactSimulationResult(**result_data)
        else:
            # Just submit and return job ID
            job_id = await self._client.submit_job(
                method="POST",
                path="/v2/impact/simulate",
                json=request.dict()
            )
            
            logger.info(f"Impact simulation job submitted: {job_id}")
            return job_id
    
    async def compare_scenarios(
        self,
        scenarios: List[Dict[str, Any]],
        comparison_dimensions: Optional[List[str]] = None,
        include_visualizations: bool = False,
        auto_wait: Optional[bool] = None,
        poll_interval: Optional[int] = None,
        max_poll_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple policy scenarios side-by-side.
        
        Args:
            scenarios: List of scenario configurations to compare
            comparison_dimensions: Specific dimensions to compare across scenarios
            include_visualizations: Whether to generate comparison visualizations
            auto_wait: Whether to automatically wait for completion
            poll_interval: Seconds between status polls
            max_poll_time: Maximum time to wait for completion
            
        Returns:
            Scenario comparison results
            
        Example:
            ```python
            scenarios = [
                {
                    "name": "Current Proposal",
                    "policy_description": "AI regulation with transparency requirements",
                    "parameters": {"time_horizon": "12_months"}
                },
                {
                    "name": "Alternative Approach", 
                    "policy_description": "AI regulation with industry self-regulation",
                    "parameters": {"time_horizon": "12_months"}
                }
            ]
            
            comparison = await client.impact.compare_scenarios(
                scenarios=scenarios,
                comparison_dimensions=["economic", "regulatory"]
            )
            ```
        """
        
        if not scenarios or len(scenarios) < 2:
            raise ValidationError("At least 2 scenarios are required for comparison")
        
        if len(scenarios) > 5:
            raise ValidationError("Maximum 5 scenarios can be compared at once")
        
        auto_wait = auto_wait if auto_wait is not None else self._client.auto_poll
        
        request_data = {
            "scenarios": scenarios,
            "comparison_dimensions": comparison_dimensions or ["economic", "regulatory", "social"],
            "include_visualizations": include_visualizations
        }
        
        logger.info(f"Submitting scenario comparison: {len(scenarios)} scenarios")
        
        if auto_wait:
            result_data = await self._client.submit_and_wait(
                method="POST",
                path="/v2/impact/compare",
                json=request_data,
                poll_interval=poll_interval,
                max_poll_time=max_poll_time
            )
            
            return result_data
        else:
            job_id = await self._client.submit_job(
                method="POST",
                path="/v2/impact/compare",
                json=request_data
            )
            
            logger.info(f"Scenario comparison job submitted: {job_id}")
            return job_id
    
    async def analyze_economic_impact(
        self,
        policy_description: str,
        economic_indicators: Optional[List[str]] = None,
        include_fred_data: bool = True,
        time_horizon: str = "12_months",
        auto_wait: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Analyze economic impact with FRED data integration.
        
        Args:
            policy_description: Policy to analyze
            economic_indicators: Specific indicators to focus on
            include_fred_data: Whether to include FRED economic data
            time_horizon: Analysis time frame
            auto_wait: Whether to automatically wait for completion
            
        Returns:
            Economic impact analysis results
        """
        
        # Build economic-focused simulation request
        parameters = SimulationParameters(
            time_horizon=time_horizon,
            confidence_threshold=0.7,
            focus_areas=economic_indicators or ["gdp", "employment", "inflation", "interest_rates"]
        )
        
        request = ImpactSimulationRequest(
            policy_description=policy_description,
            analysis_depth=AnalysisDepth.COMPREHENSIVE,
            parameters=parameters,
            impact_dimensions=[ImpactDimension.ECONOMIC],
            scenario_types=[ScenarioType.OPTIMISTIC, ScenarioType.REALISTIC, ScenarioType.PESSIMISTIC]
        )
        
        # Add economic context flag
        request_data = request.dict()
        request_data["economic_context"] = include_fred_data
        
        auto_wait = auto_wait if auto_wait is not None else self._client.auto_poll
        
        logger.info(f"Submitting economic impact analysis (FRED data: {include_fred_data})")
        
        if auto_wait:
            result_data = await self._client.submit_and_wait(
                method="POST",
                path="/v2/impact/simulate",
                json=request_data
            )
            
            return result_data
        else:
            job_id = await self._client.submit_job(
                method="POST",
                path="/v2/impact/simulate",
                json=request_data
            )
            
            logger.info(f"Economic impact analysis job submitted: {job_id}")
            return job_id
