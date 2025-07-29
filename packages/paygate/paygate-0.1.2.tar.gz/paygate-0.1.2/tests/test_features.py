"""
Tests for feature access logic.
"""

import pytest
from unittest.mock import Mock
from fastapi import HTTPException

import paygate
from paygate.features import (
    get_user_plan,
    has_feature,
    get_limit,
    get_plan_features,
    get_plan_limits,
    requires_feature,
    requires_plan,
)


# Test plan configuration
TEST_PLANS = {
    "free": {
        "features": ["basic_usage", "ai_explain"],
        "limits": {"ai_explain": 2},
        "monthly_price": 0,
        "yearly_price": 0,
    },
    "pro": {
        "features": ["basic_usage", "ai_explain", "advanced_features"],
        "limits": {"ai_explain": 20, "advanced_features": 10},
        "monthly_price": 9,
        "yearly_price": 90,
    },
    "enterprise": {
        "features": ["basic_usage", "ai_explain", "advanced_features", "priority_support"],
        "limits": {"ai_explain": 100},
        "monthly_price": 49,
        "yearly_price": 490,
    }
}


@pytest.fixture(autouse=True)
def setup_paygate():
    """Initialize paygate with test plans for each test."""
    paygate.initialize_paygate(TEST_PLANS)
    yield
    # Reset after test
    paygate.config.PLANS = {}


class MockUser:
    """Mock user object for testing."""
    def __init__(self, subscription_plan="free", subscription_status="active"):
        self.subscription_plan = subscription_plan
        self.subscription_status = subscription_status
        self.id = 123
    
    def is_subscription_active(self):
        return self.subscription_status == "active"


class TestGetUserPlan:
    def test_returns_user_plan(self):
        user = MockUser(subscription_plan="pro")
        assert get_user_plan(user) == "pro"
    
    def test_defaults_to_free_when_none(self):
        user = MockUser(subscription_plan=None)
        assert get_user_plan(user) == "free"
    
    def test_defaults_to_free_when_missing_attribute(self):
        user = Mock()
        del user.subscription_plan  # Remove the attribute
        assert get_user_plan(user) == "free"


class TestHasFeature:
    def test_user_has_feature_in_plan(self):
        user = MockUser(subscription_plan="pro")
        assert has_feature(user, "advanced_features") is True
    
    def test_user_does_not_have_feature(self):
        user = MockUser(subscription_plan="free")
        assert has_feature(user, "advanced_features") is False
    
    def test_user_has_basic_feature(self):
        user = MockUser(subscription_plan="free")
        assert has_feature(user, "basic_usage") is True
    
    def test_nonexistent_plan_returns_false(self):
        user = MockUser(subscription_plan="nonexistent")
        assert has_feature(user, "basic_usage") is False


class TestGetLimit:
    def test_returns_limit_when_exists(self):
        user = MockUser(subscription_plan="free")
        assert get_limit(user, "ai_explain") == 2
    
    def test_returns_none_when_no_limit(self):
        user = MockUser(subscription_plan="free")
        assert get_limit(user, "basic_usage") is None
    
    def test_returns_higher_limit_for_pro(self):
        user = MockUser(subscription_plan="pro")
        assert get_limit(user, "ai_explain") == 20
    
    def test_returns_none_for_nonexistent_feature(self):
        user = MockUser(subscription_plan="pro")
        assert get_limit(user, "nonexistent_feature") is None


class TestGetPlanFeatures:
    def test_returns_features_for_plan(self):
        features = get_plan_features("pro")
        expected = ["basic_usage", "ai_explain", "advanced_features"]
        assert features == expected
    
    def test_returns_empty_for_nonexistent_plan(self):
        features = get_plan_features("nonexistent")
        assert features == []


class TestGetPlanLimits:
    def test_returns_limits_for_plan(self):
        limits = get_plan_limits("pro")
        expected = {"ai_explain": 20, "advanced_features": 10}
        assert limits == expected
    
    def test_returns_empty_for_plan_without_limits(self):
        # Modify test plan to have no limits
        paygate.config.PLANS["test_plan"] = {"features": ["test"]}
        limits = get_plan_limits("test_plan")
        assert limits == {}


class TestRequiresFeatureDecorator:
    @pytest.mark.asyncio
    async def test_allows_access_when_user_has_feature(self):
        @requires_feature("basic_usage")
        async def test_endpoint(user):
            return "success"
        
        user = MockUser(subscription_plan="free")
        result = await test_endpoint(user=user)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_denies_access_when_user_lacks_feature(self):
        @requires_feature("advanced_features")
        async def test_endpoint(user):
            return "success"
        
        user = MockUser(subscription_plan="free")
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(user=user)
        
        assert exc_info.value.status_code == 403
        assert "advanced_features" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_checks_subscription_status_when_enabled(self):
        @requires_feature("basic_usage", check_subscription_status=True)
        async def test_endpoint(user):
            return "success"
        
        user = MockUser(subscription_plan="free", subscription_status="cancelled")
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(user=user)
        
        assert exc_info.value.status_code == 402
        assert "not active" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_skips_subscription_check_when_disabled(self):
        @requires_feature("basic_usage", check_subscription_status=False)
        async def test_endpoint(user):
            return "success"
        
        user = MockUser(subscription_plan="free", subscription_status="cancelled")
        result = await test_endpoint(user=user)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_raises_error_when_no_user_found(self):
        @requires_feature("basic_usage")
        async def test_endpoint():
            return "success"
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint()
        
        assert exc_info.value.status_code == 500
        assert "No user object found" in exc_info.value.detail


class TestRequiresPlanDecorator:
    @pytest.mark.asyncio
    async def test_allows_exact_plan_match(self):
        @requires_plan("pro")
        async def test_endpoint(user):
            return "success"
        
        user = MockUser(subscription_plan="pro")
        result = await test_endpoint(user=user)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_allows_higher_plan_when_enabled(self):
        @requires_plan("pro", allow_higher=True)
        async def test_endpoint(user):
            return "success"
        
        user = MockUser(subscription_plan="enterprise")
        result = await test_endpoint(user=user)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_denies_lower_plan(self):
        @requires_plan("pro")
        async def test_endpoint(user):
            return "success"
        
        user = MockUser(subscription_plan="free")
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(user=user)
        
        assert exc_info.value.status_code == 403
        assert "pro" in exc_info.value.detail 