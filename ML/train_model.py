"""
Machine Learning Module: Admission Eligibility Prediction
Algorithm: Logistic Regression
Institution: AI-Enhanced Admission Management System
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
import joblib

def generate_dataset(n_samples: int = 2500, random_state: int = 42) -> pd.DataFrame:
    """
    Generates a realistic student admission dataset based on:
    - academic_gpa: Percentage scale (50.0 - 100.0)
    - entrance_score: Score out of 100 (30.0 - 100.0)
    - attendance_pct: High school / pre-degree attendance percentage (55.0 - 100.0)
    - prev_academic_score: 10th / 12th board score percentage (45.0 - 100.0)
    - category: General, OBC, SC_ST, EWS
    - extracurricular: None, School_Level, State_Level, National_Level
    """
    np.random.seed(random_state)
    
    # Numerical distributions
    academic_gpa = np.clip(np.random.normal(loc=76.0, scale=12.0, size=n_samples), 50.0, 100.0)
    entrance_score = np.clip(np.random.normal(loc=72.0, scale=14.0, size=n_samples), 30.0, 100.0)
    attendance_pct = np.clip(np.random.normal(loc=82.0, scale=10.0, size=n_samples), 55.0, 100.0)
    prev_academic_score = np.clip(np.random.normal(loc=74.0, scale=11.0, size=n_samples), 45.0, 100.0)
    
    # Categoricals
    categories = ['General', 'OBC', 'SC_ST', 'EWS']
    category_probs = [0.40, 0.30, 0.18, 0.12]
    category = np.random.choice(categories, size=n_samples, p=category_probs)
    
    extracurriculars = ['None', 'School_Level', 'State_Level', 'National_Level']
    ec_probs = [0.45, 0.30, 0.18, 0.07]
    extracurricular = np.random.choice(extracurriculars, size=n_samples, p=ec_probs)
    
    # Category cutoff concession adjustments (affirmative action / institutional quota criteria)
    category_weight = {
        'General': 0.0,
        'OBC': 0.35,
        'SC_ST': 0.85,
        'EWS': 0.50
    }
    
    ec_bonus = {
        'None': 0.0,
        'School_Level': 0.25,
        'State_Level': 0.65,
        'National_Level': 1.20
    }
    
    # Composite score formulation reflecting real academic admission policy
    # Academic weight: 35%, Entrance: 40%, Prev score: 15%, Attendance: 10%
    base_score = (
        0.35 * ((academic_gpa - 70.0) / 10.0) +
        0.40 * ((entrance_score - 68.0) / 12.0) +
        0.15 * ((prev_academic_score - 70.0) / 10.0) +
        0.10 * ((attendance_pct - 75.0) / 10.0)
    )
    
    cat_adj = np.array([category_weight[c] for c in category])
    ec_adj = np.array([ec_bonus[e] for e in extracurricular])
    
    # Noise to reflect human panel subjectivity
    noise = np.random.normal(0, 0.35, size=n_samples)
    
    latent_score = base_score + cat_adj + ec_adj + noise
    
    # Sigmoid function for probability
    prob = 1.0 / (1.0 + np.exp(-latent_score))
    admission_status = (prob >= 0.50).astype(int)
    
    df = pd.DataFrame({
        'academic_gpa': np.round(academic_gpa, 2),
        'entrance_score': np.round(entrance_score, 2),
        'attendance_pct': np.round(attendance_pct, 2),
        'prev_academic_score': np.round(prev_academic_score, 2),
        'category': category,
        'extracurricular': extracurricular,
        'admission_status': admission_status
    })
    
    return df

def train_and_evaluate():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, 'admission_dataset.csv')
    model_path = os.path.join(script_dir, 'admission_logistic_model.joblib')
    metrics_path = os.path.join(script_dir, 'model_evaluation.json')
    
    print("================================================================")
    print("1. Generating Educational Admission Dataset...")
    df = generate_dataset(n_samples=2500, random_state=42)
    df.to_csv(dataset_path, index=False)
    print(f"   Saved {len(df)} records to {dataset_path}")
    print(f"   Eligible count: {df['admission_status'].sum()} ({df['admission_status'].mean()*100:.2f}%)")
    print(f"   Non-eligible count: {len(df) - df['admission_status'].sum()}")
    
    # Features and Target
    X = df[['academic_gpa', 'entrance_score', 'attendance_pct', 'prev_academic_score', 'category', 'extracurricular']]
    y = df['admission_status']
    
    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    numeric_features = ['academic_gpa', 'entrance_score', 'attendance_pct', 'prev_academic_score']
    categorical_features = ['category', 'extracurricular']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features)
        ]
    )
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(
            C=1.0,
            solver='lbfgs',
            max_iter=1000,
            random_state=42
        ))
    ])
    
    print("\n2. Training Logistic Regression Model with Cross-Validation...")
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='accuracy')
    print(f"   5-Fold Cross-Validation Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    pipeline.fit(X_train, y_train)
    
    print("\n3. Evaluating Model on Held-out Test Set...")
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print("----------------------------------------------------------------")
    print(f"   Accuracy : {acc:.4f} ({acc*100:.2f}%)")
    print(f"   Precision: {prec:.4f}")
    print(f"   Recall   : {rec:.4f}")
    print(f"   F1-Score : {f1:.4f}")
    print(f"   ROC-AUC  : {roc_auc:.4f}")
    print(f"   Confusion Matrix: {cm}")
    print("----------------------------------------------------------------")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Not Eligible', 'Eligible']))
    
    # Save Pipeline and Metrics
    print("\n4. Saving Trained Pipeline and Metrics...")
    joblib.dump(pipeline, model_path)
    print(f"   Model saved to {model_path}")
    
    # Also copy to Backend directory for immediate availability
    backend_model_dir = os.path.join(os.path.dirname(script_dir), 'Backend')
    joblib.dump(pipeline, os.path.join(backend_model_dir, 'admission_logistic_model.joblib'))
    print(f"   Model also synchronized to {backend_model_dir}/admission_logistic_model.joblib")
    
    eval_results = {
        'algorithm': 'Logistic Regression',
        'hyperparameters': {
            'C': 1.0,
            'penalty': 'l2',
            'solver': 'lbfgs',
            'max_iter': 1000
        },
        'dataset_size': len(df),
        'features': list(X.columns),
        'metrics': {
            'accuracy': round(float(acc), 4),
            'precision': round(float(prec), 4),
            'recall': round(float(rec), 4),
            'f1_score': round(float(f1), 4),
            'roc_auc': round(float(roc_auc), 4),
            'cv_mean_accuracy': round(float(cv_scores.mean()), 4),
            'cv_std_accuracy': round(float(cv_scores.std()), 4),
            'confusion_matrix': cm
        }
    }
    
    with open(metrics_path, 'w') as f:
        json.dump(eval_results, f, indent=4)
    print(f"   Evaluation metrics saved to {metrics_path}")
    print("================================================================")
    print("ML Model training and verification completed successfully!")

if __name__ == '__main__':
    train_and_evaluate()
