"""
ZapSEA Python SDK - Configuration

Default configuration values and constants for the SDK.
"""

# API Configuration
DEFAULT_BASE_URL = "https://api.polityflow.com"
DEFAULT_TIMEOUT = 60
DEFAULT_MAX_RETRIES = 3

# Job Polling Configuration
DEFAULT_POLL_INTERVAL = 3  # seconds
DEFAULT_MAX_POLL_TIME = 300  # 5 minutes

# API Endpoints
API_ENDPOINTS = {
    "health": "/api/v1/navigator/health",
    "v2_impact_simulate": "/v2/impact/simulate",
    "v2_impact_compare": "/v2/impact/compare", 
    "v2_influence_path": "/v2/influence/path",
    "v2_jobs_status": "/v2/jobs/{job_id}",
    "v2_jobs_cancel": "/v2/jobs/{job_id}",
    "v2_jobs_list": "/v2/jobs/",
    "v2_feedback": "/v2/feedback/"
}

# Rate Limits by Tier
TIER_RATE_LIMITS = {
    "free": {
        "requests_per_minute": 60,
        "monthly_quota": 1000
    },
    "professional": {
        "requests_per_minute": 300,
        "monthly_quota": 10000
    },
    "enterprise": {
        "requests_per_minute": 1000,
        "monthly_quota": 100000
    }
}

# Valid Analysis Depths
ANALYSIS_DEPTHS = ["basic", "standard", "comprehensive", "deep"]

# Valid Impact Dimensions
IMPACT_DIMENSIONS = [
    "economic",
    "regulatory", 
    "social",
    "technological",
    "environmental",
    "political"
]

# Valid Scenario Types
SCENARIO_TYPES = [
    "optimistic",
    "realistic", 
    "pessimistic",
    "worst_case",
    "best_case"
]

# Valid Time Horizons
TIME_HORIZONS = [
    "3_months",
    "6_months", 
    "12_months",
    "24_months",
    "5_years"
]

# Job Status Values
JOB_STATUSES = [
    "queued",
    "processing",
    "completed",
    "failed",
    "cancelled"
]

# HTTP Status Codes
HTTP_STATUS_CODES = {
    "OK": 200,
    "ACCEPTED": 202,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "PAYMENT_REQUIRED": 402,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "UNPROCESSABLE_ENTITY": 422,
    "TOO_MANY_REQUESTS": 429,
    "INTERNAL_SERVER_ERROR": 500,
    "BAD_GATEWAY": 502,
    "SERVICE_UNAVAILABLE": 503
}

# SDK Metadata
SDK_VERSION = "1.0.0"
SDK_USER_AGENT = f"ZapSEA-Python-SDK/{SDK_VERSION}"
