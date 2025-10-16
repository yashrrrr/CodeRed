"""
Streak Management System for Professional Learners
Implements weekly goal streaks instead of daily (adapted for working professionals)
Based on idea.txt Table 2 recommendations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class WeeklyGoal:
    """Represents a weekly learning goal"""
    week_start: datetime
    week_end: datetime
    target_hours: float = 10.0  # Default 10 hours per week
    target_modules: int = 1  # Default 1 module per week
    target_assessments: int = 1  # Default 1 assessment per week
    actual_hours: float = 0.0
    actual_modules: int = 0
    actual_assessments: int = 0
    is_complete: bool = False
    completion_date: Optional[datetime] = None

@dataclass
class StreakData:
    """Represents a learner's streak information"""
    current_streak: int = 0
    longest_streak: int = 0
    total_weeks_completed: int = 0
    streak_freezes_available: int = 2  # Professional pause feature
    streak_freezes_used: List[datetime] = field(default_factory=list)
    last_active_week: Optional[datetime] = None
    weekly_goals: List[WeeklyGoal] = field(default_factory=list)

class StreakSystem:
    """
    Manages weekly learning streaks for professional learners
    Acknowledges that daily streaks are unrealistic for working professionals
    """

    def __init__(self):
        self.learner_streaks = {}  # {learner_id: StreakData}
        self.streak_rewards = self._initialize_streak_rewards()

    def _initialize_streak_rewards(self) -> Dict[int, Dict[str, Any]]:
        """
        Initialize streak milestone rewards
        """
        return {
            1: {'career_points': 50, 'message': 'Great start! First week complete!'},
            4: {'career_points': 200, 'message': 'One month of consistent learning!'},
            8: {'career_points': 400, 'message': 'Two months strong! You\'re building a habit!'},
            12: {'career_points': 600, 'message': 'Quarter champion! 3 months of dedication!'},
            24: {'career_points': 1200, 'message': 'Half-year hero! Incredible commitment!'},
            52: {'career_points': 5000, 'message': 'One year warrior! You\'re unstoppable!'}
        }

    def update_weekly_progress(self, learner_id: str,
                              progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a learner's weekly progress

        Args:
            learner_id: Unique learner identifier
            progress_data: Dictionary with weekly progress metrics

        Returns:
            Update results including streak status
        """
        if learner_id not in self.learner_streaks:
            self.learner_streaks[learner_id] = StreakData()

        streak_data = self.learner_streaks[learner_id]
        current_week_start = self._get_week_start(datetime.utcnow())

        # Get or create current week's goal
        current_goal = self._get_or_create_weekly_goal(streak_data, current_week_start)

        # Update progress
        current_goal.actual_hours = progress_data.get('hours_studied', 0)
        current_goal.actual_modules = progress_data.get('modules_completed', 0)
        current_goal.actual_assessments = progress_data.get('assessments_completed', 0)

        # Check if goal is met
        goal_met = self._check_goal_completion(current_goal)

        result = {
            'week_start': current_week_start,
            'goal_met': goal_met,
            'current_streak': streak_data.current_streak,
            'longest_streak': streak_data.longest_streak
        }

        if goal_met and not current_goal.is_complete:
            # Mark goal as complete
            current_goal.is_complete = True
            current_goal.completion_date = datetime.utcnow()

            # Update streak
            result.update(self._update_streak(learner_id))

        return result

    def _get_week_start(self, date: datetime) -> datetime:
        """
        Get the start of the week (Monday) for a given date

        Args:
            date: Input date

        Returns:
            Monday of that week at 00:00:00
        """
        days_since_monday = date.weekday()
        week_start = date - timedelta(days=days_since_monday)
        return week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    def _get_or_create_weekly_goal(self, streak_data: StreakData,
                                  week_start: datetime) -> WeeklyGoal:
        """
        Get existing weekly goal or create new one

        Args:
            streak_data: Learner's streak data
            week_start: Start of the week

        Returns:
            WeeklyGoal object
        """
        # Check if goal already exists for this week
        for goal in streak_data.weekly_goals:
            if goal.week_start == week_start:
                return goal

        # Create new goal
        new_goal = WeeklyGoal(
            week_start=week_start,
            week_end=week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        )
        streak_data.weekly_goals.append(new_goal)

        return new_goal

    def _check_goal_completion(self, goal: WeeklyGoal) -> bool:
        """
        Check if weekly goal is met

        Args:
            goal: Weekly goal to check

        Returns:
            True if goal is met
        """
        hours_met = goal.actual_hours >= goal.target_hours * 0.8  # 80% of target hours
        modules_met = goal.actual_modules >= goal.target_modules
        assessments_met = goal.actual_assessments >= goal.target_assessments

        # Require at least 2 out of 3 targets to be met
        criteria_met = sum([hours_met, modules_met, assessments_met])
        return criteria_met >= 2

    def _update_streak(self, learner_id: str) -> Dict[str, Any]:
        """
        Update learner's streak after completing weekly goal

        Args:
            learner_id: Learner identifier

        Returns:
            Streak update results
        """
        streak_data = self.learner_streaks[learner_id]
        current_week = self._get_week_start(datetime.utcnow())

        # Check if this continues the streak
        if streak_data.last_active_week:
            weeks_diff = (current_week - streak_data.last_active_week).days // 7

            if weeks_diff == 1:
                # Consecutive week - continue streak
                streak_data.current_streak += 1
            elif weeks_diff > 1:
                # Gap in weeks - check for freeze
                if self._check_and_use_freeze(learner_id, streak_data.last_active_week, current_week):
                    streak_data.current_streak += 1
                else:
                    # Streak broken
                    streak_data.current_streak = 1
        else:
            # First week
            streak_data.current_streak = 1

        # Update records
        streak_data.last_active_week = current_week
        streak_data.total_weeks_completed += 1
        streak_data.longest_streak = max(streak_data.longest_streak, streak_data.current_streak)

        # Check for rewards
        reward = self.streak_rewards.get(streak_data.current_streak)

        result = {
            'new_streak': streak_data.current_streak,
            'longest_streak': streak_data.longest_streak,
            'total_weeks': streak_data.total_weeks_completed
        }

        if reward:
            result['reward'] = reward
            logger.info(f"Learner {learner_id} earned streak reward: {reward['message']}")

        return result

    def use_streak_freeze(self, learner_id: str, reason: str = '') -> bool:
        """
        Use a streak freeze (Professional Pause feature)

        Args:
            learner_id: Learner identifier
            reason: Optional reason for the freeze

        Returns:
            True if freeze was successfully used
        """
        if learner_id not in self.learner_streaks:
            return False

        streak_data = self.learner_streaks[learner_id]

        if streak_data.streak_freezes_available > 0:
            streak_data.streak_freezes_available -= 1
            streak_data.streak_freezes_used.append(datetime.utcnow())

            logger.info(f"Learner {learner_id} used streak freeze. Reason: {reason}")
            return True

        return False

    def _check_and_use_freeze(self, learner_id: str,
                             last_week: datetime,
                             current_week: datetime) -> bool:
        """
        Check if a freeze can be automatically applied

        Args:
            learner_id: Learner identifier
            last_week: Last active week
            current_week: Current week

        Returns:
            True if freeze was applied
        """
        streak_data = self.learner_streaks[learner_id]
        weeks_missed = ((current_week - last_week).days // 7) - 1

        # Only apply freeze for 1 week gap and if available
        if weeks_missed == 1 and streak_data.streak_freezes_available > 0:
            return self.use_streak_freeze(learner_id, 'auto_applied')

        return False

    def get_streak_status(self, learner_id: str) -> Dict[str, Any]:
        """
        Get current streak status for a learner

        Args:
            learner_id: Learner identifier

        Returns:
            Streak status dictionary
        """
        if learner_id not in self.learner_streaks:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'total_weeks_completed': 0,
                'freezes_available': 2,
                'is_active_this_week': False,
                'next_milestone': 1,
                'weeks_to_milestone': 1
            }

        streak_data = self.learner_streaks[learner_id]
        current_week = self._get_week_start(datetime.utcnow())

        # Check if active this week
        is_active_this_week = False
        for goal in streak_data.weekly_goals:
            if goal.week_start == current_week and goal.is_complete:
                is_active_this_week = True
                break

        # Find next milestone
        next_milestone = None
        for milestone_weeks in sorted(self.streak_rewards.keys()):
            if milestone_weeks > streak_data.current_streak:
                next_milestone = milestone_weeks
                break

        return {
            'current_streak': streak_data.current_streak,
            'longest_streak': streak_data.longest_streak,
            'total_weeks_completed': streak_data.total_weeks_completed,
            'freezes_available': streak_data.streak_freezes_available,
            'is_active_this_week': is_active_this_week,
            'next_milestone': next_milestone,
            'weeks_to_milestone': next_milestone - streak_data.current_streak if next_milestone else None
        }

    def get_weekly_goal_progress(self, learner_id: str) -> Dict[str, Any]:
        """
        Get current week's goal progress

        Args:
            learner_id: Learner identifier

        Returns:
            Progress dictionary
        """
        if learner_id not in self.learner_streaks:
            return {
                'hours_progress': 0,
                'modules_progress': 0,
                'assessments_progress': 0,
                'overall_progress': 0,
                'is_complete': False
            }

        streak_data = self.learner_streaks[learner_id]
        current_week = self._get_week_start(datetime.utcnow())
        current_goal = self._get_or_create_weekly_goal(streak_data, current_week)

        hours_progress = min(100, (current_goal.actual_hours / current_goal.target_hours) * 100)
        modules_progress = min(100, (current_goal.actual_modules / current_goal.target_modules) * 100)
        assessments_progress = min(100, (current_goal.actual_assessments / current_goal.target_assessments) * 100)

        return {
            'hours_progress': hours_progress,
            'hours_actual': current_goal.actual_hours,
            'hours_target': current_goal.target_hours,
            'modules_progress': modules_progress,
            'modules_actual': current_goal.actual_modules,
            'modules_target': current_goal.target_modules,
            'assessments_progress': assessments_progress,
            'assessments_actual': current_goal.actual_assessments,
            'assessments_target': current_goal.target_assessments,
            'overall_progress': (hours_progress + modules_progress + assessments_progress) / 3,
            'is_complete': current_goal.is_complete,
            'days_remaining': (current_goal.week_end - datetime.utcnow()).days
        }

    def get_streak_calendar(self, learner_id: str, weeks: int = 12) -> List[Dict[str, Any]]:
        """
        Get streak calendar data for visualization

        Args:
            learner_id: Learner identifier
            weeks: Number of weeks to include

        Returns:
            List of week data for calendar visualization
        """
        if learner_id not in self.learner_streaks:
            return []

        streak_data = self.learner_streaks[learner_id]
        calendar_data = []
        current_date = datetime.utcnow()

        for i in range(weeks):
            week_start = self._get_week_start(current_date - timedelta(weeks=i))

            # Find goal for this week
            week_goal = None
            for goal in streak_data.weekly_goals:
                if goal.week_start == week_start:
                    week_goal = goal
                    break

            calendar_data.append({
                'week_start': week_start.isoformat(),
                'week_number': week_start.isocalendar()[1],
                'is_complete': week_goal.is_complete if week_goal else False,
                'had_freeze': week_start in [self._get_week_start(f) for f in streak_data.streak_freezes_used],
                'progress': {
                    'hours': week_goal.actual_hours if week_goal else 0,
                    'modules': week_goal.actual_modules if week_goal else 0,
                    'assessments': week_goal.actual_assessments if week_goal else 0
                }
            })

        return list(reversed(calendar_data))