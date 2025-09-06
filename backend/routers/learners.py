"""
Learners API router with endpoints for learner management and interventions.
Provides REST API endpoints with validation, error handling, and OpenAI integration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

# Import database and models
from ..lib_db import get_db
from ..models import Learner, Nudge, Event
from ..services.openai_client import generate_nudge, generate_quiz
from ..lib.risk import compute_risk, compute_and_update_all

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(tags=["learners"])

# Pydantic models for request/response validation

class LearnerResponse(BaseModel):
    """Response model for learner data with computed risk scores."""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    program: str
    last_login: Optional[str] = None
    completed_percent: float
    avg_quiz_score: float
    consecutive_missed_sessions: int
    risk_score: float
    risk_label: str
    
    class Config:
        from_attributes = True

class NudgeResponse(BaseModel):
    """Response model for nudge data."""
    id: str
    learner_id: str
    channel: str
    type: str
    content: str
    gpt_prompt_version: Optional[str] = None
    gpt_fallback: bool = False
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LearnerDetailResponse(LearnerResponse):
    """Extended learner response with nudge history."""
    nudges: List[NudgeResponse] = []

class NudgeRequest(BaseModel):
    """Request model for nudge generation."""
    channel: str = Field(..., description="Delivery channel for the nudge")
    type: str = Field(default="engagement", description="Type of nudge to generate")
    
    @validator('channel')
    def validate_channel(cls, v):
        valid_channels = ['in-app', 'whatsapp', 'email']
        if v not in valid_channels:
            raise ValueError(f'Channel must be one of: {", ".join(valid_channels)}')
        return v

class NudgeGenerationResponse(BaseModel):
    """Response model for nudge generation."""
    nudge_id: str
    content: str
    channel: str
    gpt_fallback: bool
    prompt_version: str

class QuizRequest(BaseModel):
    """Request model for quiz generation."""
    difficulty: Optional[str] = Field(default="medium", description="Quiz difficulty level")
    topic_focus: Optional[str] = Field(default=None, description="Specific topic to focus on")

class QuizResponse(BaseModel):
    """Response model for quiz generation."""
    content: Dict[str, Any]
    gpt_fallback: bool
    prompt_version: str

class SimulationRequest(BaseModel):
    """Request model for simulation runs."""
    auto_nudge: bool = Field(default=False, description="Automatically generate nudges for high-risk learners")
    risk_threshold: float = Field(default=0.7, description="Risk threshold for auto-nudge generation")

class SimulationResponse(BaseModel):
    """Response model for simulation results."""
    processed_learners: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    auto_nudges_generated: int = 0

# Helper functions

async def get_learner_by_id(db: AsyncSession, learner_id: str) -> Optional[Learner]:
    """Get learner by ID with error handling."""
    try:
        result = await db.execute(select(Learner).where(Learner.id == learner_id))
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Database error fetching learner {learner_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")

def learner_to_dict(learner: Learner) -> Dict[str, Any]:
    """Convert learner model to dictionary for risk computation."""
    return {
        'id': learner.id,
        'name': learner.name,
        'email': learner.email,
        'phone': learner.phone,
        'program': learner.program,
        'last_login': learner.last_login,
        'completed_percent': learner.completed_percent,
        'avg_quiz_score': learner.avg_quiz_score,
        'consecutive_missed_sessions': learner.consecutive_missed_sessions,
        'risk_score': learner.risk_score,
        'risk_label': learner.risk_label
    }

async def update_learner_risk(db: AsyncSession, learner: Learner, risk_data: Dict[str, Any]) -> None:
    """Update learner risk score and label in database."""
    try:
        await db.execute(
            update(Learner)
            .where(Learner.id == learner.id)
            .values(
                risk_score=risk_data['risk_score'],
                risk_label=risk_data['risk_label']
            )
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to update risk for learner {learner.id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update risk score")

# API Endpoints

@router.get("/learners", response_model=List[LearnerResponse])
async def get_learners(
    risk_filter: Optional[str] = Query(None, description="Filter by risk level: low, medium, high"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of learners to return"),
    offset: int = Query(0, ge=0, description="Number of learners to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of learners with computed risk scores and optional filtering.
    
    - **risk_filter**: Filter learners by risk level (low, medium, high)
    - **limit**: Maximum number of results (1-1000)
    - **offset**: Number of results to skip for pagination
    """
    try:
        # Build query with optional risk filtering
        query = select(Learner)
        
        if risk_filter:
            if risk_filter not in ['low', 'medium', 'high']:
                raise HTTPException(
                    status_code=400, 
                    detail="risk_filter must be one of: low, medium, high"
                )
            query = query.where(Learner.risk_label == risk_filter)
        
        # Add pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        learners = result.scalars().all()
        
        # Compute fresh risk scores for all learners
        learner_dicts = [learner_to_dict(learner) for learner in learners]
        updated_learners = compute_and_update_all(learner_dicts)
        
        # Update database with new risk scores
        for i, learner in enumerate(learners):
            if i < len(updated_learners):
                risk_data = updated_learners[i]
                learner.risk_score = risk_data['risk_score']
                learner.risk_label = risk_data['risk_label']
        
        # Commit risk score updates
        await db.commit()
        
        return [LearnerResponse.from_orm(learner) for learner in learners]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching learners: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/learners/{learner_id}", response_model=LearnerDetailResponse)
async def get_learner_detail(
    learner_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed learner information including nudge history.
    
    - **learner_id**: Unique identifier for the learner
    """
    learner = await get_learner_by_id(db, learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    
    try:
        # Compute fresh risk score
        learner_dict = learner_to_dict(learner)
        updated_learner = compute_risk(learner_dict)
        
        # Update learner object with fresh risk data
        learner.risk_score = updated_learner['risk_score']
        learner.risk_label = updated_learner['risk_label']
        
        # Update database
        await update_learner_risk(db, learner, updated_learner)
        
        # Fetch nudges for this learner
        nudges_result = await db.execute(
            select(Nudge)
            .where(Nudge.learner_id == learner_id)
            .order_by(Nudge.created_at.desc())
        )
        nudges = nudges_result.scalars().all()
        
        # Create response with nudges
        response_data = LearnerResponse.from_orm(learner).dict()
        response_data['nudges'] = [NudgeResponse.from_orm(nudge) for nudge in nudges]
        
        return LearnerDetailResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching learner detail for {learner_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/learners/{learner_id}/nudge", response_model=NudgeGenerationResponse)
async def generate_learner_nudge(
    learner_id: str,
    request: NudgeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate personalized nudge for a learner using OpenAI integration.
    
    - **learner_id**: Unique identifier for the learner
    - **channel**: Delivery channel (in-app, whatsapp, email)
    - **type**: Type of nudge to generate
    """
    learner = await get_learner_by_id(db, learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    
    try:
        # Prepare context for nudge generation
        context = {
            'name': learner.name,
            'channel': request.channel,
            'completed_percent': learner.completed_percent,
            'avg_quiz_score': learner.avg_quiz_score,
            'consecutive_missed_sessions': learner.consecutive_missed_sessions,
            'program': learner.program,
            'type': request.type
        }
        
        # Generate nudge using OpenAI service
        nudge_result = await generate_nudge(context)
        
        # Create nudge record in database
        nudge_id = str(uuid.uuid4())
        nudge = Nudge(
            id=nudge_id,
            learner_id=learner_id,
            channel=request.channel,
            type=request.type,
            content=nudge_result['content'],
            gpt_prompt_version=nudge_result['prompt_version'],
            gpt_fallback=nudge_result['gptFallback'],
            status='generated',
            created_at=datetime.utcnow()
        )
        
        db.add(nudge)
        await db.commit()
        
        # Log nudge generation event
        event = Event(
            id=str(uuid.uuid4()),
            learner_id=learner_id,
            type='nudge_generated',
            event_metadata={
                'nudge_id': nudge_id,
                'channel': request.channel,
                'gpt_fallback': nudge_result['gptFallback']
            },
            timestamp=datetime.utcnow()
        )
        
        db.add(event)
        await db.commit()
        
        return NudgeGenerationResponse(
            nudge_id=nudge_id,
            content=nudge_result['content'],
            channel=request.channel,
            gpt_fallback=nudge_result['gptFallback'],
            prompt_version=nudge_result['prompt_version']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating nudge for learner {learner_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to generate nudge")

@router.post("/learners/{learner_id}/quiz", response_model=QuizResponse)
async def generate_learner_quiz(
    learner_id: str,
    request: QuizRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate quiz content for a learner using OpenAI integration.
    
    - **learner_id**: Unique identifier for the learner
    - **difficulty**: Quiz difficulty level
    - **topic_focus**: Specific topic to focus on (optional)
    """
    learner = await get_learner_by_id(db, learner_id)
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    
    try:
        # Prepare context for quiz generation
        context = {
            'name': learner.name,
            'program': learner.program,
            'completed_percent': learner.completed_percent,
            'difficulty': request.difficulty,
            'topic_focus': request.topic_focus
        }
        
        # Generate quiz using OpenAI service
        quiz_result = await generate_quiz(context)
        
        # Log quiz generation event
        event = Event(
            id=str(uuid.uuid4()),
            learner_id=learner_id,
            type='quiz_generated',
            event_metadata={
                'difficulty': request.difficulty,
                'topic_focus': request.topic_focus,
                'gpt_fallback': quiz_result['gptFallback']
            },
            timestamp=datetime.utcnow()
        )
        
        db.add(event)
        await db.commit()
        
        return QuizResponse(
            content=quiz_result['content'],
            gpt_fallback=quiz_result['gptFallback'],
            prompt_version=quiz_result['prompt_version']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz for learner {learner_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to generate quiz")

@router.post("/simulate/run", response_model=SimulationResponse)
async def run_simulation(
    request: SimulationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Run batch risk recomputation for all learners with optional auto-nudge generation.
    
    - **auto_nudge**: Automatically generate nudges for high-risk learners
    - **risk_threshold**: Risk threshold for auto-nudge generation (0.0-1.0)
    """
    try:
        # Fetch all learners
        result = await db.execute(select(Learner))
        learners = result.scalars().all()
        
        if not learners:
            return SimulationResponse(
                processed_learners=0,
                high_risk_count=0,
                medium_risk_count=0,
                low_risk_count=0,
                auto_nudges_generated=0
            )
        
        # Convert to dictionaries for risk computation
        learner_dicts = [learner_to_dict(learner) for learner in learners]
        
        # Compute risk scores for all learners
        updated_learners = compute_and_update_all(learner_dicts)
        
        # Count risk levels and update database
        risk_counts = {'high': 0, 'medium': 0, 'low': 0}
        auto_nudges_generated = 0
        
        for i, learner in enumerate(learners):
            if i < len(updated_learners):
                risk_data = updated_learners[i]
                
                # Update learner risk data
                learner.risk_score = risk_data['risk_score']
                learner.risk_label = risk_data['risk_label']
                
                # Count risk levels
                risk_counts[risk_data['risk_label']] += 1
                
                # Generate auto-nudges if requested and learner is high-risk
                if (request.auto_nudge and 
                    risk_data['risk_score'] >= request.risk_threshold):
                    
                    try:
                        # Generate nudge for high-risk learner
                        context = {
                            'name': learner.name,
                            'channel': 'in-app',  # Default channel for auto-nudges
                            'completed_percent': learner.completed_percent,
                            'avg_quiz_score': learner.avg_quiz_score,
                            'consecutive_missed_sessions': learner.consecutive_missed_sessions,
                            'program': learner.program,
                            'type': 'risk_intervention'
                        }
                        
                        nudge_result = await generate_nudge(context)
                        
                        # Create nudge record
                        nudge = Nudge(
                            id=str(uuid.uuid4()),
                            learner_id=learner.id,
                            channel='in-app',
                            type='risk_intervention',
                            content=nudge_result['content'],
                            gpt_prompt_version=nudge_result['prompt_version'],
                            gpt_fallback=nudge_result['gptFallback'],
                            status='auto_generated',
                            created_at=datetime.utcnow()
                        )
                        
                        db.add(nudge)
                        auto_nudges_generated += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to generate auto-nudge for learner {learner.id}: {e}")
                        # Continue with other learners even if one fails
        
        # Commit all changes
        await db.commit()
        
        # Log simulation event
        event = Event(
            id=str(uuid.uuid4()),
            learner_id='system',  # System-level event
            type='simulation_run',
            event_metadata={
                'processed_learners': len(learners),
                'risk_counts': risk_counts,
                'auto_nudge': request.auto_nudge,
                'auto_nudges_generated': auto_nudges_generated,
                'risk_threshold': request.risk_threshold
            },
            timestamp=datetime.utcnow()
        )
        
        db.add(event)
        await db.commit()
        
        return SimulationResponse(
            processed_learners=len(learners),
            high_risk_count=risk_counts['high'],
            medium_risk_count=risk_counts['medium'],
            low_risk_count=risk_counts['low'],
            auto_nudges_generated=auto_nudges_generated
        )
        
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Simulation failed")