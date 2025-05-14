import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pandas as pd

MODEL_PATH = "ml_model.joblib"

def train_model(csv_path):
    """
    Train and save a relevance classification model from a labeled CSV file.
    """
    df = pd.read_csv(csv_path)
    X = df['text']
    y = df['label']

    model = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', LogisticRegression())
    ])

    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model trained and saved to {MODEL_PATH}")

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model file not found. Please train the model first.")
    return joblib.load(MODEL_PATH)

def is_relevant(text):
    """
    Return True if the given text is classified as relevant.
    """
    model = load_model()
    prediction = model.predict([text])[0]
    return prediction == "relevant"

# For testing or training manually

