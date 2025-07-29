"""
Usage limiting functionality for feature gating.
This module provides tools to track and enforce usage limits.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Protocol
from functools import wraps

from fastapi import HTTPException

from .features import get_limit, has_feature


class UsageStore(Protocol):
    """Protocol for usage storage backends."""
    
    async def get_usage(self, user_id: str, feature: str, period: str = "monthly") -> int:
        """Get current usage count for a user and feature."""
        ...
    
    async def increment_usage(self, user_id: str, feature: str, amount: int = 1, period: str = "monthly") -> int:
        """Increment usage count and return new total."""
        ...
    
    async def reset_usage(self, user_id: str, feature: str, period: str = "monthly") -> None:
        """Reset usage count for a user and feature."""
        ...


class MemoryUsageStore:
    """Simple in-memory usage store (not recommended for production)."""
    
    def __init__(self):
        self._usage: Dict[str, Dict[str, int]] = {}
        self._last_reset: Dict[str, datetime] = {}
    
    def _get_key(self, user_id: str, feature: str, period: str) -> str:
        return f"{user_id}:{feature}:{period}"
    
    async def get_usage(self, user_id: str, feature: str, period: str = "monthly") -> int:
        """Get current usage count."""
        key = self._get_key(user_id, feature, period)
        
        # Check if we need to reset for the period
        if self._should_reset(key, period):
            await self.reset_usage(user_id, feature, period)
        
        return self._usage.get(key, 0)
    
    async def increment_usage(self, user_id: str, feature: str, amount: int = 1, period: str = "monthly") -> int:
        """Increment usage count."""
        key = self._get_key(user_id, feature, period)
        
        # Check if we need to reset for the period
        if self._should_reset(key, period):
            await self.reset_usage(user_id, feature, period)
        
        current = self._usage.get(key, 0)
        new_usage = current + amount
        self._usage[key] = new_usage
        
        return new_usage
    
    async def reset_usage(self, user_id: str, feature: str, period: str = "monthly") -> None:
        """Reset usage count."""
        key = self._get_key(user_id, feature, period)
        self._usage[key] = 0
        self._last_reset[key] = datetime.utcnow()
    
    def _should_reset(self, key: str, period: str) -> bool:
        """Check if usage should be reset based on period."""
        last_reset = self._last_reset.get(key)
        if not last_reset:
            return True
        
        now = datetime.utcnow()
        
        if period == "daily":
            return (now - last_reset).days >= 1
        elif period == "monthly":
            return (now - last_reset).days >= 30
        elif period == "yearly":
            return (now - last_reset).days >= 365
        
        return False


class RedisUsageStore:
    """Redis-based usage store (requires redis package)."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def _get_key(self, user_id: str, feature: str, period: str) -> str:
        now = datetime.utcnow()
        
        if period == "daily":
            date_key = now.strftime("%Y-%m-%d")
        elif period == "monthly":
            date_key = now.strftime("%Y-%m")
        elif period == "yearly":
            date_key = now.strftime("%Y")
        else:
            date_key = period
        
        return f"usage:{user_id}:{feature}:{date_key}"
    
    def _get_ttl(self, period: str) -> int:
        """Get TTL in seconds for the period."""
        if period == "daily":
            return 86400  # 24 hours
        elif period == "monthly":
            return 2678400  # 31 days
        elif period == "yearly":
            return 31536000  # 365 days
        return 86400  # Default to daily
    
    async def get_usage(self, user_id: str, feature: str, period: str = "monthly") -> int:
        """Get current usage count."""
        key = self._get_key(user_id, feature, period)
        value = await self.redis.get(key)
        return int(value) if value else 0
    
    async def increment_usage(self, user_id: str, feature: str, amount: int = 1, period: str = "monthly") -> int:
        """Increment usage count."""
        key = self._get_key(user_id, feature, period)
        ttl = self._get_ttl(period)
        
        # Use Redis pipeline for atomicity
        async with self.redis.pipeline() as pipe:
            await pipe.incr(key, amount)
            await pipe.expire(key, ttl)
            results = await pipe.execute()
        
        return results[0]
    
    async def reset_usage(self, user_id: str, feature: str, period: str = "monthly") -> None:
        """Reset usage count."""
        key = self._get_key(user_id, feature, period)
        await self.redis.delete(key)


# Global usage store instance
_usage_store: Optional[UsageStore] = None


def set_usage_store(store: UsageStore) -> None:
    """Set the global usage store."""
    global _usage_store
    _usage_store = store


def get_usage_store() -> UsageStore:
    """Get the current usage store or create a default one."""
    global _usage_store
    if _usage_store is None:
        _usage_store = MemoryUsageStore()
    return _usage_store


async def get_user_usage(user_id: str, feature: str, period: str = "monthly") -> int:
    """Get current usage for a user and feature."""
    store = get_usage_store()
    return await store.get_usage(user_id, feature, period)


async def check_feature_limit(user: Any, feature: str, period: str = "monthly") -> bool:
    """
    Check if user is within the feature limit.
    
    Args:
        user: User object
        feature: Feature name to check
        period: Usage period (daily, monthly, yearly)
        
    Returns:
        True if user is within limit
    """
    # First check if user has the feature
    if not has_feature(user, feature):
        return False
    
    # Get the limit for this feature
    limit = get_limit(user, feature)
    if limit is None:
        return True  # No limit set
    
    # Get current usage
    user_id = str(getattr(user, "id", "unknown"))
    usage = await get_user_usage(user_id, feature, period)
    
    return usage < limit


async def increment_feature_usage(user: Any, feature: str, amount: int = 1, period: str = "monthly") -> int:
    """
    Increment usage for a feature and return new total.
    
    Args:
        user: User object
        feature: Feature name
        amount: Amount to increment by
        period: Usage period
        
    Returns:
        New usage total
    """
    user_id = str(getattr(user, "id", "unknown"))
    store = get_usage_store()
    return await store.increment_usage(user_id, feature, amount, period)


def requires_feature_with_limit(feature: str, period: str = "monthly", auto_increment: bool = True):
    """
    Decorator that checks both feature access and usage limits.
    
    Args:
        feature: Feature name required
        period: Usage period to check
        auto_increment: Whether to automatically increment usage on success
    
    Usage:
        @requires_feature_with_limit("ai_explain", period="monthly")
        async def explain_code(user: User = Depends(get_current_user)):
            # This will check both feature access and usage limits
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find user object in function parameters
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
                raise HTTPException(500, "No user object found in function parameters")
            
            # Check feature access
            if not has_feature(user, feature):
                raise HTTPException(403, f"Feature '{feature}' not available")
            
            # Check usage limits
            if not await check_feature_limit(user, feature, period):
                limit = get_limit(user, feature)
                usage = await get_user_usage(str(user.id), feature, period)
                raise HTTPException(
                    429,
                    detail=f"Feature '{feature}' limit exceeded. Used {usage}/{limit} for {period} period."
                )
            
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Increment usage if successful and auto_increment is enabled
            if auto_increment:
                await increment_feature_usage(user, feature, 1, period)
            
            return result
        
        return wrapper
    return decorator 


# --- MongoDB Usage Store (pymongo) ---
class MongoUsageStore:
    """
    MongoDB-based usage store (requires pymongo).
    Usage is tracked per user, feature, and period (e.g., monthly).
    Usage:
        from pymongo import MongoClient
        from paygate.limits import MongoUsageStore, set_usage_store
        client = MongoClient("mongodb://localhost:27017")
        collection = client["paygate"]["usage"]
        store = MongoUsageStore(collection)
        set_usage_store(store)
    """
    def __init__(self, collection):
        self.collection = collection

    async def get_usage(self, user_id: str, feature: str, period: str = "monthly") -> int:
        doc = await self.collection.find_one({"user_id": user_id, "feature": feature, "period": period})
        return doc["usage"] if doc and "usage" in doc else 0

    async def increment_usage(self, user_id: str, feature: str, amount: int = 1, period: str = "monthly") -> int:
        result = await self.collection.find_one_and_update(
            {"user_id": user_id, "feature": feature, "period": period},
            {"$inc": {"usage": amount}},
            upsert=True,
            return_document=True
        )
        return result["usage"] if result and "usage" in result else amount

    async def reset_usage(self, user_id: str, feature: str, period: str = "monthly") -> None:
        await self.collection.update_one(
            {"user_id": user_id, "feature": feature, "period": period},
            {"$set": {"usage": 0}},
            upsert=True
        )

# --- SQLAlchemy Usage Store (async) ---
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import declarative_base, mapped_column, Mapped

Base = declarative_base()

class UsageRecord(Base):
    __tablename__ = "paygate_usage"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str]
    feature: Mapped[str]
    period: Mapped[str]
    usage: Mapped[int]

class SQLAlchemyUsageStore:
    """
    SQLAlchemy-based usage store (async).
    Usage:
        from paygate.limits import SQLAlchemyUsageStore, set_usage_store
        store = SQLAlchemyUsageStore(session_factory)
        set_usage_store(store)
    """
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_usage(self, user_id: str, feature: str, period: str = "monthly") -> int:
        async with self.session_factory() as session:
            stmt = select(UsageRecord).where(
                UsageRecord.user_id == user_id,
                UsageRecord.feature == feature,
                UsageRecord.period == period
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            return record.usage if record else 0

    async def increment_usage(self, user_id: str, feature: str, amount: int = 1, period: str = "monthly") -> int:
        async with self.session_factory() as session:
            stmt = select(UsageRecord).where(
                UsageRecord.user_id == user_id,
                UsageRecord.feature == feature,
                UsageRecord.period == period
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            if record:
                record.usage += amount
            else:
                record = UsageRecord(user_id=user_id, feature=feature, period=period, usage=amount)
                session.add(record)
            await session.commit()
            return record.usage

    async def reset_usage(self, user_id: str, feature: str, period: str = "monthly") -> None:
        async with self.session_factory() as session:
            stmt = select(UsageRecord).where(
                UsageRecord.user_id == user_id,
                UsageRecord.feature == feature,
                UsageRecord.period == period
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            if record:
                record.usage = 0
                await session.commit()
            else:
                record = UsageRecord(user_id=user_id, feature=feature, period=period, usage=0)
                session.add(record)
                await session.commit() 