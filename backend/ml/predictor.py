"""
Machine Learning Predictor Module for Dropout Risk Assessment
Implements Random Forest and Boosted Decision Trees as per idea.txt
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import recall_score, precision_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, Tuple, Any, Optional, List
from datetime import datetime
import logging

from .feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)

class DropoutPredictor:
    """
    Main predictor class implementing ML models for dropout risk assessment
    Optimized for RECALL as per idea.txt recommendations
    """

    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize predictor with specified model type

        Args:
            model_type: 'random_forest', 'decision_tree', or 'gradient_boosting'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_engineer = FeatureEngineer()
        self.is_trained = False
        self.model_path = 'data/trained_models'
        self.performance_metrics = {}

        # Initialize model based on type
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the ML model with optimized parameters"""
        if self.model_type == 'random_forest':
            # Random Forest optimized for recall
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced',  # Handle class imbalance
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'gradient_boosting':
            # Gradient Boosting (Boosted Decision Trees)
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                min_samples_split=5,
                min_samples_leaf=2,
                subsample=0.8,
                random_state=42
            )
        else:  # decision_tree
            # Single Decision Tree
            self.model = DecisionTreeClassifier(
                max_depth=7,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced',
                random_state=42
            )

    def train(self, X: np.ndarray, y: np.ndarray,
              validate: bool = True) -> Dict[str, float]:
        """
        Train the model on provided data

        Args:
            X: Feature matrix
            y: Target labels (0: retained, 1: dropout)
            validate: Whether to perform cross-validation

        Returns:
            Dictionary of performance metrics
        """
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)

            if validate:
                # Split for validation
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=0.2, random_state=42, stratify=y
                )

                # Train model
                self.model.fit(X_train, y_train)

                # Predict on test set
                y_pred = self.model.predict(X_test)
                y_pred_proba = self.model.predict_proba(X_test)[:, 1]

                # Calculate metrics (optimizing for RECALL as per idea.txt)
                self.performance_metrics = {
                    'recall': recall_score(y_test, y_pred),  # PRIMARY METRIC
                    'precision': precision_score(y_test, y_pred),
                    'f1_score': f1_score(y_test, y_pred),
                    'auc_roc': roc_auc_score(y_test, y_pred_proba),
                    'accuracy': self.model.score(X_test, y_test)
                }

                # Log performance
                logger.info(f"Model trained with Recall: {self.performance_metrics['recall']:.3f}")

                # Cross-validation for robustness
                cv_scores = cross_val_score(
                    self.model, X_scaled, y, cv=5, scoring='recall'
                )
                self.performance_metrics['cv_recall_mean'] = cv_scores.mean()
                self.performance_metrics['cv_recall_std'] = cv_scores.std()

            else:
                # Train on full dataset
                self.model.fit(X_scaled, y)
                self.performance_metrics = {'trained_on_full_data': True}

            self.is_trained = True
            return self.performance_metrics

        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise

    def predict_risk(self, learner_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict dropout risk for a single learner

        Args:
            learner_data: Dictionary with learner's features

        Returns:
            Risk assessment dictionary
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        try:
            # Extract features
            features = self.feature_engineer.extract_features(learner_data)
            features_scaled = self.scaler.transform([features])

            # Get prediction and probability
            risk_probability = self.model.predict_proba(features_scaled)[0, 1]
            risk_prediction = self.model.predict(features_scaled)[0]

            # Determine risk level (traffic light system from idea.txt)
            if risk_probability >= 0.7:
                risk_label = 'high'
                risk_color = 'red'
            elif risk_probability >= 0.4:
                risk_label = 'medium'
                risk_color = 'yellow'
            else:
                risk_label = 'low'
                risk_color = 'green'

            # Get feature importance for this prediction
            feature_contributions = self._get_feature_contributions(features)

            return {
                'risk_score': float(risk_probability),
                'risk_label': risk_label,
                'risk_color': risk_color,
                'will_dropout': bool(risk_prediction),
                'confidence': float(max(risk_probability, 1 - risk_probability)),
                'top_risk_factors': feature_contributions[:5],
                'prediction_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error predicting risk: {e}")
            raise

    def predict_batch(self, learners_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict risk for multiple learners

        Args:
            learners_data: List of learner data dictionaries

        Returns:
            List of risk assessments
        """
        predictions = []
        for learner_data in learners_data:
            try:
                prediction = self.predict_risk(learner_data)
                prediction['learner_id'] = learner_data.get('id', 'unknown')
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error predicting for learner {learner_data.get('id')}: {e}")
                predictions.append({
                    'learner_id': learner_data.get('id', 'unknown'),
                    'error': str(e),
                    'risk_score': 0.5,
                    'risk_label': 'unknown'
                })

        return predictions

    def _get_feature_contributions(self, features: np.ndarray) -> List[Tuple[str, float]]:
        """
        Get feature contributions to the prediction
        """
        if not hasattr(self.model, 'feature_importances_'):
            return []

        feature_names = self.feature_engineer.get_feature_names()
        importances = self.model.feature_importances_

        # Calculate weighted feature values
        weighted_features = features * importances

        # Sort by importance
        feature_contributions = list(zip(feature_names, weighted_features))
        feature_contributions.sort(key=lambda x: abs(x[1]), reverse=True)

        # Return top contributing factors
        return [(name, float(value)) for name, value in feature_contributions]

    def save_model(self, model_name: str = None):
        """
        Save trained model to disk

        Args:
            model_name: Custom name for the model file
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        os.makedirs(self.model_path, exist_ok=True)

        if model_name is None:
            model_name = f"{self.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Save model
        model_file = os.path.join(self.model_path, f"{model_name}.pkl")
        joblib.dump(self.model, model_file)

        # Save scaler
        scaler_file = os.path.join(self.model_path, f"{model_name}_scaler.pkl")
        joblib.dump(self.scaler, scaler_file)

        # Save metrics
        metrics_file = os.path.join(self.model_path, f"{model_name}_metrics.json")
        import json
        with open(metrics_file, 'w') as f:
            json.dump(self.performance_metrics, f, indent=2)

        logger.info(f"Model saved as {model_name}")
        return model_name

    def load_model(self, model_name: str):
        """
        Load a trained model from disk

        Args:
            model_name: Name of the model to load
        """
        try:
            # Load model
            model_file = os.path.join(self.model_path, f"{model_name}.pkl")
            self.model = joblib.load(model_file)

            # Load scaler
            scaler_file = os.path.join(self.model_path, f"{model_name}_scaler.pkl")
            self.scaler = joblib.load(scaler_file)

            # Load metrics
            metrics_file = os.path.join(self.model_path, f"{model_name}_metrics.json")
            import json
            with open(metrics_file, 'r') as f:
                self.performance_metrics = json.load(f)

            self.is_trained = True
            logger.info(f"Model {model_name} loaded successfully")

        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            raise

    def explain_prediction(self, learner_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide detailed explanation of the prediction

        Returns interpretable explanation for stakeholders
        """
        prediction = self.predict_risk(learner_data)

        # Get feature values
        features = self.feature_engineer.extract_features(learner_data)
        feature_names = self.feature_engineer.get_feature_names()

        # Identify problematic areas
        problematic_features = []
        positive_features = []

        for i, (name, value) in enumerate(zip(feature_names, features)):
            if 'login_recency' in name and value > 72:  # >3 days
                problematic_features.append(f"Haven't logged in for {value:.0f} hours")
            elif 'quiz_score' in name and value < 0.6:
                problematic_features.append(f"Low quiz performance ({value*100:.0f}%)")
            elif 'video_completion' in name and value < 0.5:
                problematic_features.append(f"Low video engagement ({value*100:.0f}%)")
            elif 'missed_last_weekly' in name and value == 1:
                problematic_features.append("Missed last weekly assessment")
            elif 'behind_schedule' in name and value > 7:
                problematic_features.append(f"Behind schedule by {value:.0f} days")

            # Positive indicators
            if 'forum' in name and value > 5:
                positive_features.append("Active forum participation")
            elif 'assignment' in name and 'on_time' in name and value > 0.8:
                positive_features.append("Good assignment submission record")

        explanation = {
            **prediction,
            'risk_factors': problematic_features[:3] if problematic_features else ['No major concerns'],
            'positive_factors': positive_features[:2] if positive_features else ['Limited positive indicators'],
            'recommendation': self._generate_recommendation(prediction['risk_label'])
        }

        return explanation

    def _generate_recommendation(self, risk_label: str) -> str:
        """Generate actionable recommendation based on risk level"""
        recommendations = {
            'high': "Immediate intervention needed. Personal outreach recommended within 24 hours.",
            'medium': "Monitor closely. Automated engagement nudges should be increased.",
            'low': "Continue current engagement. Consider peer learning opportunities."
        }
        return recommendations.get(risk_label, "Continue monitoring")