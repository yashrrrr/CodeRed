"""
FastAPI Backend for Engagement & Retention Intelligence Layer
Simplified API for MVP demonstration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel
import logging
from database import SimpleDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = SimpleDB()

# Create FastAPI application
app = FastAPI(
    title="Engagement & Retention Intelligence API",
    description="ML-powered platform for dropout prediction and learner engagement",
    version="2.0.0"
)

# Configure CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class PredictionRequest(BaseModel):
    learner_id: str
    features: Dict[str, Any]

class PredictionResponse(BaseModel):
    learner_id: str
    risk_score: float
    risk_label: str
    risk_color: str
    top_risk_factors: List[str]
    recommended_interventions: List[str]

class NudgeRequest(BaseModel):
    learner_id: str
    risk_signal: str
    channel: str
    intensity: str

class NudgeResponse(BaseModel):
    nudge_id: str
    content: str
    channel: str
    scheduled_at: str

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Engagement & Retention Intelligence Layer",
        "status": "operational",
        "version": "2.0.0"
    }

@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "intelligence-layer"
    }

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_dropout_risk(request: PredictionRequest) -> PredictionResponse:
    """
    Predict dropout risk for a learner using trained ML model
    """
    try:
        import joblib
        import pandas as pd
        import os

        # Load trained model and feature columns
        model_path = '../models/random_forest_model.pkl'
        feature_cols_path = '../models/feature_columns.pkl'

        if os.path.exists(model_path) and os.path.exists(feature_cols_path):
            # Load actual trained model
            model = joblib.load(model_path)
            feature_cols = joblib.load(feature_cols_path)

            # Prepare features
            features_df = pd.DataFrame([request.features])

            # Ensure all required features are present
            for col in feature_cols:
                if col not in features_df.columns:
                    features_df[col] = 0

            # Make prediction
            X = features_df[feature_cols].fillna(0)
            risk_proba = model.predict_proba(X)[0][1]  # Probability of being at risk
            risk_score = float(risk_proba)

            # Get feature importances for this prediction
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]

            # Generate risk factors based on actual feature values
            top_risk_factors = []
            for feat_name, importance in top_features:
                if feat_name in request.features:
                    value = request.features[feat_name]
                    if 'frequency' in feat_name:
                        top_risk_factors.append(f"Low {feat_name.replace('_', ' ')}: {value} days/week")
                    elif 'score' in feat_name:
                        top_risk_factors.append(f"Low {feat_name.replace('_', ' ')}: {value:.1%}")
                    elif 'behind' in feat_name:
                        top_risk_factors.append(f"Behind schedule by {value} days")
                    else:
                        top_risk_factors.append(f"{feat_name.replace('_', ' ').title()}: {value}")

        else:
            # Fallback to simulated prediction if models not found
            logger.warning("Trained models not found, using simulated prediction")
            risk_score = 0.65

            top_risk_factors = [
                "Low login frequency (2 days/week)",
                "Declining quiz scores (-15%)",
                "Behind schedule by 7 days"
            ]

        # Determine risk label and color
        risk_label = "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
        risk_color = "red" if risk_label == "high" else "yellow" if risk_label == "medium" else "green"

        # Generate interventions based on risk level
        if risk_label == "high":
            recommended_interventions = [
                "Immediate personalized outreach from instructor",
                "Schedule urgent 1-on-1 mentoring session",
                "Provide intensive support resources",
                "Consider course pace adjustment"
            ]
        elif risk_label == "medium":
            recommended_interventions = [
                "Send personalized encouragement nudge",
                "Offer optional tutoring session",
                "Share relevant study resources"
            ]
        else:
            recommended_interventions = [
                "Continue regular engagement",
                "Celebrate recent achievements",
                "Suggest advanced challenges"
            ]

        # Save prediction to database
        db.save_prediction({
            'learner_id': request.learner_id,
            'risk_score': risk_score,
            'risk_label': risk_label,
            'risk_color': risk_color,
            'top_risk_factors': top_risk_factors if top_risk_factors else [
                "Low login frequency",
                "Behind schedule",
                "Low quiz performance"
            ],
            'recommended_interventions': recommended_interventions
        })

        return PredictionResponse(
            learner_id=request.learner_id,
            risk_score=risk_score,
            risk_label=risk_label,
            risk_color=risk_color,
            top_risk_factors=top_risk_factors if top_risk_factors else [
                "Low login frequency",
                "Behind schedule",
                "Low quiz performance"
            ],
            recommended_interventions=recommended_interventions
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/nudge", response_model=NudgeResponse)
async def generate_nudge(request: NudgeRequest) -> NudgeResponse:
    """
    Generate a personalized nudge for a learner
    """
    try:
        # Import nudge engine
        from nudges.engine import NudgeEngine, RiskSignal
        from nudges.templates import NudgeTemplates

        # Create nudge
        nudge_id = f"nudge_{request.learner_id}_{datetime.utcnow().timestamp()}"

        # Generate content
        templates = NudgeTemplates()
        content = templates.generate('inactivity_gentle', {
            'name': request.learner_id,
            'last_topic': 'Machine Learning Basics'
        })

        # Save nudge to database
        db.save_nudge({
            'nudge_id': nudge_id,
            'learner_id': request.learner_id,
            'risk_signal': request.risk_signal,
            'intensity': request.intensity,
            'channel': request.channel,
            'content': content
        })

        return NudgeResponse(
            nudge_id=nudge_id,
            content=content,
            channel=request.channel,
            scheduled_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Nudge generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/achievements/{learner_id}")
async def get_achievements(learner_id: str) -> Dict[str, Any]:
    """
    Get learner achievements
    """
    try:
        # Import achievement system
        from gamification.achievements import AchievementSystem

        achievement_system = AchievementSystem()

        # For demo, return sample achievements
        return {
            "learner_id": learner_id,
            "total_points": 1250,
            "achievements": [
                {
                    "name": "Python Proficiency",
                    "description": "Demonstrated proficiency in Python",
                    "points": 500,
                    "earned": True
                },
                {
                    "name": "Week Warrior",
                    "description": "4-week learning streak",
                    "points": 200,
                    "earned": True
                }
            ],
            "next_achievements": [
                {
                    "name": "SQL Expert",
                    "description": "Master SQL queries",
                    "points": 450,
                    "progress": 60
                }
            ]
        }
    except Exception as e:
        logger.error(f"Achievement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leaderboard")
async def get_leaderboard(board_type: str = "skill_mastery") -> Dict[str, Any]:
    """
    Get leaderboard data
    """
    try:
        # For demo, return sample leaderboard
        return {
            "leaderboard_type": board_type,
            "entries": [
                {"rank": 1, "name": "Alice Johnson", "score": 2500, "movement": "up"},
                {"rank": 2, "name": "Bob Smith", "score": 2350, "movement": "same"},
                {"rank": 3, "name": "Charlie Davis", "score": 2200, "movement": "down"},
                {"rank": 4, "name": "Diana Prince", "score": 2100, "movement": "up"},
                {"rank": 5, "name": "Eve Wilson", "score": 2000, "movement": "up"}
            ],
            "updated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/summary")
async def get_analytics_summary() -> Dict[str, Any]:
    """
    Get analytics summary
    """
    return {
        "metrics": {
            "total_learners": 1000,
            "at_risk_count": 350,
            "dropout_reduction": 35,
            "avg_engagement": 68,
            "nudge_response_rate": 68,
            "model_recall": 78,
            "model_precision": 71
        },
        "business_impact": {
            "revenue_retained": 2300000,
            "cac_reduction": 28,
            "ltv_increase": 1100
        },
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )