"""
Synthetic Data Generator for Learner Engagement Platform
Creates realistic learner behavior data for ML training and testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
from faker import Faker
import os

fake = Faker()
np.random.seed(42)
random.seed(42)

class LearnerDataGenerator:
    """
    Generates synthetic learner data with realistic patterns
    """

    def __init__(self, num_learners: int = 500):
        self.num_learners = num_learners
        self.programs = ['data_science', 'machine_learning', 'mba', 'technology', 'marketing']
        self.learners = []

    def generate_learner_profile(self, learner_id: int) -> dict:
        """
        Generate a single learner profile with behavioral patterns
        """
        # Determine learner archetype (affects behavior patterns)
        archetype = np.random.choice([
            'high_performer',      # 20% - Consistently engaged, high scores
            'steady_learner',      # 35% - Regular engagement, moderate scores
            'struggling_learner',  # 25% - Low engagement, poor scores
            'inconsistent_learner', # 15% - Variable engagement
            'at_risk_learner'      # 5% - High dropout risk
        ], p=[0.20, 0.35, 0.25, 0.15, 0.05])

        # Base profile
        profile = {
            'id': f'learner_{learner_id:04d}',
            'name': fake.name(),
            'email': fake.email(),
            'program': random.choice(self.programs),
            'archetype': archetype,
            'enrollment_date': fake.date_between(start_date='-180d', end_date='-30d'),
            'years_work_experience': np.random.randint(0, 15),
            'prior_online_courses_completed': np.random.randint(0, 5),
            'concurrent_courses': np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1]),
            'has_scholarship': random.random() < 0.15,
            'career_change_goal': random.random() < 0.40,
            'weekly_study_hours_available': np.random.uniform(5, 25)
        }

        # Generate behavior based on archetype
        behavior = self._generate_behavior_pattern(archetype)
        profile.update(behavior)

        # Calculate dropout risk (target variable)
        profile['dropout_risk'] = self._calculate_dropout_risk(profile, archetype)

        return profile

    def _generate_behavior_pattern(self, archetype: str) -> dict:
        """
        Generate behavioral metrics based on learner archetype
        """
        if archetype == 'high_performer':
            return {
                # Engagement metrics
                'login_frequency_7days': np.random.randint(5, 10),
                'login_recency_hours': np.random.uniform(0, 48),
                'avg_session_duration_minutes': np.random.uniform(45, 90),
                'video_completion_rate': np.random.uniform(0.85, 1.0),
                'total_video_time_hours': np.random.uniform(20, 40),
                'current_week_material_access': np.random.randint(5, 15),
                'other_weeks_material_access': np.random.randint(2, 8),

                # Forum participation
                'forum_posts_count': np.random.randint(5, 20),
                'forum_replies_count': np.random.randint(10, 30),
                'forum_threads_viewed': np.random.randint(20, 50),
                'forum_helpful_answers': np.random.randint(5, 15),

                # Help-seeking
                'accessed_faq': random.random() < 0.3,
                'contacted_support': random.random() < 0.1,
                'support_tickets_count': np.random.randint(0, 2),

                # Performance metrics
                'avg_quiz_score': np.random.uniform(85, 98),
                'latest_quiz_score': np.random.uniform(80, 100),
                'quiz_score_trend': np.random.uniform(0, 0.5),  # Improving
                'assignments_completed_pct': np.random.uniform(90, 100),
                'assignments_on_time_pct': np.random.uniform(95, 100),
                'avg_assignment_score': np.random.uniform(85, 95),
                'weekly_test_submission_rate': np.random.uniform(95, 100),
                'weekly_test_avg_score': np.random.uniform(85, 95),
                'missed_last_weekly_test': False,

                # Pacing metrics
                'course_progress_pct': np.random.uniform(70, 100),
                'modules_completed': np.random.randint(8, 15),
                'behind_schedule_days': 0,
                'practice_activities_completed_pct': np.random.uniform(80, 100),
                'optional_content_accessed_pct': np.random.uniform(60, 100),
                'late_submissions_count': np.random.randint(0, 1),
                'avg_submission_delay_hours': 0,

                # Streak data
                'weekly_streak': np.random.randint(4, 12),
                'weekly_goals_met': np.random.randint(8, 15)
            }

        elif archetype == 'steady_learner':
            return {
                # Engagement metrics
                'login_frequency_7days': np.random.randint(3, 7),
                'login_recency_hours': np.random.uniform(24, 72),
                'avg_session_duration_minutes': np.random.uniform(30, 60),
                'video_completion_rate': np.random.uniform(0.65, 0.85),
                'total_video_time_hours': np.random.uniform(15, 25),
                'current_week_material_access': np.random.randint(3, 8),
                'other_weeks_material_access': np.random.randint(1, 5),

                # Forum participation
                'forum_posts_count': np.random.randint(2, 10),
                'forum_replies_count': np.random.randint(5, 15),
                'forum_threads_viewed': np.random.randint(10, 30),
                'forum_helpful_answers': np.random.randint(2, 8),

                # Help-seeking
                'accessed_faq': random.random() < 0.5,
                'contacted_support': random.random() < 0.2,
                'support_tickets_count': np.random.randint(0, 3),

                # Performance metrics
                'avg_quiz_score': np.random.uniform(70, 85),
                'latest_quiz_score': np.random.uniform(65, 85),
                'quiz_score_trend': np.random.uniform(-0.1, 0.2),
                'assignments_completed_pct': np.random.uniform(75, 95),
                'assignments_on_time_pct': np.random.uniform(70, 90),
                'avg_assignment_score': np.random.uniform(70, 85),
                'weekly_test_submission_rate': np.random.uniform(70, 90),
                'weekly_test_avg_score': np.random.uniform(70, 85),
                'missed_last_weekly_test': random.random() < 0.2,

                # Pacing metrics
                'course_progress_pct': np.random.uniform(50, 80),
                'modules_completed': np.random.randint(5, 10),
                'behind_schedule_days': np.random.randint(0, 7),
                'practice_activities_completed_pct': np.random.uniform(60, 85),
                'optional_content_accessed_pct': np.random.uniform(30, 70),
                'late_submissions_count': np.random.randint(1, 4),
                'avg_submission_delay_hours': np.random.uniform(0, 24),

                # Streak data
                'weekly_streak': np.random.randint(2, 6),
                'weekly_goals_met': np.random.randint(4, 10)
            }

        elif archetype == 'struggling_learner':
            return {
                # Engagement metrics
                'login_frequency_7days': np.random.randint(0, 3),
                'login_recency_hours': np.random.uniform(72, 168),
                'avg_session_duration_minutes': np.random.uniform(10, 30),
                'video_completion_rate': np.random.uniform(0.20, 0.50),
                'total_video_time_hours': np.random.uniform(5, 15),
                'current_week_material_access': np.random.randint(0, 3),
                'other_weeks_material_access': np.random.randint(0, 2),

                # Forum participation
                'forum_posts_count': np.random.randint(0, 3),
                'forum_replies_count': np.random.randint(0, 5),
                'forum_threads_viewed': np.random.randint(0, 10),
                'forum_helpful_answers': 0,

                # Help-seeking
                'accessed_faq': random.random() < 0.7,
                'contacted_support': random.random() < 0.4,
                'support_tickets_count': np.random.randint(2, 6),

                # Performance metrics
                'avg_quiz_score': np.random.uniform(40, 65),
                'latest_quiz_score': np.random.uniform(30, 60),
                'quiz_score_trend': np.random.uniform(-0.3, 0),
                'assignments_completed_pct': np.random.uniform(40, 70),
                'assignments_on_time_pct': np.random.uniform(30, 60),
                'avg_assignment_score': np.random.uniform(45, 65),
                'weekly_test_submission_rate': np.random.uniform(30, 60),
                'weekly_test_avg_score': np.random.uniform(40, 60),
                'missed_last_weekly_test': random.random() < 0.6,

                # Pacing metrics
                'course_progress_pct': np.random.uniform(20, 50),
                'modules_completed': np.random.randint(2, 5),
                'behind_schedule_days': np.random.randint(7, 21),
                'practice_activities_completed_pct': np.random.uniform(20, 50),
                'optional_content_accessed_pct': np.random.uniform(0, 30),
                'late_submissions_count': np.random.randint(3, 8),
                'avg_submission_delay_hours': np.random.uniform(24, 72),

                # Streak data
                'weekly_streak': np.random.randint(0, 2),
                'weekly_goals_met': np.random.randint(0, 3)
            }

        elif archetype == 'inconsistent_learner':
            # High variance in behavior
            return {
                # Engagement metrics
                'login_frequency_7days': np.random.randint(1, 8),
                'login_recency_hours': np.random.uniform(12, 120),
                'avg_session_duration_minutes': np.random.uniform(15, 75),
                'video_completion_rate': np.random.uniform(0.30, 0.80),
                'total_video_time_hours': np.random.uniform(8, 30),
                'current_week_material_access': np.random.randint(1, 10),
                'other_weeks_material_access': np.random.randint(0, 6),

                # Forum participation
                'forum_posts_count': np.random.randint(0, 15),
                'forum_replies_count': np.random.randint(0, 20),
                'forum_threads_viewed': np.random.randint(5, 35),
                'forum_helpful_answers': np.random.randint(0, 5),

                # Help-seeking
                'accessed_faq': random.random() < 0.5,
                'contacted_support': random.random() < 0.3,
                'support_tickets_count': np.random.randint(1, 4),

                # Performance metrics (high variance)
                'avg_quiz_score': np.random.uniform(50, 85),
                'latest_quiz_score': np.random.uniform(40, 90),
                'quiz_score_trend': np.random.uniform(-0.5, 0.5),
                'assignments_completed_pct': np.random.uniform(50, 90),
                'assignments_on_time_pct': np.random.uniform(40, 80),
                'avg_assignment_score': np.random.uniform(55, 80),
                'weekly_test_submission_rate': np.random.uniform(40, 85),
                'weekly_test_avg_score': np.random.uniform(50, 80),
                'missed_last_weekly_test': random.random() < 0.4,

                # Pacing metrics
                'course_progress_pct': np.random.uniform(30, 70),
                'modules_completed': np.random.randint(3, 8),
                'behind_schedule_days': np.random.randint(3, 14),
                'practice_activities_completed_pct': np.random.uniform(30, 75),
                'optional_content_accessed_pct': np.random.uniform(10, 60),
                'late_submissions_count': np.random.randint(2, 6),
                'avg_submission_delay_hours': np.random.uniform(6, 48),

                # Streak data
                'weekly_streak': np.random.randint(0, 4),
                'weekly_goals_met': np.random.randint(2, 6)
            }

        else:  # at_risk_learner
            return {
                # Engagement metrics (very low)
                'login_frequency_7days': np.random.randint(0, 2),
                'login_recency_hours': np.random.uniform(120, 336),  # 5-14 days
                'avg_session_duration_minutes': np.random.uniform(5, 20),
                'video_completion_rate': np.random.uniform(0.05, 0.30),
                'total_video_time_hours': np.random.uniform(1, 8),
                'current_week_material_access': np.random.randint(0, 1),
                'other_weeks_material_access': 0,

                # Forum participation (minimal)
                'forum_posts_count': 0,
                'forum_replies_count': np.random.randint(0, 2),
                'forum_threads_viewed': np.random.randint(0, 5),
                'forum_helpful_answers': 0,

                # Help-seeking (either high or none)
                'accessed_faq': random.random() < 0.8,
                'contacted_support': random.random() < 0.5,
                'support_tickets_count': np.random.randint(0, 8),

                # Performance metrics (very poor)
                'avg_quiz_score': np.random.uniform(20, 50),
                'latest_quiz_score': np.random.uniform(10, 45),
                'quiz_score_trend': np.random.uniform(-0.5, -0.1),
                'assignments_completed_pct': np.random.uniform(10, 40),
                'assignments_on_time_pct': np.random.uniform(0, 30),
                'avg_assignment_score': np.random.uniform(20, 50),
                'weekly_test_submission_rate': np.random.uniform(0, 30),
                'weekly_test_avg_score': np.random.uniform(20, 45),
                'missed_last_weekly_test': True,

                # Pacing metrics (far behind)
                'course_progress_pct': np.random.uniform(5, 25),
                'modules_completed': np.random.randint(0, 3),
                'behind_schedule_days': np.random.randint(14, 30),
                'practice_activities_completed_pct': np.random.uniform(0, 20),
                'optional_content_accessed_pct': 0,
                'late_submissions_count': np.random.randint(5, 10),
                'avg_submission_delay_hours': np.random.uniform(48, 120),

                # Streak data (broken)
                'weekly_streak': 0,
                'weekly_goals_met': 0
            }

    def _calculate_dropout_risk(self, profile: dict, archetype: str) -> int:
        """
        Calculate dropout risk label (0: retained, 1: dropout)
        Based on archetype and behavior patterns
        """
        # Base dropout probabilities by archetype
        dropout_probs = {
            'high_performer': 0.05,
            'steady_learner': 0.15,
            'struggling_learner': 0.60,
            'inconsistent_learner': 0.40,
            'at_risk_learner': 0.85
        }

        base_prob = dropout_probs[archetype]

        # Adjust based on specific metrics
        if profile['avg_quiz_score'] < 50:
            base_prob += 0.15
        if profile['login_frequency_7days'] < 2:
            base_prob += 0.10
        if profile['behind_schedule_days'] > 14:
            base_prob += 0.10
        if profile['weekly_streak'] == 0:
            base_prob += 0.05
        if profile['course_progress_pct'] < 30:
            base_prob += 0.10

        # Cap at 0.95
        final_prob = min(base_prob, 0.95)

        # Return binary label
        return 1 if random.random() < final_prob else 0

    def generate_dataset(self) -> pd.DataFrame:
        """
        Generate full dataset
        """
        print(f"Generating {self.num_learners} learner profiles...")

        for i in range(self.num_learners):
            if i % 100 == 0:
                print(f"  Generated {i}/{self.num_learners} learners...")

            learner = self.generate_learner_profile(i)
            self.learners.append(learner)

        df = pd.DataFrame(self.learners)

        # Remove archetype column (not used in ML)
        df = df.drop('archetype', axis=1)

        print(f"Dataset generation complete!")
        print(f"Shape: {df.shape}")
        print(f"Dropout rate: {df['dropout_risk'].mean():.2%}")

        return df

def main():
    """
    Main function to generate and save data
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Generate training data
    generator = LearnerDataGenerator(num_learners=1000)
    df = generator.generate_dataset()

    # Save to CSV
    output_path = 'data/sample_learners.csv'
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")

    # Generate smaller test dataset
    test_generator = LearnerDataGenerator(num_learners=200)
    test_df = test_generator.generate_dataset()
    test_df.to_csv('data/test_learners.csv', index=False)
    print(f"Test data saved to data/test_learners.csv")

    # Print sample statistics
    print("\nDataset Statistics:")
    print("-" * 40)
    print(f"Total learners: {len(df)}")
    print(f"Features: {len(df.columns) - 1}")
    print(f"Dropout rate: {df['dropout_risk'].mean():.2%}")
    print(f"High performers: {(df['avg_quiz_score'] > 85).sum()}")
    print(f"At risk: {(df['dropout_risk'] == 1).sum()}")
    print("\nSample features:")
    print(df.columns.tolist()[:10])

if __name__ == "__main__":
    main()