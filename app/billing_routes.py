from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging
import stripe
import os

from .config import settings
from .database import get_db
from .models import User
from .auth_dependencies import get_current_firebase_user
from .services.stripe_webhooks import StripeWebhookManager

logger = logging.getLogger(__name__)
router = APIRouter()
webhooks = StripeWebhookManager()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class CreateCheckoutSessionRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str

class SubscriptionInfo(BaseModel):
    status: str
    current_period_end: Optional[datetime]
    plan_name: Optional[str]
    plan_price: Optional[float]

# Pricing tiers
PRICING_PLANS = {
    "starter": {
        "name": "Starter",
        "price": 29.00,
        "tests_limit": 10,
        "features": ["Basic A/B testing", "5 YouTube channels", "Basic analytics"]
    },
    "professional": {
        "name": "Professional", 
        "price": 79.00,
        "tests_limit": 50,
        "features": ["Advanced A/B testing", "Unlimited channels", "Detailed analytics", "Priority support"]
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 199.00,
        "tests_limit": -1,  # Unlimited
        "features": ["Unlimited testing", "Custom integrations", "Dedicated support", "Advanced reporting"]
    }
}

@router.get("/billing/plans")
async def get_pricing_plans():
    """Get available pricing plans"""
    return {"plans": PRICING_PLANS}

@router.get("/billing/subscription")
async def get_subscription_info(
    current_user: User = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription information"""
    try:
        # For now, return basic info - extend when Stripe is integrated
        subscription_info = {
            "status": "free",
            "current_period_end": None,
            "plan_name": "Free",
            "plan_price": 0.00,
            "tests_used": 0,
            "tests_limit": 3,  # Free tier limit
            "features": ["3 A/B tests", "1 YouTube channel", "Basic analytics"]
        }
        
        # TODO: Integrate with Stripe to get real subscription data
        # if current_user.stripe_customer_id:
        #     stripe_customer = stripe.Customer.retrieve(current_user.stripe_customer_id)
        #     # Process Stripe subscription data
        
        return subscription_info
        
    except Exception as e:
        logger.error(f"Error fetching subscription info for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription information"
        )

@router.post("/billing/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_user: User = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session for subscription"""
    
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Billing system not configured. Please contact support."
        )
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': request.price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            customer_email=current_user.email,
            metadata={
                'user_id': current_user.id,
                'firebase_uid': current_user.firebase_uid
            }
        )
        
        return {"checkout_url": checkout_session.url}
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create checkout session"
        )
    except Exception as e:
        logger.error(f"Error creating checkout session for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )

@router.post("/billing/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        return await webhooks.handle_webhook(request)
    except Exception as e:
        import logging; logging.exception("stripe webhook error")
        raise HTTPException(status_code=400, detail="Webhook error")

@router.get("/billing/usage")
async def get_usage_info(
    current_user: User = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """Get current user's usage information"""
    try:
        # Count user's A/B tests
        from .models import ABTest
        active_tests = db.query(ABTest).filter(
            ABTest.user_id == current_user.id,
            ABTest.is_active == True
        ).count()
        
        total_tests = db.query(ABTest).filter(
            ABTest.user_id == current_user.id
        ).count()
        
        return {
            "active_tests": active_tests,
            "total_tests": total_tests,
            "tests_limit": 3,  # Free tier limit - TODO: Get from subscription
            "usage_percentage": min((active_tests / 3) * 100, 100),
            "can_create_test": active_tests < 3
        }
        
    except Exception as e:
        logger.error(f"Error fetching usage info for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch usage information"
        )