from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from .database import Base
from .database_utils import get_database_compatible_datetime
import uuid
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from .config import settings
import base64
import hashlib
import logging
from typing import Optional


logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firebase_uid = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String)
    photo_url = Column(String)
    
    google_access_token = Column(Text)  # Encrypted
    google_refresh_token = Column(Text)  # Encrypted
    token_expires_at = Column(DateTime)
    
    youtube_channel_id = Column(String)
    youtube_channel_title = Column(String)
    
    # Billing/Subscription fields
    stripe_customer_id = Column(String, nullable=True)
    subscription_status = Column(String, default="free")  # free, active, cancelled, past_due
    subscription_plan = Column(String, default="free")    # free, starter, professional, enterprise
    subscription_period_end = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=get_database_compatible_datetime())
    updated_at = Column(DateTime, server_default=get_database_compatible_datetime(), onupdate=get_database_compatible_datetime())
    is_active = Column(Boolean, default=True)
    
    ab_tests = relationship("ABTest", back_populates="user")
    youtube_channels = relationship("YouTubeChannel", back_populates="user")
    
    @staticmethod
    def _get_encryption_key() -> bytes:
        """Generate encryption key from secret key"""
        key_material = settings.secret_key.encode()
        digest = hashlib.sha256(key_material).digest()
        return base64.urlsafe_b64encode(digest)
    
    @classmethod
    def _encrypt_token(cls, token: Optional[str]) -> Optional[str]:
        """Encrypt a token for secure storage"""
        if not token:
            return None
        
        try:
            fernet = Fernet(cls._get_encryption_key())
            encrypted_token = fernet.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted_token).decode()
        except Exception as e:
            logger.error(f"Token encryption failed: {e}")
            raise ValueError("Failed to encrypt token")
    
    @classmethod
    def _decrypt_token(cls, encrypted_token: Optional[str]) -> Optional[str]:
        """Decrypt a token for use"""
        if not encrypted_token:
            return None
        
        if settings.is_development and encrypted_token in ["dev_access_token", "dev_refresh_token"]:
            return encrypted_token
        
        try:
            fernet = Fernet(cls._get_encryption_key())
            decoded_token = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted_token = fernet.decrypt(decoded_token)
            return decrypted_token.decode()
        except Exception as e:
            logger.error(f"Token decryption failed: {e}")
            return None
    
    def set_google_tokens(self, access_token: Optional[str], refresh_token: Optional[str] = None, expires_in: int = 3600):
        """Set encrypted Google OAuth tokens with expiration"""
        try:
            if access_token:
                self.google_access_token = self._encrypt_token(access_token)
            
            if refresh_token:
                self.google_refresh_token = self._encrypt_token(refresh_token)
            
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            self.updated_at = datetime.utcnow()
            
            logger.info(f"Updated OAuth tokens for user {self.id}")
            
        except Exception as e:
            logger.error(f"Failed to set Google tokens for user {self.id}: {e}")
            raise ValueError("Failed to store authentication tokens")
    
    def get_google_access_token(self) -> Optional[str]:
        """Get decrypted Google access token"""
        logger.debug(f"Getting access token for user {self.id}")
        
        if not self.google_access_token:
            logger.warning(f"User {self.id} has no encrypted access token stored")
            return None
            
        if self.is_token_expired():
            logger.warning(f"User {self.id} access token is expired (expires at: {self.token_expires_at})")
            
        decrypted_token = self._decrypt_token(self.google_access_token)
        if decrypted_token:
            logger.debug(f"Successfully decrypted access token for user {self.id}")
        else:
            logger.error(f"Failed to decrypt access token for user {self.id}")
            
        return decrypted_token
    
    def get_google_refresh_token(self) -> Optional[str]:
        """Get decrypted Google refresh token"""
        logger.debug(f"Getting refresh token for user {self.id}")
        
        if not self.google_refresh_token:
            logger.warning(f"User {self.id} has no encrypted refresh token stored")
            return None
            
        decrypted_token = self._decrypt_token(self.google_refresh_token)
        if decrypted_token:
            logger.debug(f"Successfully decrypted refresh token for user {self.id}")
        else:
            logger.error(f"Failed to decrypt refresh token for user {self.id}")
            
        return decrypted_token
    
    def is_token_expired(self) -> bool:
        """Check if the access token is expired or will expire soon"""
        if not self.token_expires_at:
            return True
        
        buffer_time = timedelta(minutes=5)
        return datetime.utcnow() + buffer_time >= self.token_expires_at
    
    def clear_google_tokens(self):
        """Clear all Google OAuth tokens"""
        self.google_access_token = None
        self.google_refresh_token = None
        self.token_expires_at = None
        self.updated_at = datetime.utcnow()
        
        logger.info(f"Cleared OAuth tokens for user {self.id}")
    
    def has_valid_tokens(self) -> bool:
        """Check if user has valid, non-expired tokens"""
        return (
            self.google_access_token is not None and 
            self.google_refresh_token is not None and 
            not self.is_token_expired()
        )
    
    def needs_token_refresh(self) -> bool:
        """Check if tokens need to be refreshed"""
        return (
            self.google_refresh_token is not None and 
            (self.google_access_token is None or self.is_token_expired())
        )
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            "id": self.id,
            "firebase_uid": self.firebase_uid,
            "email": self.email,
            "display_name": self.display_name,
            "photo_url": self.photo_url,
            "youtube_channel_id": self.youtube_channel_id,
            "youtube_channel_title": self.youtube_channel_title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "has_valid_tokens": self.has_valid_tokens(),
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
        }


class ABTest(Base):
    __tablename__ = "ab_tests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    video_id = Column(String, nullable=False)
    video_title = Column(String, nullable=False)
    
    title_variants = Column(JSON)  # List of title variants to test
    test_duration_hours = Column(Integer, default=24)
    rotation_interval_hours = Column(Integer, default=4)
    
    status = Column(String, default="draft")  # draft, active, paused, completed
    current_variant_index = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    results = Column(JSON)  # Store metrics for each variant
    winner_variant_index = Column(Integer)
    
    created_at = Column(DateTime, server_default=get_database_compatible_datetime())
    updated_at = Column(DateTime, server_default=get_database_compatible_datetime(), onupdate=get_database_compatible_datetime())
    
    user = relationship("User", back_populates="ab_tests")
    rotations = relationship("TitleRotation", back_populates="ab_test")


class TitleRotation(Base):
    __tablename__ = "title_rotations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ab_test_id = Column(String, ForeignKey("ab_tests.id"), nullable=False)
    
    variant_index = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    
    views_start = Column(Integer)
    views_end = Column(Integer)
    likes_start = Column(Integer)
    likes_end = Column(Integer)
    comments_start = Column(Integer)
    comments_end = Column(Integer)
    
    views_gained = Column(Integer)
    engagement_rate = Column(Float)
    
    created_at = Column(DateTime, server_default=get_database_compatible_datetime())
    
    ab_test = relationship("ABTest", back_populates="rotations")


class YouTubeChannel(Base):
    __tablename__ = "youtube_channels"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    channel_id = Column(String, nullable=False, unique=True, index=True)
    channel_title = Column(String, nullable=False)
    channel_description = Column(Text)
    
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    thumbnail_url = Column(String)
    custom_url = Column(String)
    
    is_active = Column(Boolean, default=True)
    is_selected = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=get_database_compatible_datetime())
    updated_at = Column(DateTime, server_default=get_database_compatible_datetime(), onupdate=get_database_compatible_datetime())
    
    user = relationship("User", back_populates="youtube_channels")
    
    def to_dict(self) -> dict:
        """Convert channel to dictionary"""
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "channel_title": self.channel_title,
            "channel_description": self.channel_description,
            "subscriber_count": self.subscriber_count,
            "video_count": self.video_count,
            "view_count": self.view_count,
            "thumbnail_url": self.thumbnail_url,
            "custom_url": self.custom_url,
            "is_active": self.is_active,
            "is_selected": self.is_selected,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class QuotaUsage(Base):
    __tablename__ = "quota_usage"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    date = Column(DateTime, nullable=False)
    api_calls_count = Column(Integer, default=0)
    quota_units_used = Column(Integer, default=0)
    
    videos_list_calls = Column(Integer, default=0)  # 1 unit each
    videos_update_calls = Column(Integer, default=0)  # 50 units each
    
    created_at = Column(DateTime, server_default=get_database_compatible_datetime())
    updated_at = Column(DateTime, server_default=get_database_compatible_datetime(), onupdate=get_database_compatible_datetime())
