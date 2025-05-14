import joblib
import os

# Load model and vectorizer once
MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_model.joblib")
model_bundle = joblib.load(MODEL_PATH)
vectorizer = model_bundle["vectorizer"]
model = model_bundle["model"]

def is_relevant(text):
    X = vectorizer.transform([text])
    return model.predict(X)[0] == 1
