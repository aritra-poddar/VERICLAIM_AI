"""
FraudDetector: IsolationForest-based fraud detection for insurance claims.

Features used:
- amount
- days_since_last_claim
- num_previous_claims
- patient_age

Usage:
1. Train on a CSV dataset with these columns.
2. Save the model using .fit().
3. Load the model using .load() and predict new claims using .predict_anomaly().
"""

from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np
import joblib
import os
from typing import List, Dict, Any

# Path to save/load the model
MODEL_PATH = os.getenv(
    "FRAUD_MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "isolation_forest.joblib")
)

class FraudDetector:
    def __init__(self, random_state: int = 42, contamination: float = 0.02):
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self.fitted = False
        self.features: List[str] = []

    def fit(self, df: pd.DataFrame, feature_cols: List[str]):
        """
        Train the IsolationForest on the given DataFrame.
        Saves the model to MODEL_PATH.
        """
        X = df[feature_cols].values
        self.model.fit(X)
        self.fitted = True
        self.features = feature_cols
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump({"model": self.model, "features": self.features}, MODEL_PATH)
        print(f"Model trained and saved to {MODEL_PATH}")

    def load(self):
        """
        Load pre-trained model from disk.
        """
        if os.path.exists(MODEL_PATH):
            payload = joblib.load(MODEL_PATH)
            self.model = payload["model"]
            self.features = payload["features"]
            self.fitted = True
            print("Model loaded successfully.")
        else:
            raise FileNotFoundError(f"Fraud model not found at {MODEL_PATH}. Train first.")

    def predict_anomaly(self, claim_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict if a claim is anomalous (fraudulent).
        Returns dict with:
        - status: "✅ ELIGIBLE" or "⚠️ REQUIRES MANUAL REVIEW"
        - is_anomaly: boolean
        - score: IsolationForest anomaly score
        """
        if not self.fitted:
            raise RuntimeError("Model not fitted. Call fit() or load().")
        
        # Ensure numeric array in correct order
        try:
            X = np.array([float(claim_features[c]) for c in self.features]).reshape(1, -1)
        except KeyError as e:
            raise ValueError(f"Missing required feature: {e}")
        except ValueError:
            raise ValueError("All feature values must be numeric.")

        score = self.model.decision_function(X)[0]
        pred = self.model.predict(X)[0]  # -1 anomaly, 1 normal
        is_anomaly = (pred == -1)
        status = "⚠️ REQUIRES MANUAL REVIEW" if is_anomaly else "✅ ELIGIBLE"

        return {"status": status, "is_anomaly": bool(is_anomaly), "score": float(score)}

    @staticmethod
    def train_from_csv(csv_path: str, feature_cols: List[str] = None):
        """
        Convenience function to train a model directly from a CSV dataset.
        """
        df = pd.read_csv(csv_path)
        if feature_cols is None:
            feature_cols = ['amount', 'days_since_last_claim', 'num_previous_claims', 'patient_age']

        detector = FraudDetector()
        detector.fit(df, feature_cols)
        return detector

# Example usage:
# detector = FraudDetector.train_from_csv("synthetic_insurance_claims_large.csv")
# detector.load()
# result = detector.predict_anomaly({
#     "amount": 500,
#     "days_since_last_claim": 30,
#     "num_previous_claims": 0,
#     "patient_age": 35
# })
# print(result)
