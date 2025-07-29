"""
paygate: Reusable subscription & feature gating library for FastAPI with Paddle integration.
"""

from .config import initialize_paygate
from .features import has_feature, get_limit, requires_feature, get_user_plan
from .models import SubscriptionMixin
from .paddle import handle_webhook, create_paddle_router, set_user_handlers
from .limits import requires_feature_with_limit, check_feature_limit, increment_feature_usage

__version__ = "0.1.0"
__all__ = [
    "initialize_paygate",
    "has_feature",
    "get_limit", 
    "requires_feature",
    "get_user_plan",
    "SubscriptionMixin",
    "handle_webhook",
    "create_paddle_router",
    "set_user_handlers",
    "requires_feature_with_limit",
    "check_feature_limit",
    "increment_feature_usage",
] 