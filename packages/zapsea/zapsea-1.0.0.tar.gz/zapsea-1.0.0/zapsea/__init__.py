"""
ZapSEA Python SDK

A production-ready Python SDK for the ZapSEA Intelligence Engine API V2.
Provides simple, async-first interfaces for policy impact simulation and analysis.

Example:
    ```python
    from zapsea import ZapSEA
    
    # Initialize client
    client = ZapSEA(api_key="pk_live_your_api_key_here")
    
    # Run impact simulation
    result = await client.impact.simulate(
        policy_description="AI regulation for financial services",
        analysis_depth="comprehensive"
    )
    
    print(f"Simulation ID: {result.simulation_id}")
    print(f"Success Probability: {result.success_probability}")
    ```
"""

from .client import ZapSEA
from .exceptions import (
    ZapSEAError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
    JobTimeoutError
)
from .types import (
    ImpactSimulationResult,
    InfluencePathResult,
    JobStatus,
    SimulationParameters
)

__version__ = "1.0.0"
__author__ = "ZapSEA Team"
__email__ = "support@polityflow.com"

__all__ = [
    "ZapSEA",
    "ZapSEAError",
    "AuthenticationError", 
    "RateLimitError",
    "ValidationError",
    "APIError",
    "JobTimeoutError",
    "ImpactSimulationResult",
    "InfluencePathResult", 
    "JobStatus",
    "SimulationParameters"
]
