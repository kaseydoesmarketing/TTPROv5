from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid


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
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    ab_tests = relationship("ABTest", back_populates="user")


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
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
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
    
    created_at = Column(DateTime, server_default=func.now())
    
    ab_test = relationship("ABTest", back_populates="rotations")


class QuotaUsage(Base):
    __tablename__ = "quota_usage"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    date = Column(DateTime, nullable=False)
    api_calls_count = Column(Integer, default=0)
    quota_units_used = Column(Integer, default=0)
    
    videos_list_calls = Column(Integer, default=0)  # 1 unit each
    videos_update_calls = Column(Integer, default=0)  # 50 units each
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
