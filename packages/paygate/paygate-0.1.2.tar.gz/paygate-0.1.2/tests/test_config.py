"""
Tests for configuration module.
"""

import pytest
import paygate
from paygate.config import (
    initialize_paygate,
    get_plans,
    get_plan_config,
    validate_paddle_config,
    PLANS
)


class TestInitializePaygate:
    def test_initializes_plans_correctly(self):
        test_plans = {
            "free": {
                "features": ["basic"],
                "monthly_price": 0
            },
            "pro": {
                "features": ["basic", "advanced"],
                "monthly_price": 10
            }
        }
        
        initialize_paygate(test_plans)
        
        assert get_plans() == test_plans
    
    def test_validates_plan_structure(self):
        invalid_plans = {
            "free": "not_a_dict"  # Should be a dictionary
        }
        
        with pytest.raises(ValueError, match="must be a dictionary"):
            initialize_paygate(invalid_plans)
    
    def test_requires_features_field(self):
        invalid_plans = {
            "free": {
                "monthly_price": 0
                # Missing required "features" field
            }
        }
        
        with pytest.raises(ValueError, match="missing required field: features"):
            initialize_paygate(invalid_plans)
    
    def test_validates_features_is_list(self):
        invalid_plans = {
            "free": {
                "features": "not_a_list",  # Should be a list
                "monthly_price": 0
            }
        }
        
        with pytest.raises(ValueError, match="features must be a list"):
            initialize_paygate(invalid_plans)
    
    def test_copies_plans_not_reference(self):
        original_plans = {
            "free": {
                "features": ["basic"],
                "monthly_price": 0
            }
        }
        
        initialize_paygate(original_plans)
        
        # Modify original
        original_plans["free"]["monthly_price"] = 999
        
        # Should not affect the stored plans
        assert get_plans()["free"]["monthly_price"] == 0


class TestGetPlans:
    def test_returns_copy_of_plans(self):
        test_plans = {
            "free": {
                "features": ["basic"],
                "monthly_price": 0
            }
        }
        
        initialize_paygate(test_plans)
        plans_copy = get_plans()
        
        # Modify the copy
        plans_copy["free"]["monthly_price"] = 999
        
        # Original should be unchanged
        assert get_plans()["free"]["monthly_price"] == 0


class TestGetPlanConfig:
    def test_returns_plan_config_when_exists(self):
        test_plans = {
            "pro": {
                "features": ["advanced"],
                "monthly_price": 10
            }
        }
        
        initialize_paygate(test_plans)
        config = get_plan_config("pro")
        
        assert config == test_plans["pro"]
    
    def test_returns_none_when_plan_not_exists(self):
        initialize_paygate({})
        config = get_plan_config("nonexistent")
        
        assert config is None


class TestValidatePaddleConfig:
    def test_returns_true_when_all_config_present(self, monkeypatch):
        monkeypatch.setenv("PADDLE_VENDOR_ID", "vendor123")
        monkeypatch.setenv("PADDLE_API_KEY", "key123")
        monkeypatch.setenv("PADDLE_PUBLIC_KEY", "public123")
        
        # Reload the module to pick up env vars
        import importlib
        import paygate.config
        importlib.reload(paygate.config)
        
        assert paygate.config.validate_paddle_config() is True
    
    def test_returns_false_when_config_missing(self, monkeypatch):
        # Clear environment variables
        monkeypatch.delenv("PADDLE_VENDOR_ID", raising=False)
        monkeypatch.delenv("PADDLE_API_KEY", raising=False)
        monkeypatch.delenv("PADDLE_PUBLIC_KEY", raising=False)
        
        # Reload the module
        import importlib
        import paygate.config
        importlib.reload(paygate.config)
        
        assert paygate.config.validate_paddle_config() is False


class TestPlanValidation:
    def test_accepts_valid_minimal_plan(self):
        valid_plans = {
            "free": {
                "features": []
            }
        }
        
        # Should not raise
        initialize_paygate(valid_plans)
    
    def test_accepts_plan_with_all_fields(self):
        complete_plans = {
            "pro": {
                "features": ["basic", "advanced"],
                "limits": {"basic": 10, "advanced": 5},
                "monthly_price": 10,
                "yearly_price": 100,
                "paddle_product_id": "prod_123"
            }
        }
        
        # Should not raise
        initialize_paygate(complete_plans)
        
        assert get_plan_config("pro") == complete_plans["pro"] 