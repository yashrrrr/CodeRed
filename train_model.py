"""
Train ML models for dropout prediction
Creates actual trained models instead of using simulated predictions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, recall_score, precision_score, accuracy_score
import joblib
import os

def train_models():
    """Train and save ML models for dropout prediction"""

    print("Loading training data...")
    # Load the generated synthetic data
    df = pd.read_csv('data/sample_learners.csv')

    # Define feature columns (all numeric columns except id, name, email, and target)
    feature_cols = [col for col in df.columns if col not in [
        'id', 'name', 'email', 'program', 'enrollment_date',
        'last_activity_date', 'dropout_risk'
    ]]

    X = df[feature_cols].fillna(0)
    y = (df['dropout_risk'] > 0.5).astype(int)  # Convert risk score to binary

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print(f"Features: {len(feature_cols)}")

    # Train Random Forest (optimized for recall)
    print("\nTraining Random Forest model...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        class_weight='balanced',  # Important for imbalanced data
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    # Evaluate Random Forest
    rf_pred = rf_model.predict(X_test)
    rf_recall = recall_score(y_test, rf_pred)
    rf_precision = precision_score(y_test, rf_pred)
    rf_accuracy = accuracy_score(y_test, rf_pred)

    print(f"Random Forest - Accuracy: {rf_accuracy:.2%}, Recall: {rf_recall:.2%}, Precision: {rf_precision:.2%}")

    # Train Gradient Boosting (alternative model)
    print("\nTraining Gradient Boosting model...")
    gb_model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        subsample=0.8,
        random_state=42
    )
    gb_model.fit(X_train, y_train)

    # Evaluate Gradient Boosting
    gb_pred = gb_model.predict(X_test)
    gb_recall = recall_score(y_test, gb_pred)
    gb_precision = precision_score(y_test, gb_pred)
    gb_accuracy = accuracy_score(y_test, gb_pred)

    print(f"Gradient Boosting - Accuracy: {gb_accuracy:.2%}, Recall: {gb_recall:.2%}, Precision: {gb_precision:.2%}")

    # Save models
    os.makedirs('models', exist_ok=True)

    joblib.dump(rf_model, 'models/random_forest_model.pkl')
    joblib.dump(gb_model, 'models/gradient_boosting_model.pkl')
    joblib.dump(feature_cols, 'models/feature_columns.pkl')

    print(f"\nModels saved to models/ directory")

    # Feature importance
    print("\nTop 10 Most Important Features (Random Forest):")
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)

    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")

    return {
        'rf_metrics': {
            'accuracy': rf_accuracy,
            'recall': rf_recall,
            'precision': rf_precision
        },
        'gb_metrics': {
            'accuracy': gb_accuracy,
            'recall': gb_recall,
            'precision': gb_precision
        },
        'feature_importance': feature_importance.to_dict('records')
    }

if __name__ == "__main__":
    results = train_models()
    print("\n✓ Model training complete!")
    print(f"\nBest model for recall: {'Random Forest' if results['rf_metrics']['recall'] > results['gb_metrics']['recall'] else 'Gradient Boosting'}")