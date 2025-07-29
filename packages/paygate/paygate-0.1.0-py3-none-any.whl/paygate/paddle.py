"""
Paddle webhook handler for subscription events.
"""

import json
import hmac
import hashlib
from datetime import datetime
from typing import Any, Dict, Optional, Callable, Awaitable

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

from .config import PADDLE_WEBHOOK_SECRET, PLANS


class PaddleWebhookEvent(BaseModel):
    """Pydantic model for Paddle webhook events."""
    alert_name: str
    alert_id: str
    subscription_id: Optional[str] = None
    subscription_plan_id: Optional[str] = None
    user_id: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    next_bill_date: Optional[str] = None
    subscription_payment_id: Optional[str] = None
    passthrough: Optional[str] = None


# Global handlers - will be set by the consuming application
_user_lookup_handler: Optional[Callable[[str], Awaitable[Any]]] = None
_user_update_handler: Optional[Callable[[Any, Dict[str, Any]], Awaitable[None]]] = None


def set_user_handlers(
    lookup_handler: Callable[[str], Awaitable[Any]],
    update_handler: Callable[[Any, Dict[str, Any]], Awaitable[None]]
) -> None:
    """
    Set the user lookup and update handlers.
    
    Args:
        lookup_handler: Async function to find user by email or paddle_subscription_id
        update_handler: Async function to update user subscription data
    """
    global _user_lookup_handler, _user_update_handler
    _user_lookup_handler = lookup_handler
    _user_update_handler = update_handler


def verify_paddle_webhook(request_body: bytes, signature: str) -> bool:
    """
    Verify Paddle webhook signature.
    
    Args:
        request_body: Raw request body
        signature: Paddle signature from headers
        
    Returns:
        True if signature is valid
    """
    if not PADDLE_WEBHOOK_SECRET:
        # In development, you might want to skip verification
        return True
        
    # Paddle sends signature as 'sha1=<hash>'
    if signature.startswith('sha1='):
        signature = signature[5:]
    
    expected_signature = hmac.new(
        PADDLE_WEBHOOK_SECRET.encode('utf-8'),
        request_body,
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def get_plan_from_paddle_product_id(product_id: str) -> Optional[str]:
    """
    Map Paddle product ID to internal plan name.
    
    Args:
        product_id: Paddle product ID
        
    Returns:
        Internal plan name or None if not found
    """
    for plan_name, plan_config in PLANS.items():
        if plan_config.get("paddle_product_id") == product_id:
            return plan_name
    return None


async def process_subscription_created(event_data: Dict[str, Any]) -> None:
    """Process subscription_created webhook event."""
    if not _user_lookup_handler or not _user_update_handler:
        raise HTTPException(500, "User handlers not configured")
    
    email = event_data.get("email")
    subscription_id = event_data.get("subscription_id")
    product_id = event_data.get("subscription_plan_id")
    
    if not email or not subscription_id:
        raise HTTPException(400, "Missing required fields in webhook")
    
    # Find user by email
    user = await _user_lookup_handler(email)
    if not user:
        raise HTTPException(404, f"User not found: {email}")
    
    # Determine plan from product ID
    plan = get_plan_from_paddle_product_id(product_id) if product_id else "free"
    
    # Parse next bill date
    next_bill_date = None
    if event_data.get("next_bill_date"):
        try:
            next_bill_date = datetime.fromisoformat(
                event_data["next_bill_date"].replace("Z", "+00:00")
            )
        except ValueError:
            pass
    
    # Update user subscription
    update_data = {
        "subscription_plan": plan or "free",
        "subscription_status": "active",
        "subscription_ends_at": next_bill_date,
        "paddle_subscription_id": subscription_id,
        "paddle_customer_id": event_data.get("user_id"),
        "subscription_created_at": datetime.utcnow(),
        "subscription_updated_at": datetime.utcnow(),
    }
    
    await _user_update_handler(user, update_data)


async def process_subscription_updated(event_data: Dict[str, Any]) -> None:
    """Process subscription_updated webhook event."""
    if not _user_lookup_handler or not _user_update_handler:
        raise HTTPException(500, "User handlers not configured")
    
    subscription_id = event_data.get("subscription_id")
    if not subscription_id:
        raise HTTPException(400, "Missing subscription_id in webhook")
    
    # Find user by subscription ID
    user = await _user_lookup_handler(subscription_id)
    if not user:
        raise HTTPException(404, f"User not found for subscription: {subscription_id}")
    
    # Update subscription data
    update_data = {"subscription_updated_at": datetime.utcnow()}
    
    if "status" in event_data:
        update_data["subscription_status"] = event_data["status"]
    
    if "next_bill_date" in event_data:
        try:
            update_data["subscription_ends_at"] = datetime.fromisoformat(
                event_data["next_bill_date"].replace("Z", "+00:00")
            )
        except ValueError:
            pass
    
    if "subscription_plan_id" in event_data:
        plan = get_plan_from_paddle_product_id(event_data["subscription_plan_id"])
        if plan:
            update_data["subscription_plan"] = plan
    
    await _user_update_handler(user, update_data)


async def process_subscription_cancelled(event_data: Dict[str, Any]) -> None:
    """Process subscription_cancelled webhook event."""
    if not _user_lookup_handler or not _user_update_handler:
        raise HTTPException(500, "User handlers not configured")
    
    subscription_id = event_data.get("subscription_id")
    if not subscription_id:
        raise HTTPException(400, "Missing subscription_id in webhook")
    
    user = await _user_lookup_handler(subscription_id)
    if not user:
        raise HTTPException(404, f"User not found for subscription: {subscription_id}")
    
    # Update to cancelled status but keep end date
    update_data = {
        "subscription_status": "cancelled",
        "subscription_updated_at": datetime.utcnow(),
    }
    
    await _user_update_handler(user, update_data)


# Event handlers mapping
WEBHOOK_HANDLERS = {
    "subscription_created": process_subscription_created,
    "subscription_updated": process_subscription_updated,
    "subscription_cancelled": process_subscription_cancelled,
    "subscription_payment_succeeded": process_subscription_updated,
    "subscription_payment_failed": process_subscription_updated,
}


async def handle_webhook(request: Request) -> Dict[str, str]:
    """
    Main webhook handler function.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Success response dictionary
    """
    # Get raw body and signature
    body = await request.body()
    signature = request.headers.get("X-Paddle-Signature", "")
    
    # Verify signature
    if not verify_paddle_webhook(body, signature):
        raise HTTPException(400, "Invalid webhook signature")
    
    # Parse webhook data
    try:
        # Paddle sends form-encoded data
        form_data = await request.form()
        alert_name = form_data.get("alert_name")
        
        if not alert_name:
            raise HTTPException(400, "Missing alert_name in webhook")
        
        # Convert form data to dict
        event_data = dict(form_data)
        
        # Handle the event
        handler = WEBHOOK_HANDLERS.get(alert_name)
        if handler:
            await handler(event_data)
        else:
            print(f"Unhandled webhook event: {alert_name}")
    
    except Exception as e:
        print(f"Webhook processing error: {e}")
        raise HTTPException(500, f"Webhook processing failed: {str(e)}")
    
    return {"status": "success"}


def create_paddle_router() -> APIRouter:
    """
    Create a FastAPI router with the Paddle webhook endpoint.
    
    Returns:
        APIRouter with /webhook/paddle endpoint
    """
    router = APIRouter()
    
    @router.post("/webhook/paddle")
    async def paddle_webhook(request: Request) -> Dict[str, str]:
        """Paddle webhook endpoint."""
        return await handle_webhook(request)
    
    return router 