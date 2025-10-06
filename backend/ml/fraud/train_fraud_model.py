import pandas as pd
import os
from fraud_detection import FraudDetector  # make sure this file contains your updated FraudDetector class

# 1. Path to your CSV file
csv_path = r"C:\Users\arpit\synthetic_insurance_claims_large.csv"  # use raw string to avoid escape issues

# 2. Check if file exists
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found at: {csv_path}")

# 3. Load dataset
df = pd.read_csv(csv_path)

# 4. Define features for training
feature_cols = ['amount', 'days_since_last_claim', 'num_previous_claims', 'patient_age']

# Ensure all required columns exist
missing_cols = [col for col in feature_cols if col not in df.columns]
if missing_cols:
    raise ValueError(f"The following required columns are missing in the dataset: {missing_cols}")

# 5. Initialize the detector
detector = FraudDetector()

# 6. Train the model
detector.fit(df, feature_cols)

print("✅ Model trained and saved successfully at:", os.path.join(os.path.dirname(__file__), "isolation_forest.joblib"))
