"""
Multi-Tiered Nudge Engine for Automated Interventions
Implements graduated response system from idea.txt Table 3
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import logging
import random

logger = logging.getLogger(__name__)

class NudgeChannel(Enum):
    """Communication channels for nudges"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

class NudgeIntensity(Enum):
    """Intervention intensity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    HUMAN_ESCALATION = 4

class RiskSignal(Enum):
    """Types of risk signals that trigger nudges"""
    INACTIVITY = "inactivity"
    FAILED_QUIZ = "failed_quiz"
    LOW_VIDEO_ENGAGEMENT = "low_video_engagement"
    APPROACHING_DEADLINE = "approaching_deadline"
    MISSED_WEEKLY_GOAL = "missed_weekly_goal"
    DECLINING_PERFORMANCE = "declining_performance"
    HIGH_RISK_SCORE = "high_risk_score"

@dataclass
class Nudge:
    """Represents a single nudge intervention"""
    id: str
    learner_id: str
    risk_signal: RiskSignal
    intensity: NudgeIntensity
    channel: NudgeChannel
    content: str
    tone: str
    action_link: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    response_received: bool = False
    effectiveness_score: Optional[float] = None

class NudgeEngine:
    """
    Implements multi-tiered automated nudging system
    Based on idea.txt Table 3: Nudge Intervention Matrix
    """

    def __init__(self):
        self.nudge_history = {}  # {learner_id: [nudges]}
        self.nudge_rules = self._initialize_nudge_rules()
        self.cooldown_periods = self._initialize_cooldown_periods()
        self.last_nudge_times = {}  # {learner_id: {signal_type: datetime}}

    def _initialize_nudge_rules(self) -> Dict[RiskSignal, List[Dict[str, Any]]]:
        """
        Initialize nudge rules based on Table 3 from idea.txt
        Each signal has three escalation stages plus human intervention
        """
        return {
            RiskSignal.INACTIVITY: [
                # Stage 1: Low Intensity (Days 7-10)
                {
                    'intensity': NudgeIntensity.LOW,
                    'channels': [NudgeChannel.PUSH, NudgeChannel.EMAIL],
                    'tone': 'encouraging',
                    'template': 'inactivity_gentle',
                    'trigger_after_days': 7
                },
                # Stage 2: Medium Intensity (Days 11-14)
                {
                    'intensity': NudgeIntensity.MEDIUM,
                    'channels': [NudgeChannel.IN_APP, NudgeChannel.EMAIL],
                    'tone': 'supportive_social',
                    'template': 'inactivity_social_proof',
                    'trigger_after_days': 11
                },
                # Stage 3: Human Escalation (Day 15+)
                {
                    'intensity': NudgeIntensity.HUMAN_ESCALATION,
                    'channels': [NudgeChannel.EMAIL],
                    'tone': 'personal_concern',
                    'template': 'instructor_check_in',
                    'trigger_after_days': 15
                }
            ],

            RiskSignal.FAILED_QUIZ: [
                # Stage 1: Low Intensity (Immediately after 2nd failure)
                {
                    'intensity': NudgeIntensity.LOW,
                    'channels': [NudgeChannel.IN_APP],
                    'tone': 'diagnostic',
                    'template': 'quiz_review_suggestion',
                    'trigger_after_failures': 2
                },
                # Stage 2: Medium Intensity (After 3rd failure)
                {
                    'intensity': NudgeIntensity.MEDIUM,
                    'channels': [NudgeChannel.EMAIL],
                    'tone': 'resource_oriented',
                    'template': 'bonus_materials_unlock',
                    'trigger_after_failures': 3
                },
                # Stage 3: Human Escalation (After 4th failure)
                {
                    'intensity': NudgeIntensity.HUMAN_ESCALATION,
                    'channels': [NudgeChannel.EMAIL],
                    'tone': 'supportive',
                    'template': 'advisor_tutoring_offer',
                    'trigger_after_failures': 4
                }
            ],

            RiskSignal.LOW_VIDEO_ENGAGEMENT: [
                # Stage 1: Low Intensity
                {
                    'intensity': NudgeIntensity.LOW,
                    'channels': [NudgeChannel.PUSH],
                    'tone': 'value_highlighting',
                    'template': 'video_key_concept',
                    'trigger_threshold': 0.3  # <30% videos watched
                },
                # Stage 2: Medium Intensity
                {
                    'intensity': NudgeIntensity.MEDIUM,
                    'channels': [NudgeChannel.IN_APP],
                    'tone': 'interactive',
                    'template': 'video_quiz_challenge',
                    'trigger_threshold': 0.2  # <20% videos watched
                },
                # Stage 3: Peer Challenge
                {
                    'intensity': NudgeIntensity.HIGH,
                    'channels': [NudgeChannel.EMAIL],
                    'tone': 'social',
                    'template': 'peer_study_session',
                    'trigger_threshold': 0.1  # <10% videos watched
                }
            ],

            RiskSignal.APPROACHING_DEADLINE: [
                # Stage 1: 48 hours before
                {
                    'intensity': NudgeIntensity.LOW,
                    'channels': [NudgeChannel.PUSH, NudgeChannel.EMAIL],
                    'tone': 'reminder',
                    'template': 'deadline_friendly',
                    'hours_before': 48
                },
                # Stage 2: 24 hours before
                {
                    'intensity': NudgeIntensity.MEDIUM,
                    'channels': [NudgeChannel.PUSH, NudgeChannel.EMAIL],
                    'tone': 'urgency_support',
                    'template': 'deadline_urgent_help',
                    'hours_before': 24
                },
                # Stage 3: Extension offer
                {
                    'intensity': NudgeIntensity.HIGH,
                    'channels': [NudgeChannel.IN_APP],
                    'tone': 'supportive',
                    'template': 'extension_offer',
                    'hours_before': 6
                }
            ],

            RiskSignal.HIGH_RISK_SCORE: [
                # Stage 1: Automated encouragement
                {
                    'intensity': NudgeIntensity.LOW,
                    'channels': [NudgeChannel.IN_APP],
                    'tone': 'motivational',
                    'template': 'risk_encouragement',
                    'risk_threshold': 0.6
                },
                # Stage 2: Resource provision
                {
                    'intensity': NudgeIntensity.MEDIUM,
                    'channels': [NudgeChannel.EMAIL],
                    'tone': 'helpful',
                    'template': 'risk_resources',
                    'risk_threshold': 0.7
                },
                # Stage 3: Personal intervention
                {
                    'intensity': NudgeIntensity.HUMAN_ESCALATION,
                    'channels': [NudgeChannel.EMAIL],
                    'tone': 'personal',
                    'template': 'mentor_reach_out',
                    'risk_threshold': 0.8
                }
            ]
        }

    def _initialize_cooldown_periods(self) -> Dict[RiskSignal, timedelta]:
        """
        Initialize cooldown periods to avoid nudge fatigue
        """
        return {
            RiskSignal.INACTIVITY: timedelta(days=3),
            RiskSignal.FAILED_QUIZ: timedelta(days=1),
            RiskSignal.LOW_VIDEO_ENGAGEMENT: timedelta(days=2),
            RiskSignal.APPROACHING_DEADLINE: timedelta(hours=12),
            RiskSignal.MISSED_WEEKLY_GOAL: timedelta(days=2),
            RiskSignal.DECLINING_PERFORMANCE: timedelta(days=3),
            RiskSignal.HIGH_RISK_SCORE: timedelta(days=2)
        }

    def generate_nudge(self, learner_id: str, risk_signal: RiskSignal,
                      context: Dict[str, Any]) -> Optional[Nudge]:
        """
        Generate appropriate nudge based on risk signal and context

        Args:
            learner_id: Learner identifier
            risk_signal: Type of risk detected
            context: Additional context for nudge generation

        Returns:
            Nudge object or None if in cooldown
        """
        # Check cooldown
        if self._is_in_cooldown(learner_id, risk_signal):
            logger.info(f"Skipping nudge for {learner_id} - {risk_signal}: in cooldown")
            return None

        # Get appropriate nudge rule
        nudge_rule = self._select_nudge_rule(risk_signal, context)
        if not nudge_rule:
            return None

        # Generate nudge content
        content = self._generate_content(nudge_rule['template'], context)

        # Select channel (prefer first available)
        channel = nudge_rule['channels'][0]

        # Create nudge
        nudge = Nudge(
            id=f"{learner_id}_{risk_signal.value}_{datetime.utcnow().timestamp()}",
            learner_id=learner_id,
            risk_signal=risk_signal,
            intensity=nudge_rule['intensity'],
            channel=channel,
            content=content,
            tone=nudge_rule['tone'],
            action_link=self._generate_action_link(risk_signal, context),
            scheduled_at=datetime.utcnow()
        )

        # Record nudge
        self._record_nudge(learner_id, nudge, risk_signal)

        return nudge

    def _is_in_cooldown(self, learner_id: str, risk_signal: RiskSignal) -> bool:
        """
        Check if learner is in cooldown period for specific signal

        Args:
            learner_id: Learner identifier
            risk_signal: Risk signal type

        Returns:
            True if in cooldown period
        """
        if learner_id not in self.last_nudge_times:
            return False

        last_nudge = self.last_nudge_times[learner_id].get(risk_signal)
        if not last_nudge:
            return False

        cooldown_period = self.cooldown_periods[risk_signal]
        return datetime.utcnow() < last_nudge + cooldown_period

    def _select_nudge_rule(self, risk_signal: RiskSignal,
                          context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Select appropriate nudge rule based on context

        Args:
            risk_signal: Risk signal type
            context: Context data

        Returns:
            Nudge rule dictionary or None
        """
        rules = self.nudge_rules.get(risk_signal, [])
        if not rules:
            return None

        # Determine which stage to use based on context
        if risk_signal == RiskSignal.INACTIVITY:
            days_inactive = context.get('days_inactive', 0)
            for rule in rules:
                if days_inactive >= rule.get('trigger_after_days', 0):
                    selected_rule = rule
            return selected_rule if 'selected_rule' in locals() else rules[0]

        elif risk_signal == RiskSignal.FAILED_QUIZ:
            failure_count = context.get('failure_count', 0)
            for rule in rules:
                if failure_count >= rule.get('trigger_after_failures', 0):
                    selected_rule = rule
            return selected_rule if 'selected_rule' in locals() else rules[0]

        elif risk_signal == RiskSignal.APPROACHING_DEADLINE:
            hours_remaining = context.get('hours_remaining', 48)
            for rule in rules:
                if hours_remaining <= rule.get('hours_before', float('inf')):
                    return rule
            return rules[0]

        # Default to first rule
        return rules[0]

    def _generate_content(self, template: str, context: Dict[str, Any]) -> str:
        """
        Generate nudge content from template

        Args:
            template: Template name
            context: Context for content generation

        Returns:
            Nudge content string
        """
        from .templates import NudgeTemplates
        templates = NudgeTemplates()
        return templates.generate(template, context)

    def _generate_action_link(self, risk_signal: RiskSignal,
                             context: Dict[str, Any]) -> str:
        """
        Generate appropriate action link for the nudge

        Args:
            risk_signal: Risk signal type
            context: Context data

        Returns:
            Action URL
        """
        base_url = "https://platform.com"

        if risk_signal == RiskSignal.INACTIVITY:
            return f"{base_url}/continue-learning"
        elif risk_signal == RiskSignal.FAILED_QUIZ:
            quiz_id = context.get('quiz_id', '')
            return f"{base_url}/quiz/{quiz_id}/review"
        elif risk_signal == RiskSignal.LOW_VIDEO_ENGAGEMENT:
            video_id = context.get('next_video_id', '')
            return f"{base_url}/video/{video_id}"
        elif risk_signal == RiskSignal.APPROACHING_DEADLINE:
            assignment_id = context.get('assignment_id', '')
            return f"{base_url}/assignment/{assignment_id}"
        else:
            return f"{base_url}/dashboard"

    def _record_nudge(self, learner_id: str, nudge: Nudge, risk_signal: RiskSignal):
        """
        Record nudge in history and update last nudge time

        Args:
            learner_id: Learner identifier
            nudge: Nudge object
            risk_signal: Risk signal type
        """
        # Add to history
        if learner_id not in self.nudge_history:
            self.nudge_history[learner_id] = []
        self.nudge_history[learner_id].append(nudge)

        # Update last nudge time
        if learner_id not in self.last_nudge_times:
            self.last_nudge_times[learner_id] = {}
        self.last_nudge_times[learner_id][risk_signal] = datetime.utcnow()

    def get_pending_nudges(self, learner_id: Optional[str] = None) -> List[Nudge]:
        """
        Get pending nudges that need to be sent

        Args:
            learner_id: Optional filter by learner

        Returns:
            List of pending nudges
        """
        pending = []

        for lid, nudges in self.nudge_history.items():
            if learner_id and lid != learner_id:
                continue

            for nudge in nudges:
                if nudge.scheduled_at and not nudge.sent_at:
                    if nudge.scheduled_at <= datetime.utcnow():
                        pending.append(nudge)

        return pending

    def mark_nudge_sent(self, nudge_id: str):
        """
        Mark a nudge as sent

        Args:
            nudge_id: Nudge identifier
        """
        for nudges in self.nudge_history.values():
            for nudge in nudges:
                if nudge.id == nudge_id:
                    nudge.sent_at = datetime.utcnow()
                    logger.info(f"Nudge {nudge_id} marked as sent")
                    return

    def record_nudge_response(self, nudge_id: str, responded: bool,
                            effectiveness_score: Optional[float] = None):
        """
        Record learner's response to a nudge

        Args:
            nudge_id: Nudge identifier
            responded: Whether learner responded
            effectiveness_score: Optional effectiveness rating
        """
        for nudges in self.nudge_history.values():
            for nudge in nudges:
                if nudge.id == nudge_id:
                    nudge.response_received = responded
                    nudge.effectiveness_score = effectiveness_score
                    logger.info(f"Nudge {nudge_id} response recorded: {responded}")
                    return

    def get_nudge_analytics(self, learner_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get analytics on nudge effectiveness

        Args:
            learner_id: Optional filter by learner

        Returns:
            Analytics dictionary
        """
        all_nudges = []
        if learner_id:
            all_nudges = self.nudge_history.get(learner_id, [])
        else:
            for nudges in self.nudge_history.values():
                all_nudges.extend(nudges)

        total_sent = len([n for n in all_nudges if n.sent_at])
        total_responded = len([n for n in all_nudges if n.response_received])
        response_rate = total_responded / total_sent if total_sent > 0 else 0

        # Calculate effectiveness by signal type
        effectiveness_by_signal = {}
        for signal in RiskSignal:
            signal_nudges = [n for n in all_nudges if n.risk_signal == signal and n.sent_at]
            signal_responded = [n for n in signal_nudges if n.response_received]
            if signal_nudges:
                effectiveness_by_signal[signal.value] = {
                    'sent': len(signal_nudges),
                    'responded': len(signal_responded),
                    'response_rate': len(signal_responded) / len(signal_nudges)
                }

        # Calculate effectiveness by intensity
        effectiveness_by_intensity = {}
        for intensity in NudgeIntensity:
            intensity_nudges = [n for n in all_nudges if n.intensity == intensity and n.sent_at]
            intensity_responded = [n for n in intensity_nudges if n.response_received]
            if intensity_nudges:
                effectiveness_by_intensity[intensity.value] = {
                    'sent': len(intensity_nudges),
                    'responded': len(intensity_responded),
                    'response_rate': len(intensity_responded) / len(intensity_nudges)
                }

        return {
            'total_nudges_sent': total_sent,
            'total_responses': total_responded,
            'overall_response_rate': response_rate,
            'by_signal_type': effectiveness_by_signal,
            'by_intensity': effectiveness_by_intensity
        }