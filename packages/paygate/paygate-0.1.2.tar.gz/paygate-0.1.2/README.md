# 📦 Paygate

> Reusable subscription & feature gating library for FastAPI with Paddle integration

**Paygate** is a Python library that provides subscription management and feature gating for FastAPI applications. It integrates seamlessly with Paddle to handle subscription lifecycles, enforce feature access based on subscription tiers, and track usage limits.

## ✨ Features

- 🔐 **Feature Gating**: Control access to features based on subscription plans
- 📊 **Usage Limiting**: Track and enforce usage limits per feature
- 🎣 **Paddle Integration**: Handle subscription webhooks automatically  
- 🗄️ **Database Ready**: SQLAlchemy mixin for easy integration
- 🎯 **FastAPI Native**: Built specifically for FastAPI applications
- 🧪 **Testing Friendly**: Easy to mock and test
- 🔧 **Configurable**: Each app defines its own plans and features

## 🚀 Installation

```bash
pip install paygate
```

## 🏁 Quick Start

### 1. Define Your Subscription Plans

```python
# yourapp/config/subscription_plans.py
PLANS = {
    "free": {
        "features": ["basic_usage", "ai_explain"],
        "limits": {"ai_explain": 2},
        "monthly_price": 0,
        "yearly_price": 0,
    },
    "pro": {
        "features": ["replay", "ai_explain", "advanced_features"],
        "limits": {"ai_explain": 20},
        "monthly_price": 9,
        "yearly_price": 90,
        "paddle_product_id": "prod_pro123"
    },
    "enterprise": {
        "features": ["replay", "ai_explain", "advanced_features", "priority_support"],
        "limits": {"ai_explain": 100},
        "monthly_price": 49,
        "yearly_price": 490,
        "paddle_product_id": "prod_enterprise456"
    }
}
```

### 2. Extend Your User Model

```python
# yourapp/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from paygate import SubscriptionMixin

class Base(DeclarativeBase):
    pass

class User(Base, SubscriptionMixin):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    # ... other user fields
    # SubscriptionMixin adds subscription fields automatically
```

### 3. Initialize Paygate

```python
# yourapp/main.py
from fastapi import FastAPI
import paygate
from yourapp.config.subscription_plans import PLANS

app = FastAPI()

# Initialize paygate with your plans
paygate.initialize_paygate(PLANS)

# Set up user handlers for webhooks
async def lookup_user(identifier: str):
    # Find user by email or paddle_subscription_id
    # Return user object or None
    pass

async def update_user(user, update_data: dict):
    # Update user subscription fields
    # Save to database
    pass

paygate.set_user_handlers(lookup_user, update_user)
```

### 4. Add Paddle Webhook Endpoint

```python
# Add to your FastAPI app
from paygate import create_paddle_router

app.include_router(create_paddle_router())
```

### 5. Use Feature Gating

```python
from fastapi import Depends
from paygate import requires_feature, requires_feature_with_limit

@app.post("/api/explain")
@requires_feature_with_limit("ai_explain", period="monthly")
async def explain_code(
    code: str,
    user: User = Depends(get_current_user)
):
    # This endpoint requires ai_explain feature
    # Usage will be automatically tracked and limited
    return {"explanation": "..."}

@app.get("/api/advanced-feature")
@requires_feature("advanced_features")
async def advanced_endpoint(user: User = Depends(get_current_user)):
    # Only users with plans that include "advanced_features" can access this
    return {"data": "advanced stuff"}
```

## 📋 Environment Variables

```bash
# Required for webhook verification
PADDLE_WEBHOOK_SECRET=your_paddle_webhook_secret

# Optional - for future Paddle API integration
PADDLE_VENDOR_ID=your_paddle_vendor_id
PADDLE_API_KEY=your_paddle_api_key
PADDLE_PUBLIC_KEY=your_paddle_public_key

# Optional
PAYGATE_ENVIRONMENT=production  # or development
```

## 🎯 Usage Limiting

Paygate supports sophisticated usage tracking:

```python
from paygate import check_feature_limit, increment_feature_usage

# Check if user can use a feature
if await check_feature_limit(user, "ai_explain"):
    # User is within limits
    result = perform_ai_explain()
    
    # Manually increment usage
    await increment_feature_usage(user, "ai_explain")
    
    return result
else:
    raise HTTPException(429, "Usage limit exceeded")
```

### Built-in Usage Stores

#### In-Memory (default)
```python
from paygate.limits import set_usage_store, MemoryUsageStore
set_usage_store(MemoryUsageStore())
```

#### Redis
```python
import redis.asyncio as redis
from paygate.limits import RedisUsageStore, set_usage_store
redis_client = redis.Redis(host='localhost', port=6379, db=0)
usage_store = RedisUsageStore(redis_client)
set_usage_store(usage_store)
```

#### MongoDB (pymongo)
```python
from pymongo import MongoClient
from paygate.limits import MongoUsageStore, set_usage_store
client = MongoClient("mongodb://localhost:27017")
collection = client["paygate"]["usage"]
store = MongoUsageStore(collection)
set_usage_store(store)
```

#### SQLAlchemy (async)
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from paygate.limits import SQLAlchemyUsageStore, set_usage_store, UsageRecord, Base

engine = create_async_engine("sqlite+aiosqlite:///./test.db")
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Create the table (run once)
import asyncio
async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(create_table())

store = SQLAlchemyUsageStore(async_session)
set_usage_store(store)
```

## 🧪 Testing

Paygate is designed to be easily testable:

```python
import pytest
from paygate import initialize_paygate, has_feature

# Test plan configuration
TEST_PLANS = {
    "free": {"features": ["basic"], "limits": {"basic": 5}},
    "pro": {"features": ["basic", "advanced"], "limits": {"basic": 50}}
}

def test_feature_access():
    initialize_paygate(TEST_PLANS)
    
    user = MockUser(subscription_plan="pro")
    
    assert has_feature(user, "basic") == True
    assert has_feature(user, "advanced") == True
    assert has_feature(user, "premium") == False
```

## 🔧 API Reference

### Core Functions

- `initialize_paygate(plans)` - Initialize with your plan configuration
- `has_feature(user, feature)` - Check if user has access to a feature
- `get_limit(user, feature)` - Get usage limit for a feature
- `requires_feature(feature)` - Decorator for feature gating
- `requires_feature_with_limit(feature)` - Decorator with usage limiting

### Models

- `SubscriptionMixin` - SQLAlchemy mixin for user models

### Webhook Handling

- `handle_webhook(request)` - Process Paddle webhooks
- `create_paddle_router()` - Create FastAPI router with webhook endpoint
- `set_user_handlers(lookup, update)` - Configure user management functions

## 🗺️ Roadmap

- [ ] Stripe integration
- [ ] Admin override UI
- [ ] Plan hierarchy system
- [ ] Paddle Checkout helpers
- [ ] Analytics and reporting
- [ ] Feature flags integration

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests. 