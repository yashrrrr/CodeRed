"""
Risk scoring utility for the Learner Engagement Platform.

This module provides deterministic risk assessment algorithms with batch processing
capabilities for learner engagement analysis.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

def _parse_iso_date(date_str: str) -> datetime:
    """
    Parse ISO date string with defensive error handling.
    Returns current time if parsing fails.
    """
    if not date_str:
        return datetime.now(timezone.utc)
    
    try:
        # Handle both with and without timezone info
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        logger.warning(f"Failed to parse date '{date_str}', using current time")
        return datetime.now(timezone.utc)

def _calculate_recency_factor(last_login: str) -> float:
    """
    Calculate recency factor based on days since last login.
    Returns 0.0 for recent logins, 1.0 for very old logins.
    """
    if not last_login:
        return 1.0  # No login data = high risk
    
    login_date = _parse_iso_date(last_login)
    now = datetime.now(timezone.utc)
    days_since_login = (now - login_date).days
    
    # Recency factor: 0.0 for 0-7 days, 1.0 for 30+ days
    if days_since_login <= 7:
        return 0.0
    elif days_since_login >= 30:
        return 1.0
    else:
        # Linear interpolation between 7 and 30 days
        return (days_since_login - 7) / 23.0

def _clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max bounds."""
    return max(min_val, min(max_val, value))

def compute_risk(learner: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute risk score for a single learner.
    
    Algorithm:
    risk_score = clamp(
        0.5 * (1 - completed_percent/100) +
        0.2 * (1 - avg_quiz_score/100) +
        0.2 * min(consecutive_missed_sessions/7, 1) +
        0.1 * recency_factor,
        0, 1
    )
    
    risk_label = "high" if score > 0.7 else "medium" if score > 0.4 else "low"
    
    Args:
        learner: Dictionary containing learner data
        
    Returns:
        Dictionary with risk_score, risk_label, and learner id
    """
    try:
        # Extract and validate data with defaults
        completed_percent = float(learner.get('completed_percent', 0))
        avg_quiz_score = float(learner.get('avg_quiz_score', 0))
        consecutive_missed = int(learner.get('consecutive_missed_sessions', 0))
        last_login = learner.get('last_login', '')
        
        # Clamp values to valid ranges
        completed_percent = _clamp(completed_percent, 0, 100)
        avg_quiz_score = _clamp(avg_quiz_score, 0, 100)
        consecutive_missed = max(0, consecutive_missed)
        
        # Calculate recency factor
        recency_factor = _calculate_recency_factor(last_login)
        
        # Compute risk score using weighted formula
        risk_score = (
            0.5 * (1 - completed_percent / 100) +
            0.2 * (1 - avg_quiz_score / 100) +
            0.2 * min(consecutive_missed / 7, 1) +
            0.1 * recency_factor
        )
        
        # Clamp final score
        risk_score = _clamp(risk_score, 0, 1)
        
        # Determine risk label
        if risk_score > 0.7:
            risk_label = 'high'
        elif risk_score > 0.4:
            risk_label = 'medium'
        else:
            risk_label = 'low'
        
        return {
            'id': learner.get('id', ''),
            'risk_score': round(risk_score, 3),
            'risk_label': risk_label
        }
        
    except (ValueError, TypeError) as e:
        logger.error(f"Error computing risk for learner {learner.get('id', 'unknown')}: {e}")
        # Return high risk for invalid data
        return {
            'id': learner.get('id', ''),
            'risk_score': 0.8,
            'risk_label': 'high'
        }

def compute_and_update_all(learners: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compute risk scores for all learners in batch.
    
    Args:
        learners: List of learner dictionaries
        
    Returns:
        List of updated learner dictionaries with risk scores
    """
    updated_learners = []
    
    for learner in learners:
        risk_result = compute_risk(learner)
        
        # Update learner with risk data
        updated_learner = learner.copy()
        updated_learner.update(risk_result)
        updated_learners.append(updated_learner)
    
    logger.info(f"Computed risk scores for {len(updated_learners)} learners")
    return updated_learners
