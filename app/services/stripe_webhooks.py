from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
import stripe
import json
import logging
from datetime import datetime
from typing import Dict, Any
import os

from ..database import SessionLocal
from ..models import User
from ..config import settings

logger = logging.getLogger(__name__)


class StripeWebhookManager:
    """Manages Stripe webhook events and processing"""
    
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = os.getenv('STRIPE_SECRET_KEY', settings.stripe_secret_key)
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', settings.stripe_webhook_secret)
        
    async def handle_webhook(self, request: Request) -> Dict[str, Any]:
        """Main webhook handler that processes Stripe events"""
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        if not sig_header:
            logger.error("Missing Stripe signature header")
            raise HTTPException(status_code=400, detail="Missing signature")
        
        if not self.webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET not configured")
            raise HTTPException(status_code=500, detail="Webhook secret not configured")
        
        try:
            # Verify webhook signature
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Process event based on type
        event_type = event['type']
        event_data = event['data']['object']
        
        logger.info(f"Processing Stripe webhook: {event_type}")
        
        try:
            if event_type == 'checkout.session.completed':
                await self._handle_checkout_completed(event_data)
            elif event_type == 'customer.subscription.created':
                await self._handle_subscription_created(event_data)
            elif event_type == 'customer.subscription.updated':
                await self._handle_subscription_updated(event_data)
            elif event_type == 'customer.subscription.deleted':
                await self._handle_subscription_deleted(event_data)
            elif event_type == 'invoice.payment_succeeded':
                await self._handle_payment_succeeded(event_data)
            elif event_type == 'invoice.payment_failed':
                await self._handle_payment_failed(event_data)
            else:
                logger.info(f"Unhandled event type: {event_type}")
        except Exception as e:
            logger.error(f"Error processing {event_type}: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing event: {str(e)}")
        
        return {"status": "success", "event_type": event_type}
    
    async def _handle_checkout_completed(self, session: Dict[str, Any]):
        """Handle successful checkout session completion"""
        customer_email = session.get('customer_email')
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')
        metadata = session.get('metadata', {})
        user_id = metadata.get('user_id')
        
        logger.info(f"Checkout completed for customer {customer_email} (user_id: {user_id})")
        
        # Get database session
        db = SessionLocal()
        try:
            # Find user and update their Stripe customer ID
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.stripe_customer_id = customer_id
                    user.stripe_subscription_id = subscription_id
                    user.subscription_status = 'active'
                    user.subscription_updated_at = datetime.utcnow()
                    db.commit()
                    logger.info(f"Updated user {user_id} with Stripe customer {customer_id}")
                else:
                    logger.warning(f"User {user_id} not found for checkout completion")
        except Exception as e:
            logger.error(f"Database error in checkout completion: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _handle_subscription_created(self, subscription: Dict[str, Any]):
        """Handle new subscription creation"""
        customer_id = subscription.get('customer')
        subscription_id = subscription.get('id')
        status = subscription.get('status')
        current_period_end = subscription.get('current_period_end')
        
        logger.info(f"Subscription {subscription_id} created for customer {customer_id}")
        
        # Update user subscription in database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                user.stripe_subscription_id = subscription_id
                user.subscription_status = status
                user.subscription_period_end = datetime.fromtimestamp(current_period_end) if current_period_end else None
                user.subscription_updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Updated subscription for user {user.id}")
            else:
                logger.warning(f"No user found for customer {customer_id}")
        except Exception as e:
            logger.error(f"Database error in subscription creation: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _handle_subscription_updated(self, subscription: Dict[str, Any]):
        """Handle subscription updates (plan changes, renewals, etc.)"""
        customer_id = subscription.get('customer')
        subscription_id = subscription.get('id')
        status = subscription.get('status')
        current_period_end = subscription.get('current_period_end')
        
        logger.info(f"Subscription {subscription_id} updated for customer {customer_id}")
        
        # Update user subscription in database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                user.stripe_subscription_id = subscription_id
                user.subscription_status = status
                user.subscription_period_end = datetime.fromtimestamp(current_period_end) if current_period_end else None
                user.subscription_updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Updated subscription for user {user.id}")
            else:
                logger.warning(f"No user found for customer {customer_id}")
        except Exception as e:
            logger.error(f"Database error in subscription update: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _handle_subscription_deleted(self, subscription: Dict[str, Any]):
        """Handle subscription cancellation"""
        customer_id = subscription.get('customer')
        subscription_id = subscription.get('id')
        
        logger.info(f"Subscription {subscription_id} cancelled for customer {customer_id}")
        
        # Update user subscription in database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                user.subscription_status = 'cancelled'
                user.subscription_updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Cancelled subscription for user {user.id}")
            else:
                logger.warning(f"No user found for customer {customer_id}")
        except Exception as e:
            logger.error(f"Database error in subscription cancellation: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _handle_payment_succeeded(self, invoice: Dict[str, Any]):
        """Handle successful payment"""
        customer_id = invoice.get('customer')
        amount_paid = invoice.get('amount_paid', 0) / 100  # Convert from cents
        
        logger.info(f"Payment succeeded for customer {customer_id}: ${amount_paid}")
        
        # Update user's subscription status to active on successful payment
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                user.subscription_status = 'active'
                user.subscription_updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Updated payment status for user {user.id}")
            else:
                logger.warning(f"No user found for customer {customer_id}")
        except Exception as e:
            logger.error(f"Database error in payment success: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _handle_payment_failed(self, invoice: Dict[str, Any]):
        """Handle failed payment"""
        customer_id = invoice.get('customer')
        
        logger.warning(f"Payment failed for customer {customer_id}")
        
        # Update user subscription status
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                user.subscription_status = 'past_due'
                user.subscription_updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Marked subscription as past_due for user {user.id}")
            else:
                logger.warning(f"No user found for customer {customer_id}")
        except Exception as e:
            logger.error(f"Database error in payment failure: {e}")
            db.rollback()
            raise
        finally:
            db.close()