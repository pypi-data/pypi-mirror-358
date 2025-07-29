"""
Configuration module for paygate library.
Handles initialization and environment variables.
"""

import os
import copy
from typing import Dict, Any, Optional

# Global plan registry that will be populated by the consuming app
PLANS: Dict[str, Dict[str, Any]] = {}

# Paddle configuration from environment
PADDLE_VENDOR_ID: Optional[str] = os.getenv("PADDLE_VENDOR_ID")
PADDLE_API_KEY: Optional[str] = os.getenv("PADDLE_API_KEY") 
PADDLE_PUBLIC_KEY: Optional[str] = os.getenv("PADDLE_PUBLIC_KEY")
PADDLE_WEBHOOK_SECRET: Optional[str] = os.getenv("PADDLE_WEBHOOK_SECRET")

# Environment settings
ENVIRONMENT: str = os.getenv("PAYGATE_ENVIRONMENT", "production")


def initialize_paygate(plan_registry: Dict[str, Dict[str, Any]]) -> None:
    """
    Initialize paygate with the consuming application's plan configuration.
    
    Args:
        plan_registry: Dictionary defining subscription plans, features, and limits
        
    Example:
        PLANS = {
            "free": {
                "features": ["basic_usage", "ai_explain"],
                "limits": {"ai_explain": 2},
                "monthly_price": 0,
                "yearly_price": 0,
            },
            "pro": {
                "features": ["replay", "ai_explain"],
                "limits": {"ai_explain": 20},
                "monthly_price": 9,
                "yearly_price": 90,
                "paddle_product_id": "prod_pro123"
            },
        }
        initialize_paygate(PLANS)
    """
    global PLANS
    PLANS = copy.deepcopy(plan_registry)
    
    # Validate plan structure
    for plan_name, plan_config in PLANS.items():
        if not isinstance(plan_config, dict):
            raise ValueError(f"Plan '{plan_name}' must be a dictionary")
            
        required_fields = ["features"]
        for field in required_fields:
            if field not in plan_config:
                raise ValueError(f"Plan '{plan_name}' missing required field: {field}")
                
        if not isinstance(plan_config["features"], list):
            raise ValueError(f"Plan '{plan_name}' features must be a list")


def get_plans() -> Dict[str, Dict[str, Any]]:
    """Get the current plan registry."""
    return copy.deepcopy(PLANS)


def get_plan_config(plan_name: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific plan."""
    return PLANS.get(plan_name)


def validate_paddle_config() -> bool:
    """Validate that required Paddle configuration is present."""
    required_vars = [PADDLE_VENDOR_ID, PADDLE_API_KEY, PADDLE_PUBLIC_KEY]
    return all(var is not None for var in required_vars) 