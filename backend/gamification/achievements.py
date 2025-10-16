"""
Achievement System for Professional Learners
Implements badges, micro-credentials, and career capital points
Based on idea.txt Table 2: Adapting Gamification for the Professional Learner
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class Achievement:
    """
    Represents a professional achievement/badge
    """
    id: str
    name: str
    description: str
    category: str  # skill, milestone, collaboration, consistency
    points_value: int  # Career Capital points
    icon: str  # Icon identifier for UI
    requirements: Dict[str, Any]
    linkedin_shareable: bool = True
    is_micro_credential: bool = False
    skill_tags: List[str] = field(default_factory=list)

class AchievementSystem:
    """
    Manages achievements, badges, and micro-credentials for professional learners
    Focuses on career-relevant accomplishments rather than casual gaming elements
    """

    def __init__(self):
        self.achievements = self._initialize_achievements()
        self.learner_achievements = {}  # {learner_id: [achievement_ids]}
        self.career_capital_points = {}  # {learner_id: points}

    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """
        Initialize all available achievements
        Based on professional skill development and career progression
        """
        achievements = {
            # Skill-based Micro-credentials (Highest Value)
            'python_proficiency': Achievement(
                id='python_proficiency',
                name='Python for Data Analysis Proficiency',
                description='Demonstrated proficiency in Python for data analysis through assessments',
                category='skill',
                points_value=500,
                icon='🐍',
                requirements={'skill_assessments_passed': ['python_basics', 'pandas', 'numpy']},
                is_micro_credential=True,
                skill_tags=['Python', 'Data Analysis', 'Programming']
            ),

            'excel_advanced': Achievement(
                id='excel_advanced',
                name='Advanced Excel Specialist',
                description='Mastered advanced Excel features including pivot tables and macros',
                category='skill',
                points_value=400,
                icon='📊',
                requirements={'modules_completed': ['excel_pivots', 'excel_macros', 'excel_analysis']},
                is_micro_credential=True,
                skill_tags=['Excel', 'Data Analysis', 'Business Intelligence']
            ),

            'sql_expert': Achievement(
                id='sql_expert',
                name='SQL Query Expert',
                description='Proven ability to write complex SQL queries for data extraction',
                category='skill',
                points_value=450,
                icon='🗄️',
                requirements={'skill_assessments_passed': ['sql_basics', 'sql_joins', 'sql_optimization']},
                is_micro_credential=True,
                skill_tags=['SQL', 'Database', 'Data Engineering']
            ),

            'ml_foundations': Achievement(
                id='ml_foundations',
                name='Machine Learning Foundations',
                description='Completed foundational machine learning concepts and applications',
                category='skill',
                points_value=600,
                icon='🤖',
                requirements={'modules_completed': ['ml_intro', 'supervised_learning', 'model_evaluation']},
                is_micro_credential=True,
                skill_tags=['Machine Learning', 'AI', 'Data Science']
            ),

            # Milestone Achievements
            'first_module': Achievement(
                id='first_module',
                name='Journey Begun',
                description='Successfully completed your first module',
                category='milestone',
                points_value=100,
                icon='🚀',
                requirements={'modules_completed_count': 1},
                is_micro_credential=False
            ),

            'halfway_hero': Achievement(
                id='halfway_hero',
                name='Halfway Hero',
                description='Reached 50% course completion',
                category='milestone',
                points_value=250,
                icon='🎯',
                requirements={'course_progress_pct': 50},
                is_micro_credential=False
            ),

            'course_complete': Achievement(
                id='course_complete',
                name='Course Completionist',
                description='Successfully completed an entire course',
                category='milestone',
                points_value=1000,
                icon='🎓',
                requirements={'courses_completed': 1},
                is_micro_credential=False
            ),

            # Consistency Achievements (Weekly Streaks for Professionals)
            'week_warrior': Achievement(
                id='week_warrior',
                name='Week Warrior',
                description='Maintained a 4-week learning streak',
                category='consistency',
                points_value=200,
                icon='🔥',
                requirements={'weekly_streak': 4},
                is_micro_credential=False
            ),

            'month_master': Achievement(
                id='month_master',
                name='Monthly Master',
                description='Consistent learning for an entire month',
                category='consistency',
                points_value=300,
                icon='📅',
                requirements={'weekly_streak': 4, 'monthly_goals_met': 1},
                is_micro_credential=False
            ),

            'quarter_champion': Achievement(
                id='quarter_champion',
                name='Quarterly Champion',
                description='Maintained consistent progress for a full quarter',
                category='consistency',
                points_value=500,
                icon='🏆',
                requirements={'weekly_streak': 12},
                is_micro_credential=False
            ),

            # Collaboration Achievements
            'helpful_peer': Achievement(
                id='helpful_peer',
                name='Helpful Peer',
                description='Provided valuable assistance to 10 fellow learners',
                category='collaboration',
                points_value=150,
                icon='🤝',
                requirements={'forum_helpful_answers': 10},
                is_micro_credential=False
            ),

            'discussion_leader': Achievement(
                id='discussion_leader',
                name='Discussion Leader',
                description='Started 5 valuable discussion threads',
                category='collaboration',
                points_value=200,
                icon='💬',
                requirements={'valuable_discussions_started': 5},
                is_micro_credential=False
            ),

            'study_group_organizer': Achievement(
                id='study_group_organizer',
                name='Study Group Organizer',
                description='Successfully organized and led a study group',
                category='collaboration',
                points_value=250,
                icon='👥',
                requirements={'study_groups_organized': 1},
                is_micro_credential=False
            ),

            # Performance Achievements
            'perfect_week': Achievement(
                id='perfect_week',
                name='Perfect Week',
                description='Completed all weekly goals and assessments with >90% score',
                category='performance',
                points_value=150,
                icon='⭐',
                requirements={'perfect_weeks': 1},
                is_micro_credential=False
            ),

            'comeback_kid': Achievement(
                id='comeback_kid',
                name='Comeback Champion',
                description='Improved performance after being identified as at-risk',
                category='performance',
                points_value=300,
                icon='💪',
                requirements={'risk_recovery': True},
                is_micro_credential=False
            ),

            'top_performer': Achievement(
                id='top_performer',
                name='Top Performer',
                description='Ranked in top 10% of your cohort',
                category='performance',
                points_value=400,
                icon='🥇',
                requirements={'cohort_rank_percentile': 90},
                is_micro_credential=False
            )
        }

        return achievements

    def check_achievements(self, learner_id: str,
                         learner_stats: Dict[str, Any]) -> List[Achievement]:
        """
        Check if learner has earned any new achievements

        Args:
            learner_id: Unique learner identifier
            learner_stats: Current learner statistics

        Returns:
            List of newly earned achievements
        """
        if learner_id not in self.learner_achievements:
            self.learner_achievements[learner_id] = []

        new_achievements = []
        current_achievements = self.learner_achievements[learner_id]

        for achievement_id, achievement in self.achievements.items():
            # Skip if already earned
            if achievement_id in current_achievements:
                continue

            # Check if requirements are met
            if self._check_requirements(achievement.requirements, learner_stats):
                new_achievements.append(achievement)
                current_achievements.append(achievement_id)

                # Award career capital points
                self._award_points(learner_id, achievement.points_value)

                logger.info(f"Learner {learner_id} earned achievement: {achievement.name}")

        return new_achievements

    def _check_requirements(self, requirements: Dict[str, Any],
                          stats: Dict[str, Any]) -> bool:
        """
        Check if achievement requirements are met

        Args:
            requirements: Achievement requirements
            stats: Learner statistics

        Returns:
            True if all requirements are met
        """
        for key, value in requirements.items():
            if key == 'skill_assessments_passed':
                # Check if all required assessments are passed
                passed = stats.get('assessments_passed', [])
                if not all(assessment in passed for assessment in value):
                    return False

            elif key == 'modules_completed':
                # Check if specific modules are completed
                completed = stats.get('modules_completed', [])
                if isinstance(value, list):
                    if not all(module in completed for module in value):
                        return False
                else:
                    if len(completed) < value:
                        return False

            elif key == 'modules_completed_count':
                if len(stats.get('modules_completed', [])) < value:
                    return False

            elif key == 'course_progress_pct':
                if stats.get('course_progress_pct', 0) < value:
                    return False

            elif key == 'weekly_streak':
                if stats.get('weekly_streak', 0) < value:
                    return False

            elif key == 'forum_helpful_answers':
                if stats.get('forum_helpful_answers', 0) < value:
                    return False

            elif key == 'cohort_rank_percentile':
                if stats.get('cohort_rank_percentile', 0) < value:
                    return False

            elif key == 'risk_recovery':
                # Check if learner improved from high risk to low risk
                if not stats.get('recovered_from_risk', False):
                    return False

            else:
                # Generic numeric comparison
                if stats.get(key, 0) < value:
                    return False

        return True

    def _award_points(self, learner_id: str, points: int):
        """
        Award career capital points to learner

        Args:
            learner_id: Learner identifier
            points: Points to award
        """
        if learner_id not in self.career_capital_points:
            self.career_capital_points[learner_id] = 0

        self.career_capital_points[learner_id] += points

    def get_learner_achievements(self, learner_id: str) -> List[Achievement]:
        """
        Get all achievements earned by a learner

        Args:
            learner_id: Learner identifier

        Returns:
            List of achievements
        """
        achievement_ids = self.learner_achievements.get(learner_id, [])
        return [self.achievements[aid] for aid in achievement_ids]

    def get_career_capital_points(self, learner_id: str) -> int:
        """
        Get learner's career capital points

        Args:
            learner_id: Learner identifier

        Returns:
            Total points
        """
        return self.career_capital_points.get(learner_id, 0)

    def get_linkedin_shareable_achievements(self, learner_id: str) -> List[Dict[str, Any]]:
        """
        Get achievements formatted for LinkedIn sharing

        Args:
            learner_id: Learner identifier

        Returns:
            List of shareable achievement data
        """
        achievements = self.get_learner_achievements(learner_id)
        shareable = []

        for achievement in achievements:
            if achievement.linkedin_shareable:
                shareable.append({
                    'title': achievement.name,
                    'description': achievement.description,
                    'is_credential': achievement.is_micro_credential,
                    'skills': achievement.skill_tags,
                    'icon': achievement.icon,
                    'verification_url': f"https://platform.com/verify/{learner_id}/{achievement.id}"
                })

        return shareable

    def get_next_achievements(self, learner_id: str,
                            learner_stats: Dict[str, Any],
                            limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get next achievable achievements for motivation

        Args:
            learner_id: Learner identifier
            learner_stats: Current learner statistics
            limit: Maximum number of achievements to return

        Returns:
            List of next achievable achievements with progress
        """
        current_achievements = self.learner_achievements.get(learner_id, [])
        next_achievements = []

        for achievement_id, achievement in self.achievements.items():
            if achievement_id in current_achievements:
                continue

            progress = self._calculate_progress(achievement.requirements, learner_stats)
            if 0 < progress < 100:  # Partially complete
                next_achievements.append({
                    'achievement': achievement,
                    'progress': progress,
                    'remaining': self._get_remaining_requirements(achievement.requirements, learner_stats)
                })

        # Sort by progress (closest to completion first)
        next_achievements.sort(key=lambda x: x['progress'], reverse=True)

        return next_achievements[:limit]

    def _calculate_progress(self, requirements: Dict[str, Any],
                          stats: Dict[str, Any]) -> float:
        """
        Calculate percentage progress towards an achievement

        Args:
            requirements: Achievement requirements
            stats: Learner statistics

        Returns:
            Progress percentage (0-100)
        """
        if not requirements:
            return 0

        progress_items = []

        for key, value in requirements.items():
            if isinstance(value, (int, float)):
                current = stats.get(key, 0)
                progress_items.append(min(current / value * 100, 100))
            elif isinstance(value, list):
                completed = stats.get(key.replace('_required', ''), [])
                if completed:
                    progress_items.append(len(set(completed) & set(value)) / len(value) * 100)
                else:
                    progress_items.append(0)

        return sum(progress_items) / len(progress_items) if progress_items else 0

    def _get_remaining_requirements(self, requirements: Dict[str, Any],
                                  stats: Dict[str, Any]) -> str:
        """
        Get human-readable remaining requirements

        Args:
            requirements: Achievement requirements
            stats: Learner statistics

        Returns:
            Description of what's needed
        """
        remaining = []

        for key, value in requirements.items():
            if key == 'modules_completed_count':
                current = len(stats.get('modules_completed', []))
                if current < value:
                    remaining.append(f"Complete {value - current} more modules")

            elif key == 'weekly_streak':
                current = stats.get('weekly_streak', 0)
                if current < value:
                    remaining.append(f"Maintain streak for {value - current} more weeks")

            elif key == 'course_progress_pct':
                current = stats.get('course_progress_pct', 0)
                if current < value:
                    remaining.append(f"Reach {value}% course completion (currently {current}%)")

        return ", ".join(remaining) if remaining else "Requirements nearly met"