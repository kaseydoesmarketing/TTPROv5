from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


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
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
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
