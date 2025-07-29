"""
Feature access logic for subscription-based feature gating.
"""

from functools import wraps
from typing import Any, Optional, List, Callable

from fastapi import HTTPException

from . import config


def get_user_plan(user: Any) -> str:
    """
    Get the subscription plan for a user.
    
    Args:
        user: User object with subscription_plan attribute
        
    Returns:
        Plan name, defaults to "free" if not set
    """
    return getattr(user, "subscription_plan", "free") or "free"


def has_feature(user: Any, feature: str) -> bool:
    """
    Check if a user has access to a specific feature.
    
    Args:
        user: User object
        feature: Feature name to check
        
    Returns:
        True if user has access to the feature
    """
    plan = get_user_plan(user)
    plan_config = config.PLANS.get(plan, {})
    features = plan_config.get("features", [])
    return feature in features


def get_limit(user: Any, feature: str) -> Optional[int]:
    """
    Get the usage limit for a feature for the user's plan.
    
    Args:
        user: User object
        feature: Feature name
        
    Returns:
        Limit number, or None if no limit is set
    """
    plan = get_user_plan(user)
    plan_config = config.PLANS.get(plan, {})
    limits = plan_config.get("limits", {})
    return limits.get(feature)


def get_plan_features(plan_name: str) -> List[str]:
    """
    Get all features available in a plan.
    
    Args:
        plan_name: Name of the plan
        
    Returns:
        List of feature names
    """
    plan_config = config.PLANS.get(plan_name, {})
    return plan_config.get("features", [])


def get_plan_limits(plan_name: str) -> dict:
    """
    Get all limits for a plan.
    
    Args:
        plan_name: Name of the plan
        
    Returns:
        Dictionary of feature limits
    """
    plan_config = config.PLANS.get(plan_name, {})
    return plan_config.get("limits", {})


def requires_feature(feature: str, check_subscription_status: bool = True) -> Callable:
    """
    Decorator that requires a user to have access to a specific feature.
    
    Args:
        feature: Feature name required
        check_subscription_status: Whether to check if subscription is active
        
    Usage:
        @requires_feature("ai_explain")
        async def explain_code(user: User = Depends(get_current_user)):
            # This endpoint requires ai_explain feature
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Try to find user in function arguments
            user = None
            
            # Check kwargs first (most common for FastAPI dependencies)
            for key, value in kwargs.items():
                if hasattr(value, 'subscription_plan'):
                    user = value
                    break
            
            # Check args if not found in kwargs
            if user is None:
                for arg in args:
                    if hasattr(arg, 'subscription_plan'):
                        user = arg
                        break
                        
            if user is None:
                raise HTTPException(
                    status_code=500,
                    detail="No user object found in function parameters"
                )
            
            # Check if subscription is active (if enabled)
            if check_subscription_status and hasattr(user, 'is_subscription_active'):
                if not user.is_subscription_active():
                    raise HTTPException(
                        status_code=402,
                        detail="Subscription is not active"
                    )
            
            # Check feature access
            if not has_feature(user, feature):
                plan = get_user_plan(user)
                raise HTTPException(
                    status_code=403,
                    detail=f"Feature '{feature}' not available in '{plan}' plan"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def requires_plan(required_plan: str, allow_higher: bool = True) -> Callable:
    """
    Decorator that requires a user to have a specific plan or higher.
    
    Args:
        required_plan: Minimum plan required
        allow_higher: Whether to allow higher tier plans
        
    Note: This assumes a plan hierarchy. You may need to customize this
    based on your specific plan structure.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Find user object (same logic as requires_feature)
            user = None
            for key, value in kwargs.items():
                if hasattr(value, 'subscription_plan'):
                    user = value
                    break
                    
            if user is None:
                for arg in args:
                    if hasattr(arg, 'subscription_plan'):
                        user = arg
                        break
                        
            if user is None:
                raise HTTPException(
                    status_code=500,
                    detail="No user object found in function parameters"
                )
            
            user_plan = get_user_plan(user)
            
            if allow_higher:
                # This is a simplified check - you might want to implement
                # a proper plan hierarchy system
                if user_plan == required_plan or user_plan in ["pro", "enterprise"]:
                    return await func(*args, **kwargs)
            else:
                if user_plan == required_plan:
                    return await func(*args, **kwargs)
            
            raise HTTPException(
                status_code=403,
                detail=f"Plan '{required_plan}' or higher required. Current plan: '{user_plan}'"
            )
        
        return wrapper
    return decorator 