<<<<<<< HEAD
"""Quick end-to-end test of the phishing detection pipeline."""
import re
import joblib
from pathlib import Path

models_dir = Path("models")
model = joblib.load(models_dir / "best_model.joblib")
tfidf = joblib.load(models_dir / "tfidf_vectorizer.joblib")
le = joblib.load(models_dir / "label_encoder.joblib")
name = joblib.load(models_dir / "best_model_name.joblib")

def clean_text(text):
    text = text.lower()
    text = re.sub(r"https?://\S+", " URL ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

test_cases = [
    ("URGENT: Your account has been compromised! Click here NOW to verify your identity", "phishing"),
    ("Hey are we still meeting for coffee tomorrow at 3pm", "legitimate"),
    ("You have won a FREE prize! Claim now at http://scam-link.com", "phishing"),
    ("Hi team, please find the meeting notes attached from today", "legitimate"),
    ("Your bank account will be suspended unless you verify within 24 hours", "phishing"),
]

print(f"Model: {name}")
print("=" * 70)
passed = 0
for text, expected in test_cases:
    cleaned = clean_text(text)
    pred = le.inverse_transform(model.predict(tfidf.transform([cleaned])))[0]
    status = "PASS" if pred == expected else "FAIL"
    if pred == expected:
        passed += 1
    print(f"[{status}] Expected={expected:<12} Got={pred:<12} | {text[:50]}...")

print("=" * 70)
print(f"Result: {passed}/{len(test_cases)} tests passed")
=======
"""Quick end-to-end test of the phishing detection pipeline."""
import re
import joblib
from pathlib import Path

models_dir = Path("models")
model = joblib.load(models_dir / "best_model.joblib")
tfidf = joblib.load(models_dir / "tfidf_vectorizer.joblib")
le = joblib.load(models_dir / "label_encoder.joblib")
name = joblib.load(models_dir / "best_model_name.joblib")

def clean_text(text):
    text = text.lower()
    text = re.sub(r"https?://\S+", " URL ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

test_cases = [
    ("URGENT: Your account has been compromised! Click here NOW to verify your identity", "phishing"),
    ("Hey are we still meeting for coffee tomorrow at 3pm", "legitimate"),
    ("You have won a FREE prize! Claim now at http://scam-link.com", "phishing"),
    ("Hi team, please find the meeting notes attached from today", "legitimate"),
    ("Your bank account will be suspended unless you verify within 24 hours", "phishing"),
]

print(f"Model: {name}")
print("=" * 70)
passed = 0
for text, expected in test_cases:
    cleaned = clean_text(text)
    pred = le.inverse_transform(model.predict(tfidf.transform([cleaned])))[0]
    status = "PASS" if pred == expected else "FAIL"
    if pred == expected:
        passed += 1
    print(f"[{status}] Expected={expected:<12} Got={pred:<12} | {text[:50]}...")

print("=" * 70)
print(f"Result: {passed}/{len(test_cases)} tests passed")
>>>>>>> 13d69a23734bbe47eb1db6598bc86b5975a7a2ec
