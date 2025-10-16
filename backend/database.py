"""
Simple SQLite database for persisting nudges, achievements, and predictions
Lightweight solution for MVP - no need for complex ORM
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class SimpleDB:
    """Simple SQLite database wrapper for MVP"""

    def __init__(self, db_path: str = "learner_platform.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create nudge history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nudge_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nudge_id TEXT UNIQUE,
                learner_id TEXT,
                risk_signal TEXT,
                intensity TEXT,
                channel TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_received BOOLEAN DEFAULT 0,
                response_time TIMESTAMP,
                effectiveness_score REAL
            )
        """)

        # Create prediction history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                learner_id TEXT,
                risk_score REAL,
                risk_label TEXT,
                risk_color TEXT,
                top_risk_factors TEXT,
                recommended_interventions TEXT,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_type TEXT DEFAULT 'random_forest'
            )
        """)

        # Create achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                learner_id TEXT,
                achievement_name TEXT,
                achievement_type TEXT,
                description TEXT,
                points_awarded INTEGER,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(learner_id, achievement_name)
            )
        """)

        # Create weekly streaks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_streaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                learner_id TEXT,
                week_number INTEGER,
                goals_met BOOLEAN DEFAULT 0,
                streak_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(learner_id, week_number)
            )
        """)

        conn.commit()
        conn.close()

    def save_nudge(self, nudge_data: Dict[str, Any]) -> bool:
        """Save nudge to history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO nudge_history
                (nudge_id, learner_id, risk_signal, intensity, channel, content)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                nudge_data.get('nudge_id'),
                nudge_data.get('learner_id'),
                nudge_data.get('risk_signal'),
                nudge_data.get('intensity'),
                nudge_data.get('channel'),
                nudge_data.get('content')
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving nudge: {e}")
            return False

    def update_nudge_response(self, nudge_id: str, effectiveness_score: float) -> bool:
        """Update nudge response tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE nudge_history
                SET response_received = 1,
                    response_time = CURRENT_TIMESTAMP,
                    effectiveness_score = ?
                WHERE nudge_id = ?
            """, (effectiveness_score, nudge_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating nudge response: {e}")
            return False

    def save_prediction(self, prediction_data: Dict[str, Any]) -> bool:
        """Save prediction to history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO prediction_history
                (learner_id, risk_score, risk_label, risk_color,
                 top_risk_factors, recommended_interventions, model_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction_data.get('learner_id'),
                prediction_data.get('risk_score'),
                prediction_data.get('risk_label'),
                prediction_data.get('risk_color'),
                json.dumps(prediction_data.get('top_risk_factors', [])),
                json.dumps(prediction_data.get('recommended_interventions', [])),
                prediction_data.get('model_type', 'random_forest')
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving prediction: {e}")
            return False

    def save_achievement(self, achievement_data: Dict[str, Any]) -> bool:
        """Save learner achievement"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR IGNORE INTO achievements
                (learner_id, achievement_name, achievement_type, description, points_awarded)
                VALUES (?, ?, ?, ?, ?)
            """, (
                achievement_data.get('learner_id'),
                achievement_data.get('achievement_name'),
                achievement_data.get('achievement_type'),
                achievement_data.get('description'),
                achievement_data.get('points_awarded', 0)
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving achievement: {e}")
            return False

    def get_learner_achievements(self, learner_id: str) -> List[Dict[str, Any]]:
        """Get all achievements for a learner"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM achievements
                WHERE learner_id = ?
                ORDER BY earned_at DESC
            """, (learner_id,))

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting achievements: {e}")
            return []

    def update_weekly_streak(self, learner_id: str, week_number: int, goals_met: bool) -> bool:
        """Update weekly streak tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get current streak count
            cursor.execute("""
                SELECT streak_count FROM weekly_streaks
                WHERE learner_id = ?
                ORDER BY week_number DESC
                LIMIT 1
            """, (learner_id,))

            result = cursor.fetchone()
            current_streak = result[0] if result else 0

            # Calculate new streak
            new_streak = current_streak + 1 if goals_met else 0

            # Insert or update
            cursor.execute("""
                INSERT OR REPLACE INTO weekly_streaks
                (learner_id, week_number, goals_met, streak_count)
                VALUES (?, ?, ?, ?)
            """, (learner_id, week_number, goals_met, new_streak))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating streak: {e}")
            return False

    def get_nudge_effectiveness_stats(self) -> Dict[str, Any]:
        """Get nudge effectiveness statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Overall response rate
            cursor.execute("""
                SELECT
                    COUNT(*) as total_nudges,
                    SUM(CASE WHEN response_received = 1 THEN 1 ELSE 0 END) as responses_received,
                    AVG(CASE WHEN effectiveness_score IS NOT NULL THEN effectiveness_score ELSE 0 END) as avg_effectiveness
                FROM nudge_history
            """)

            stats = cursor.fetchone()
            conn.close()

            total_nudges = stats[0] or 0
            responses = stats[1] or 0
            avg_effectiveness = stats[2] or 0

            return {
                'total_nudges': total_nudges,
                'responses_received': responses,
                'response_rate': (responses / total_nudges * 100) if total_nudges > 0 else 0,
                'avg_effectiveness': avg_effectiveness
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total_nudges': 0,
                'responses_received': 0,
                'response_rate': 0,
                'avg_effectiveness': 0
            }

    def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent predictions for monitoring"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM prediction_history
                ORDER BY prediction_date DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()
            conn.close()

            predictions = []
            for row in rows:
                pred = dict(row)
                # Parse JSON fields
                pred['top_risk_factors'] = json.loads(pred['top_risk_factors'])
                pred['recommended_interventions'] = json.loads(pred['recommended_interventions'])
                predictions.append(pred)

            return predictions
        except Exception as e:
            print(f"Error getting predictions: {e}")
            return []