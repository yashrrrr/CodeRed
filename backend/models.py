"""
SQLAlchemy ORM models for the Learner Engagement Platform.
Defines Learner, Nudge, and Event models with async patterns.
"""

from sqlalchemy import String, Float, Integer, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.lib_db import Base

class Learner(Base):
    """
    Learner model representing a student in the platform.
    Stores engagement metrics and computed risk assessment data.
    """
    __tablename__ = "learners"
    
    # Primary key - using string for easier CSV import and debugging
    id: Mapped[str] = mapped_column(String, primary_key=True)
    
    # Basic learner information
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String)
    program: Mapped[str] = mapped_column(String, nullable=False)
    
    # Engagement metrics
    last_login: Mapped[Optional[str]] = mapped_column(String)  # ISO format datetime string
    completed_percent: Mapped[float] = mapped_column(Float, default=0.0)
    avg_quiz_score: Mapped[float] = mapped_column(Float, default=0.0)
    consecutive_missed_sessions: Mapped[int] = mapped_column(Integer, default=0)
    
    # Computed risk assessment fields
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_label: Mapped[str] = mapped_column(String, default="low")
    
    # Relationships
    nudges: Mapped[List["Nudge"]] = relationship("Nudge", back_populates="learner", cascade="all, delete-orphan")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="learner", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Learner(id='{self.id}', name='{self.name}', risk_label='{self.risk_label}')>"

class Nudge(Base):
    """
    Nudge model representing generated interventions for learners.
    Tracks AI-generated content and delivery metadata.
    """
    __tablename__ = "nudges"
    
    # Primary key
    id: Mapped[str] = mapped_column(String, primary_key=True)
    
    # Foreign key to learner
    learner_id: Mapped[str] = mapped_column(String, ForeignKey("learners.id"), nullable=False)
    
    # Nudge configuration
    channel: Mapped[str] = mapped_column(String, nullable=False)  # in-app, whatsapp, email
    type: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # AI generation metadata
    gpt_prompt_version: Mapped[Optional[str]] = mapped_column(String)
    gpt_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Status and timing
    status: Mapped[str] = mapped_column(String, default="generated")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship
    learner: Mapped["Learner"] = relationship("Learner", back_populates="nudges")
    
    def __repr__(self) -> str:
        return f"<Nudge(id='{self.id}', learner_id='{self.learner_id}', channel='{self.channel}')>"

class Event(Base):
    """
    Event model for tracking learner activities and system interactions.
    Provides flexible metadata storage for analytics and debugging.
    """
    __tablename__ = "events"
    
    # Primary key
    id: Mapped[str] = mapped_column(String, primary_key=True)
    
    # Foreign key to learner
    learner_id: Mapped[str] = mapped_column(String, ForeignKey("learners.id"), nullable=False)
    
    # Event details
    type: Mapped[str] = mapped_column(String, nullable=False)  # login, quiz_completed, nudge_sent, etc.
    event_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # Flexible event data
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship
    learner: Mapped["Learner"] = relationship("Learner", back_populates="events")
    
    def __repr__(self) -> str:
        return f"<Event(id='{self.id}', learner_id='{self.learner_id}', type='{self.type}')>"