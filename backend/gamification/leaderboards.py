"""
Leaderboard System for Professional Learners
Focuses on skill mastery and professional competence rather than XP
Based on idea.txt recommendations for professional adaptation
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class LeaderboardType(Enum):
    """Types of leaderboards available"""
    SKILL_MASTERY = "skill_mastery"
    PROJECTS_COMPLETED = "projects_completed"
    HELPFUL_CONTRIBUTIONS = "helpful_contributions"
    CONSISTENCY_STREAK = "consistency_streak"
    IMPROVEMENT_RATE = "improvement_rate"
    CAREER_CAPITAL = "career_capital"

@dataclass
class LeaderboardEntry:
    """Represents an entry in a leaderboard"""
    learner_id: str
    learner_name: str
    score: float
    rank: int
    details: Dict[str, Any]
    movement: int = 0  # Position change from last week

class LeaderboardSystem:
    """
    Manages professional-focused leaderboards
    Emphasizes competence over time spent (no XP)
    """

    def __init__(self):
        self.leaderboards = {}
        self.learner_scores = {}
        self.historical_data = {}

    def update_learner_score(self, learner_id: str, learner_name: str,
                            leaderboard_type: LeaderboardType,
                            score_data: Dict[str, Any]):
        """
        Update a learner's score on a specific leaderboard

        Args:
            learner_id: Unique learner identifier
            learner_name: Learner's display name
            leaderboard_type: Type of leaderboard
            score_data: Data used to calculate score
        """
        score = self._calculate_score(leaderboard_type, score_data)

        if leaderboard_type not in self.leaderboards:
            self.leaderboards[leaderboard_type] = {}

        # Store previous rank for movement calculation
        previous_rank = None
        if learner_id in self.leaderboards[leaderboard_type]:
            previous_rank = self._get_learner_rank(learner_id, leaderboard_type)

        # Update score
        self.leaderboards[leaderboard_type][learner_id] = {
            'name': learner_name,
            'score': score,
            'details': self._get_score_details(leaderboard_type, score_data),
            'updated_at': datetime.utcnow(),
            'previous_rank': previous_rank
        }

    def _calculate_score(self, leaderboard_type: LeaderboardType,
                        score_data: Dict[str, Any]) -> float:
        """
        Calculate score based on leaderboard type

        Args:
            leaderboard_type: Type of leaderboard
            score_data: Data for score calculation

        Returns:
            Calculated score
        """
        if leaderboard_type == LeaderboardType.SKILL_MASTERY:
            # Score based on skills validated through assessments
            skills_mastered = score_data.get('skills_mastered', [])
            skill_scores = score_data.get('skill_assessment_scores', {})
            total_score = 0
            for skill in skills_mastered:
                # Weight by assessment score
                total_score += skill_scores.get(skill, 0) * 10
            return total_score

        elif leaderboard_type == LeaderboardType.PROJECTS_COMPLETED:
            # Score based on number and quality of projects
            projects = score_data.get('projects_completed', 0)
            avg_project_score = score_data.get('avg_project_score', 0)
            return projects * avg_project_score

        elif leaderboard_type == LeaderboardType.HELPFUL_CONTRIBUTIONS:
            # Score based on forum contributions that helped others
            helpful_answers = score_data.get('helpful_answers', 0)
            answers_marked_best = score_data.get('answers_marked_best', 0)
            upvotes_received = score_data.get('upvotes_received', 0)
            return helpful_answers * 10 + answers_marked_best * 50 + upvotes_received

        elif leaderboard_type == LeaderboardType.CONSISTENCY_STREAK:
            # Score based on weekly streak and consistency
            weekly_streak = score_data.get('weekly_streak', 0)
            goals_met = score_data.get('weekly_goals_met', 0)
            return weekly_streak * 100 + goals_met * 25

        elif leaderboard_type == LeaderboardType.IMPROVEMENT_RATE:
            # Score based on performance improvement over time
            initial_score = score_data.get('initial_avg_score', 50)
            current_score = score_data.get('current_avg_score', 50)
            time_period_weeks = score_data.get('weeks_active', 1)
            improvement = (current_score - initial_score) / time_period_weeks
            return max(0, improvement * 100)

        elif leaderboard_type == LeaderboardType.CAREER_CAPITAL:
            # Total career capital points earned
            return score_data.get('career_capital_points', 0)

        return 0

    def _get_score_details(self, leaderboard_type: LeaderboardType,
                          score_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed breakdown of score components

        Args:
            leaderboard_type: Type of leaderboard
            score_data: Score data

        Returns:
            Detailed breakdown
        """
        if leaderboard_type == LeaderboardType.SKILL_MASTERY:
            return {
                'skills_mastered': score_data.get('skills_mastered', []),
                'total_skills': len(score_data.get('skills_mastered', [])),
                'avg_assessment_score': score_data.get('avg_skill_score', 0)
            }

        elif leaderboard_type == LeaderboardType.PROJECTS_COMPLETED:
            return {
                'projects_count': score_data.get('projects_completed', 0),
                'avg_score': score_data.get('avg_project_score', 0),
                'latest_project': score_data.get('latest_project_name', '')
            }

        elif leaderboard_type == LeaderboardType.HELPFUL_CONTRIBUTIONS:
            return {
                'helpful_answers': score_data.get('helpful_answers', 0),
                'best_answers': score_data.get('answers_marked_best', 0),
                'upvotes': score_data.get('upvotes_received', 0)
            }

        elif leaderboard_type == LeaderboardType.CONSISTENCY_STREAK:
            return {
                'current_streak': score_data.get('weekly_streak', 0),
                'longest_streak': score_data.get('longest_streak', 0),
                'goals_met': score_data.get('weekly_goals_met', 0)
            }

        elif leaderboard_type == LeaderboardType.IMPROVEMENT_RATE:
            return {
                'improvement_pct': score_data.get('improvement_percentage', 0),
                'from_score': score_data.get('initial_avg_score', 0),
                'to_score': score_data.get('current_avg_score', 0)
            }

        elif leaderboard_type == LeaderboardType.CAREER_CAPITAL:
            return {
                'total_points': score_data.get('career_capital_points', 0),
                'achievements_earned': score_data.get('achievements_count', 0),
                'micro_credentials': score_data.get('micro_credentials_count', 0)
            }

        return {}

    def get_leaderboard(self, leaderboard_type: LeaderboardType,
                       cohort_filter: Optional[str] = None,
                       limit: int = 100) -> List[LeaderboardEntry]:
        """
        Get leaderboard entries sorted by rank

        Args:
            leaderboard_type: Type of leaderboard
            cohort_filter: Optional cohort/program filter
            limit: Maximum entries to return

        Returns:
            List of leaderboard entries
        """
        if leaderboard_type not in self.leaderboards:
            return []

        entries = []
        leaderboard_data = self.leaderboards[leaderboard_type]

        # Convert to list of entries
        for learner_id, data in leaderboard_data.items():
            # Apply cohort filter if specified
            if cohort_filter and data.get('cohort') != cohort_filter:
                continue

            entries.append({
                'learner_id': learner_id,
                'name': data['name'],
                'score': data['score'],
                'details': data['details'],
                'previous_rank': data.get('previous_rank')
            })

        # Sort by score (descending)
        entries.sort(key=lambda x: x['score'], reverse=True)

        # Create LeaderboardEntry objects with ranks and movement
        leaderboard_entries = []
        for rank, entry in enumerate(entries[:limit], start=1):
            movement = 0
            if entry['previous_rank'] is not None:
                movement = entry['previous_rank'] - rank

            leaderboard_entries.append(LeaderboardEntry(
                learner_id=entry['learner_id'],
                learner_name=entry['name'],
                score=entry['score'],
                rank=rank,
                details=entry['details'],
                movement=movement
            ))

        return leaderboard_entries

    def get_learner_position(self, learner_id: str,
                            leaderboard_type: LeaderboardType) -> Optional[LeaderboardEntry]:
        """
        Get a specific learner's position on a leaderboard

        Args:
            learner_id: Learner identifier
            leaderboard_type: Type of leaderboard

        Returns:
            Learner's leaderboard entry or None
        """
        leaderboard = self.get_leaderboard(leaderboard_type, limit=1000)

        for entry in leaderboard:
            if entry.learner_id == learner_id:
                return entry

        return None

    def get_learner_rankings(self, learner_id: str) -> Dict[LeaderboardType, LeaderboardEntry]:
        """
        Get all rankings for a specific learner

        Args:
            learner_id: Learner identifier

        Returns:
            Dictionary of leaderboard entries by type
        """
        rankings = {}

        for leaderboard_type in LeaderboardType:
            position = self.get_learner_position(learner_id, leaderboard_type)
            if position:
                rankings[leaderboard_type] = position

        return rankings

    def _get_learner_rank(self, learner_id: str,
                         leaderboard_type: LeaderboardType) -> Optional[int]:
        """
        Get learner's current rank on a leaderboard

        Args:
            learner_id: Learner identifier
            leaderboard_type: Type of leaderboard

        Returns:
            Current rank or None
        """
        leaderboard = self.get_leaderboard(leaderboard_type)
        for entry in leaderboard:
            if entry.learner_id == learner_id:
                return entry.rank
        return None

    def get_nearby_learners(self, learner_id: str,
                           leaderboard_type: LeaderboardType,
                           window: int = 2) -> List[LeaderboardEntry]:
        """
        Get learners near a specific learner's rank

        Args:
            learner_id: Learner identifier
            leaderboard_type: Type of leaderboard
            window: Number of positions above and below

        Returns:
            List of nearby leaderboard entries
        """
        leaderboard = self.get_leaderboard(leaderboard_type, limit=1000)

        # Find learner's position
        learner_index = None
        for i, entry in enumerate(leaderboard):
            if entry.learner_id == learner_id:
                learner_index = i
                break

        if learner_index is None:
            return []

        # Get nearby entries
        start = max(0, learner_index - window)
        end = min(len(leaderboard), learner_index + window + 1)

        return leaderboard[start:end]

    def get_top_movers(self, leaderboard_type: LeaderboardType,
                       limit: int = 5) -> List[LeaderboardEntry]:
        """
        Get learners with biggest positive rank changes

        Args:
            leaderboard_type: Type of leaderboard
            limit: Number of top movers to return

        Returns:
            List of top moving learners
        """
        leaderboard = self.get_leaderboard(leaderboard_type)

        # Filter for positive movement
        movers = [entry for entry in leaderboard if entry.movement > 0]

        # Sort by movement
        movers.sort(key=lambda x: x.movement, reverse=True)

        return movers[:limit]

    def generate_weekly_summary(self, leaderboard_type: LeaderboardType) -> Dict[str, Any]:
        """
        Generate weekly leaderboard summary for announcements

        Args:
            leaderboard_type: Type of leaderboard

        Returns:
            Summary dictionary
        """
        leaderboard = self.get_leaderboard(leaderboard_type, limit=10)
        top_movers = self.get_top_movers(leaderboard_type, limit=3)

        summary = {
            'leaderboard_type': leaderboard_type.value,
            'top_3': [
                {
                    'rank': entry.rank,
                    'name': entry.learner_name,
                    'score': entry.score,
                    'details': entry.details
                }
                for entry in leaderboard[:3]
            ],
            'biggest_movers': [
                {
                    'name': entry.learner_name,
                    'movement': entry.movement,
                    'new_rank': entry.rank
                }
                for entry in top_movers
            ],
            'total_participants': len(self.leaderboards.get(leaderboard_type, {})),
            'generated_at': datetime.utcnow().isoformat()
        }

        return summary

    def reset_weekly_leaderboards(self, preserve_types: List[LeaderboardType] = None):
        """
        Reset weekly leaderboards while preserving specified types

        Args:
            preserve_types: Leaderboard types to preserve
        """
        if preserve_types is None:
            preserve_types = [LeaderboardType.CAREER_CAPITAL, LeaderboardType.SKILL_MASTERY]

        # Archive current data
        self.historical_data[datetime.utcnow().isoformat()] = self.leaderboards.copy()

        # Reset non-preserved leaderboards
        for leaderboard_type in LeaderboardType:
            if leaderboard_type not in preserve_types:
                self.leaderboards[leaderboard_type] = {}

        logger.info(f"Weekly leaderboards reset. Preserved: {[t.value for t in preserve_types]}")