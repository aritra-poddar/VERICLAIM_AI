import pandas as pd
import joblib
import os

# Load model once
model_path = os.path.join(os.path.dirname(__file__), "fraud/isolation_forest.joblib")
model = joblib.load(model_path)

if isinstance(model, dict):
    actual_model = model['model']
else:
    actual_model = model

# Define feature order
FEATURE_ORDER = ['amount', 'days_since_last_claim', 'num_previous_claims', 'patient_age']

# Prediction function
def predict_claim(input_dict):
    claim_df = pd.DataFrame([input_dict])
    claim_df = claim_df[FEATURE_ORDER]  # reorder safely
    prediction = actual_model.predict(claim_df)
    return int(prediction[0])
