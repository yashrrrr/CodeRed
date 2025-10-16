"""
Feature Engineering Module for Learner Dropout Prediction
Implements feature extraction based on idea.txt specifications
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """
    Extracts behavioral, performance, and contextual features for ML model
    Based on Table 1 from idea.txt with focus on professional learners
    """

    def __init__(self):
        self.feature_names = []

    def extract_features(self, learner_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract all features from a single learner's data

        Args:
            learner_data: Dictionary containing learner's behavioral and performance data

        Returns:
            Feature vector as numpy array
        """
        features = []

        # Behavioral/Engagement Indicators (Effort)
        features.extend(self._extract_engagement_features(learner_data))

        # Performance Indicators (Achievement)
        features.extend(self._extract_performance_features(learner_data))

        # Pacing Indicators
        features.extend(self._extract_pacing_features(learner_data))

        # Contextual Indicators
        features.extend(self._extract_contextual_features(learner_data))

        return np.array(features)

    def _extract_engagement_features(self, data: Dict) -> List[float]:
        """Extract engagement-related features"""
        features = []

        # Login activity features
        features.append(data.get('login_frequency_7days', 0))  # Logins in last 7 days
        features.append(data.get('login_recency_hours', 168))  # Hours since last login
        features.append(data.get('avg_session_duration_minutes', 0))  # Avg session length

        # Content engagement
        features.append(data.get('video_completion_rate', 0))  # % videos watched
        features.append(data.get('total_video_time_hours', 0))  # Total video watch time
        features.append(data.get('current_week_material_access', 0))  # Current week access count
        features.append(data.get('other_weeks_material_access', 0))  # Other weeks access count

        # Forum participation
        features.append(data.get('forum_posts_count', 0))
        features.append(data.get('forum_replies_count', 0))
        features.append(data.get('forum_threads_viewed', 0))

        # Help-seeking behavior
        features.append(1 if data.get('accessed_faq', False) else 0)
        features.append(1 if data.get('contacted_support', False) else 0)
        features.append(data.get('support_tickets_count', 0))

        return features

    def _extract_performance_features(self, data: Dict) -> List[float]:
        """Extract performance-related features"""
        features = []

        # Quiz and assessment scores
        features.append(data.get('avg_quiz_score', 0) / 100.0)  # Normalized to 0-1
        features.append(data.get('latest_quiz_score', 0) / 100.0)
        features.append(data.get('quiz_score_trend', 0))  # -1 to 1 (declining to improving)

        # Assignment performance
        features.append(data.get('assignments_completed_pct', 0) / 100.0)
        features.append(data.get('assignments_on_time_pct', 0) / 100.0)
        features.append(data.get('avg_assignment_score', 0) / 100.0)

        # Weekly mini-tests (high predictive power per idea.txt)
        features.append(data.get('weekly_test_submission_rate', 0) / 100.0)
        features.append(data.get('weekly_test_avg_score', 0) / 100.0)
        features.append(1 if data.get('missed_last_weekly_test', False) else 0)

        return features

    def _extract_pacing_features(self, data: Dict) -> List[float]:
        """Extract pacing-related features"""
        features = []

        # Progress indicators
        features.append(data.get('course_progress_pct', 0) / 100.0)
        features.append(data.get('modules_completed', 0))
        features.append(data.get('behind_schedule_days', 0))

        # Practice activities
        features.append(data.get('practice_activities_completed_pct', 0) / 100.0)
        features.append(data.get('optional_content_accessed_pct', 0) / 100.0)

        # Submission patterns
        features.append(data.get('late_submissions_count', 0))
        features.append(data.get('avg_submission_delay_hours', 0))

        return features

    def _extract_contextual_features(self, data: Dict) -> List[float]:
        """Extract contextual features (use with caution for fairness)"""
        features = []

        # Academic background
        features.append(data.get('prior_online_courses_completed', 0))
        features.append(data.get('years_work_experience', 0))

        # Current context
        features.append(data.get('concurrent_courses', 0))
        features.append(1 if data.get('has_scholarship', False) else 0)

        # Program type (encoded as one-hot)
        program_type = data.get('program_type', 'other')
        features.append(1 if program_type == 'data_science' else 0)
        features.append(1 if program_type == 'mba' else 0)
        features.append(1 if program_type == 'technology' else 0)

        # Professional context
        features.append(1 if data.get('career_change_goal', False) else 0)
        features.append(data.get('weekly_study_hours_available', 10))

        return features

    def get_feature_names(self) -> List[str]:
        """Return list of feature names for interpretability"""
        return [
            # Engagement features
            'login_frequency_7days', 'login_recency_hours', 'avg_session_duration_minutes',
            'video_completion_rate', 'total_video_time_hours', 'current_week_material_access',
            'other_weeks_material_access', 'forum_posts_count', 'forum_replies_count',
            'forum_threads_viewed', 'accessed_faq', 'contacted_support', 'support_tickets_count',

            # Performance features
            'avg_quiz_score', 'latest_quiz_score', 'quiz_score_trend',
            'assignments_completed_pct', 'assignments_on_time_pct', 'avg_assignment_score',
            'weekly_test_submission_rate', 'weekly_test_avg_score', 'missed_last_weekly_test',

            # Pacing features
            'course_progress_pct', 'modules_completed', 'behind_schedule_days',
            'practice_activities_completed_pct', 'optional_content_accessed_pct',
            'late_submissions_count', 'avg_submission_delay_hours',

            # Contextual features
            'prior_online_courses_completed', 'years_work_experience', 'concurrent_courses',
            'has_scholarship', 'is_data_science', 'is_mba', 'is_technology',
            'career_change_goal', 'weekly_study_hours_available'
        ]

    def create_feature_importance_report(self, model, top_n: int = 10) -> pd.DataFrame:
        """
        Generate feature importance report for model interpretability
        """
        feature_names = self.get_feature_names()

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            })
            return feature_df.nlargest(top_n, 'importance')

        return pd.DataFrame()

    def engineer_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived features from raw data
        """
        df = df.copy()

        # Engagement intensity score
        df['engagement_intensity'] = (
            df['login_frequency_7days'] * 0.3 +
            df['video_completion_rate'] * 0.3 +
            df['forum_participation_score'] * 0.2 +
            df['practice_completion_rate'] * 0.2
        )

        # Risk momentum (are things getting better or worse?)
        df['performance_momentum'] = df['quiz_score_trend'] * df['avg_quiz_score']

        # Time management score
        df['time_management_score'] = 1 - (df['late_submissions_count'] /
                                           (df['total_submissions'] + 1))

        # Help-seeking ratio
        df['help_seeking_ratio'] = (df['support_contacts'] + df['faq_views']) / \
                                   (df['quiz_failures'] + 1)

        return df