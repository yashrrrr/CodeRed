"""
Model Training Pipeline for Dropout Prediction
Handles data preparation, training, and model selection
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, Optional
import logging
import os

from .predictor import DropoutPredictor
from .feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)

class ModelTrainer:
    """
    Handles model training, hyperparameter tuning, and model selection
    """

    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.best_model = None
        self.training_results = {}

    def prepare_training_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load and prepare data for training

        Args:
            data_path: Path to CSV file with training data

        Returns:
            X (features) and y (labels) arrays
        """
        try:
            # Load data
            df = pd.read_csv(data_path)
            logger.info(f"Loaded {len(df)} records from {data_path}")

            # Extract features for each learner
            X = []
            for _, row in df.iterrows():
                learner_data = row.to_dict()
                features = self.feature_engineer.extract_features(learner_data)
                X.append(features)

            X = np.array(X)
            y = df['dropout_risk'].values  # 0: retained, 1: dropout

            logger.info(f"Prepared {X.shape[0]} samples with {X.shape[1]} features")
            logger.info(f"Class distribution - Retained: {sum(y==0)}, Dropout: {sum(y==1)}")

            return X, y

        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise

    def train_all_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Dict]:
        """
        Train all model types and compare performance

        Args:
            X: Feature matrix
            y: Target labels

        Returns:
            Dictionary of results for each model type
        """
        model_types = ['random_forest', 'gradient_boosting', 'decision_tree']
        results = {}

        for model_type in model_types:
            logger.info(f"Training {model_type}...")

            # Create and train model
            predictor = DropoutPredictor(model_type=model_type)
            metrics = predictor.train(X, y, validate=True)

            # Store results
            results[model_type] = {
                'predictor': predictor,
                'metrics': metrics
            }

            logger.info(f"{model_type} - Recall: {metrics.get('recall', 0):.3f}, "
                       f"F1: {metrics.get('f1_score', 0):.3f}")

        # Select best model based on RECALL (as per idea.txt)
        best_model_type = max(results.keys(),
                             key=lambda k: results[k]['metrics'].get('recall', 0))
        self.best_model = results[best_model_type]['predictor']
        self.training_results = results

        logger.info(f"Best model: {best_model_type} with Recall: "
                   f"{results[best_model_type]['metrics'].get('recall', 0):.3f}")

        return results

    def hyperparameter_tuning(self, X: np.ndarray, y: np.ndarray,
                            model_type: str = 'random_forest') -> DropoutPredictor:
        """
        Perform hyperparameter tuning using GridSearchCV

        Args:
            X: Feature matrix
            y: Target labels
            model_type: Type of model to tune

        Returns:
            Tuned predictor
        """
        logger.info(f"Starting hyperparameter tuning for {model_type}...")

        predictor = DropoutPredictor(model_type=model_type)

        # Define parameter grids for different models
        param_grids = {
            'random_forest': {
                'n_estimators': [50, 100, 150],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'gradient_boosting': {
                'n_estimators': [50, 100, 150],
                'learning_rate': [0.05, 0.1, 0.15],
                'max_depth': [3, 5, 7],
                'subsample': [0.7, 0.8, 0.9]
            },
            'decision_tree': {
                'max_depth': [5, 7, 10, 15],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'criterion': ['gini', 'entropy']
            }
        }

        param_grid = param_grids.get(model_type, {})

        # Create GridSearchCV
        grid_search = GridSearchCV(
            predictor.model,
            param_grid,
            cv=StratifiedKFold(n_splits=5),
            scoring='recall',  # Optimize for recall
            n_jobs=-1,
            verbose=1
        )

        # Fit scaler and transform data
        X_scaled = predictor.scaler.fit_transform(X)

        # Perform grid search
        grid_search.fit(X_scaled, y)

        # Update model with best parameters
        predictor.model = grid_search.best_estimator_
        predictor.is_trained = True

        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best recall score: {grid_search.best_score_:.3f}")

        return predictor

    def generate_performance_report(self, predictor: DropoutPredictor,
                                   X_test: np.ndarray, y_test: np.ndarray) -> str:
        """
        Generate detailed performance report

        Args:
            predictor: Trained predictor
            X_test: Test features
            y_test: Test labels

        Returns:
            Formatted report string
        """
        # Get predictions
        X_test_scaled = predictor.scaler.transform(X_test)
        y_pred = predictor.model.predict(X_test_scaled)

        # Generate classification report
        report = classification_report(y_test, y_pred,
                                      target_names=['Retained', 'Dropout'])

        # Add confusion matrix
        cm = confusion_matrix(y_test, y_pred)

        report += "\n\nConfusion Matrix:\n"
        report += f"              Predicted\n"
        report += f"              Retained  Dropout\n"
        report += f"Actual Retained   {cm[0, 0]:5d}   {cm[0, 1]:5d}\n"
        report += f"       Dropout    {cm[1, 0]:5d}   {cm[1, 1]:5d}\n"

        # Calculate key metrics
        tn, fp, fn, tp = cm.ravel()
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        dropout_catch_rate = tp / (tp + fn) if (tp + fn) > 0 else 0

        report += f"\nKey Metrics for Dropout Detection:\n"
        report += f"Dropout Catch Rate (Recall): {dropout_catch_rate:.1%}\n"
        report += f"Precision: {precision:.1%}\n"
        report += f"False Alarm Rate: {fp / (fp + tn):.1%}\n"

        return report

    def create_feature_importance_plot(self, predictor: DropoutPredictor,
                                      save_path: str = None):
        """
        Create and save feature importance visualization

        Args:
            predictor: Trained predictor with feature importances
            save_path: Path to save the plot
        """
        if not hasattr(predictor.model, 'feature_importances_'):
            logger.warning("Model does not have feature importances")
            return

        # Get feature importance
        feature_names = predictor.feature_engineer.get_feature_names()
        importances = predictor.model.feature_importances_

        # Create DataFrame for plotting
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=True).tail(15)

        # Create plot
        plt.figure(figsize=(10, 8))
        plt.barh(importance_df['feature'], importance_df['importance'])
        plt.xlabel('Feature Importance')
        plt.title('Top 15 Most Important Features for Dropout Prediction')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            logger.info(f"Feature importance plot saved to {save_path}")
        else:
            plt.show()

    def save_training_results(self, output_dir: str = 'data/training_results'):
        """
        Save all training results and models

        Args:
            output_dir: Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)

        # Save best model
        if self.best_model:
            model_name = self.best_model.save_model('best_model')
            logger.info(f"Best model saved as {model_name}")

        # Save training results summary
        import json
        results_summary = {}
        for model_type, result in self.training_results.items():
            results_summary[model_type] = result['metrics']

        with open(os.path.join(output_dir, 'training_results.json'), 'w') as f:
            json.dump(results_summary, f, indent=2)

        logger.info(f"Training results saved to {output_dir}")

    def validate_fairness(self, predictor: DropoutPredictor,
                         X: np.ndarray, y: np.ndarray,
                         sensitive_features: Dict[str, np.ndarray]) -> Dict:
        """
        Validate model fairness across sensitive groups

        Args:
            predictor: Trained predictor
            X: Feature matrix
            y: True labels
            sensitive_features: Dictionary of sensitive feature arrays

        Returns:
            Fairness metrics dictionary
        """
        fairness_metrics = {}
        X_scaled = predictor.scaler.transform(X)
        y_pred = predictor.model.predict(X_scaled)

        for feature_name, feature_values in sensitive_features.items():
            unique_values = np.unique(feature_values)
            group_metrics = {}

            for value in unique_values:
                mask = feature_values == value
                if mask.sum() > 0:
                    group_y = y[mask]
                    group_pred = y_pred[mask]

                    # Calculate metrics for this group
                    tp = ((group_pred == 1) & (group_y == 1)).sum()
                    fn = ((group_pred == 0) & (group_y == 1)).sum()
                    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

                    group_metrics[str(value)] = {
                        'recall': recall,
                        'size': mask.sum()
                    }

            fairness_metrics[feature_name] = group_metrics

        return fairness_metrics