"""
Robust Stripe Webhook Handler
Handles payment events with comprehensive error handling and recovery
"""

import logging
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

import stripe
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session

from .config import settings
from .database_manager import db_manager, retry_on_database_error
from .models import User

logger = logging.getLogger(__name__)

class StripeWebhookManager:
    """Manages Stripe webhook processing with robust error handling"""
    
    def __init__(self):
        self.webhook_secret = settings.stripe_webhook_secret
        self.stripe_key = settings.stripe_secret_key
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize Stripe webhook manager"""
        try:
            if not self.stripe_key:
                logger.warning("⚠️ Stripe secret key not configured")
                return False
            
            stripe.api_key = self.stripe_key
            self.initialized = True
            logger.info("✅ Stripe webhook manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stripe webhook manager initialization failed: {e}")
            return False
    
    async def handle_webhook(self, request: Request) -> Dict[str, Any]:
        """Handle incoming Stripe webhook with comprehensive error handling"""
        try:
            if not self.initialized:
                logger.error("❌ Stripe webhook manager not initialized")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Payment system temporarily unavailable"
                )
            
            # Get request body and signature
            payload = await request.body()
            sig_header = request.headers.get('stripe-signature')
            
            if not sig_header:
                logger.error("❌ Missing Stripe signature header")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing signature header"
                )
            
            # Verify webhook signature
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, self.webhook_secret
                )
            except ValueError:
                logger.error("❌ Invalid webhook payload")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid payload"
                )
            except stripe.error.SignatureVerificationError:
                logger.error("❌ Invalid webhook signature")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid signature"
                )
            
            # Log the event
            logger.info(f"📥 Received Stripe webhook: {event['type']} (ID: {event['id']})")
            
            # Process the event
            result = await self._process_webhook_event(event)
            
            logger.info(f"✅ Webhook processed successfully: {event['type']}")
            return {"status": "success", "event_type": event['type'], "result": result}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Webhook processing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Webhook processing failed"
            )
    
    async def _process_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual webhook events"""
        event_type = event['type']
        event_data = event['data']['object']
        
        try:
            if event_type == 'checkout.session.completed':
                return await self._handle_checkout_completed(event_data)
            elif event_type == 'invoice.payment_succeeded':
                return await self._handle_payment_succeeded(event_data)
            elif event_type == 'invoice.payment_failed':
                return await self._handle_payment_failed(event_data)
            elif event_type == 'customer.subscription.updated':
                return await self._handle_subscription_updated(event_data)
            elif event_type == 'customer.subscription.deleted':
                return await self._handle_subscription_cancelled(event_data)
            else:
                logger.info(f"ℹ️ Unhandled webhook event type: {event_type}")
                return {"status": "ignored", "reason": "unhandled_event_type"}
                
        except Exception as e:
            logger.error(f"❌ Event processing failed for {event_type}: {e}")
            raise
    
    @retry_on_database_error(max_retries=3, delay=1.0)
    async def _handle_checkout_completed(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful checkout completion"""
        try:
            customer_id = session_data.get('customer')
            subscription_id = session_data.get('subscription')
            
            if not customer_id:
                logger.error("❌ No customer ID in checkout session")
                return {"status": "error", "reason": "missing_customer_id"}
            
            # Find user by customer ID
            with db_manager.get_db_session() as db:
                user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
                
                if not user:
                    logger.error(f"❌ User not found for customer ID: {customer_id}")
                    return {"status": "error", "reason": "user_not_found"}
                
                # Update user subscription status
                user.subscription_status = "active"
                if subscription_id:
                    # Get subscription details from Stripe
                    subscription = stripe.Subscription.retrieve(subscription_id)
                    user.subscription_plan = self._get_plan_name_from_price_id(
                        subscription['items']['data'][0]['price']['id']
                    )
                    user.subscription_period_end = datetime.fromtimestamp(
                        subscription['current_period_end']
                    )
                
                db.commit()
                
                logger.info(f"✅ Checkout completed for user {user.id}")
                return {
                    "status": "success",
                    "user_id": user.id,
                    "subscription_status": user.subscription_status
                }
                
        except Exception as e:
            logger.error(f"❌ Checkout completion handling failed: {e}")
            raise
    
    @retry_on_database_error(max_retries=3, delay=1.0)
    async def _handle_payment_succeeded(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment"""
        try:
            customer_id = invoice_data.get('customer')
            subscription_id = invoice_data.get('subscription')
            
            if not customer_id:
                return {"status": "error", "reason": "missing_customer_id"}
            
            with db_manager.get_db_session() as db:
                user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
                
                if not user:
                    logger.warning(f"⚠️ User not found for customer ID: {customer_id}")
                    return {"status": "warning", "reason": "user_not_found"}
                
                # Update subscription status and period
                user.subscription_status = "active"
                
                if subscription_id:
                    subscription = stripe.Subscription.retrieve(subscription_id)
                    user.subscription_period_end = datetime.fromtimestamp(
                        subscription['current_period_end']
                    )
                
                db.commit()
                
                logger.info(f"✅ Payment succeeded for user {user.id}")
                return {"status": "success", "user_id": user.id}
                
        except Exception as e:
            logger.error(f"❌ Payment success handling failed: {e}")
            raise
    
    @retry_on_database_error(max_retries=3, delay=1.0)
    async def _handle_payment_failed(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment"""
        try:
            customer_id = invoice_data.get('customer')
            
            if not customer_id:
                return {"status": "error", "reason": "missing_customer_id"}
            
            with db_manager.get_db_session() as db:
                user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
                
                if not user:
                    logger.warning(f"⚠️ User not found for customer ID: {customer_id}")
                    return {"status": "warning", "reason": "user_not_found"}
                
                # Update subscription status
                user.subscription_status = "past_due"
                
                db.commit()
                
                logger.warning(f"⚠️ Payment failed for user {user.id}")
                return {"status": "success", "user_id": user.id, "action": "marked_past_due"}
                
        except Exception as e:
            logger.error(f"❌ Payment failure handling failed: {e}")
            raise
    
    @retry_on_database_error(max_retries=3, delay=1.0)
    async def _handle_subscription_updated(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updates"""
        try:
            customer_id = subscription_data.get('customer')
            status = subscription_data.get('status')
            
            if not customer_id:
                return {"status": "error", "reason": "missing_customer_id"}
            
            with db_manager.get_db_session() as db:
                user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
                
                if not user:
                    logger.warning(f"⚠️ User not found for customer ID: {customer_id}")
                    return {"status": "warning", "reason": "user_not_found"}
                
                # Update subscription details
                user.subscription_status = status
                user.subscription_period_end = datetime.fromtimestamp(
                    subscription_data['current_period_end']
                )
                
                # Update plan if price changed
                if subscription_data.get('items', {}).get('data'):
                    price_id = subscription_data['items']['data'][0]['price']['id']
                    user.subscription_plan = self._get_plan_name_from_price_id(price_id)
                
                db.commit()
                
                logger.info(f"✅ Subscription updated for user {user.id}: {status}")
                return {"status": "success", "user_id": user.id, "new_status": status}
                
        except Exception as e:
            logger.error(f"❌ Subscription update handling failed: {e}")
            raise
    
    @retry_on_database_error(max_retries=3, delay=1.0)
    async def _handle_subscription_cancelled(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription cancellation"""
        try:
            customer_id = subscription_data.get('customer')
            
            if not customer_id:
                return {"status": "error", "reason": "missing_customer_id"}
            
            with db_manager.get_db_session() as db:
                user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
                
                if not user:
                    logger.warning(f"⚠️ User not found for customer ID: {customer_id}")
                    return {"status": "warning", "reason": "user_not_found"}
                
                # Update subscription status
                user.subscription_status = "cancelled"
                user.subscription_plan = "free"
                
                db.commit()
                
                logger.info(f"✅ Subscription cancelled for user {user.id}")
                return {"status": "success", "user_id": user.id, "action": "cancelled"}
                
        except Exception as e:
            logger.error(f"❌ Subscription cancellation handling failed: {e}")
            raise
    
    def _get_plan_name_from_price_id(self, price_id: str) -> str:
        """Get plan name from Stripe price ID"""
        # This would typically map price IDs to plan names
        # For now, return a default
        plan_mapping = {
            # Add your actual price IDs here
            "price_starter": "starter",
            "price_professional": "professional", 
            "price_enterprise": "enterprise"
        }
        
        return plan_mapping.get(price_id, "unknown")
    
    def get_webhook_health(self) -> Dict[str, Any]:
        """Get webhook system health status"""
        return {
            "initialized": self.initialized,
            "stripe_configured": bool(self.stripe_key),
            "webhook_secret_configured": bool(self.webhook_secret),
            "status": "healthy" if self.initialized else "degraded"
        }

# Global webhook manager
stripe_webhook_manager = StripeWebhookManager()