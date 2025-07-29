"""
Tests for the SubscriptionMixin model.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from paygate.models import SubscriptionMixin


class MockUser(SubscriptionMixin):
    """Mock user class that includes SubscriptionMixin."""
    def __init__(self):
        # Initialize with default values
        self.subscription_plan = "free"
        self.subscription_status = "active"
        self.subscription_ends_at = None
        self.subscription_provider = "paddle"
        self.paddle_subscription_id = None
        self.paddle_customer_id = None
        self.subscription_created_at = None
        self.subscription_updated_at = datetime.utcnow()


class TestSubscriptionMixin:
    def test_default_values(self):
        user = MockUser()
        
        assert user.subscription_plan == "free"
        assert user.subscription_status == "active"
        assert user.subscription_ends_at is None
        assert user.subscription_provider == "paddle"
        assert user.paddle_subscription_id is None
        assert user.paddle_customer_id is None
        assert user.subscription_created_at is None
        assert user.subscription_updated_at is not None


class TestIsSubscriptionActive:
    def test_active_subscription_without_end_date(self):
        user = MockUser()
        user.subscription_status = "active"
        user.subscription_ends_at = None
        
        assert user.is_subscription_active() is True
    
    def test_active_subscription_with_future_end_date(self):
        user = MockUser()
        user.subscription_status = "active"
        user.subscription_ends_at = datetime.utcnow() + timedelta(days=30)
        
        assert user.is_subscription_active() is True
    
    def test_active_subscription_with_past_end_date(self):
        user = MockUser()
        user.subscription_status = "active"
        user.subscription_ends_at = datetime.utcnow() - timedelta(days=1)
        
        assert user.is_subscription_active() is False
    
    def test_cancelled_subscription(self):
        user = MockUser()
        user.subscription_status = "cancelled"
        user.subscription_ends_at = None
        
        assert user.is_subscription_active() is False
    
    def test_past_due_subscription(self):
        user = MockUser()
        user.subscription_status = "past_due"
        user.subscription_ends_at = datetime.utcnow() + timedelta(days=30)
        
        assert user.is_subscription_active() is False


class TestDaysUntilExpiry:
    def test_returns_none_for_lifetime_subscription(self):
        user = MockUser()
        user.subscription_ends_at = None
        
        assert user.days_until_expiry() is None
    
    def test_returns_days_for_future_expiry(self):
        user = MockUser()
        user.subscription_ends_at = datetime.utcnow() + timedelta(days=15)
        
        days = user.days_until_expiry()
        assert days is not None and days >= 14  # Allow for timing differences
    
    def test_returns_zero_for_past_expiry(self):
        user = MockUser()
        user.subscription_ends_at = datetime.utcnow() - timedelta(days=5)
        
        days = user.days_until_expiry()
        assert days == 0
    
    def test_returns_zero_for_today_expiry(self):
        user = MockUser()
        # Set to expire in a few hours
        user.subscription_ends_at = datetime.utcnow() + timedelta(hours=12)
        
        days = user.days_until_expiry()
        assert days == 0  # Same day = 0 days


class TestSubscriptionFields:
    def test_subscription_plan_field(self):
        user = MockUser()
        user.subscription_plan = "pro"
        
        assert user.subscription_plan == "pro"
    
    def test_subscription_status_field(self):
        user = MockUser()
        user.subscription_status = "cancelled"
        
        assert user.subscription_status == "cancelled"
    
    def test_paddle_subscription_id_field(self):
        user = MockUser()
        user.paddle_subscription_id = "sub_123456"
        
        assert user.paddle_subscription_id == "sub_123456"
    
    def test_paddle_customer_id_field(self):
        user = MockUser()
        user.paddle_customer_id = "cust_789012"
        
        assert user.paddle_customer_id == "cust_789012"
    
    def test_subscription_provider_field(self):
        user = MockUser()
        user.subscription_provider = "stripe"
        
        assert user.subscription_provider == "stripe"


class TestSubscriptionTimestamps:
    def test_subscription_created_at_can_be_set(self):
        user = MockUser()
        created_time = datetime.utcnow()
        user.subscription_created_at = created_time
        
        assert user.subscription_created_at == created_time
    
    def test_subscription_updated_at_defaults_to_now(self):
        user = MockUser()
        
        assert user.subscription_updated_at is not None
        # Should be close to now (within 1 second)
        time_diff = abs((datetime.utcnow() - user.subscription_updated_at).total_seconds())
        assert time_diff < 1.0 