"""
SQLAlchemy mixin for subscription management.
Applications extend their User model with SubscriptionMixin.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column


class SubscriptionMixin:
    """
    SQLAlchemy mixin that adds subscription fields to a User model.
    
    Usage:
        class User(Base, SubscriptionMixin):
            id: Mapped[int] = mapped_column(primary_key=True)
            email: Mapped[str] = mapped_column(String(255))
            # ... other user fields
    """
    
    subscription_plan: Mapped[str] = mapped_column(
        String(50), 
        default="free",
        nullable=False,
        doc="Current subscription plan name"
    )
    
    subscription_status: Mapped[str] = mapped_column(
        String(20),
        default="active", 
        nullable=False,
        doc="Subscription status: active, canceled, past_due, etc."
    )
    
    subscription_ends_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the subscription expires (None for lifetime/free plans)"
    )
    
    subscription_provider: Mapped[str] = mapped_column(
        String(20),
        default="paddle",
        nullable=False,
        doc="Payment provider: paddle, stripe, etc."
    )
    
    paddle_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        doc="Paddle subscription ID for webhook correlation"
    )
    
    paddle_customer_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Paddle customer ID"
    )
    
    # Metadata fields
    subscription_created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the subscription was first created"
    )
    
    subscription_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Last time subscription was updated"
    )
    
    def is_subscription_active(self) -> bool:
        """Check if the subscription is currently active."""
        if self.subscription_status != "active":
            return False
            
        if self.subscription_ends_at is None:
            return True  # Lifetime or free plan
            
        return datetime.utcnow() < self.subscription_ends_at
    
    def days_until_expiry(self) -> Optional[int]:
        """Get number of days until subscription expires."""
        if self.subscription_ends_at is None:
            return None
            
        delta = self.subscription_ends_at - datetime.utcnow()
        return max(0, delta.days) 