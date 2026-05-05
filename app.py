from flask import Flask, request, render_template_string
import joblib
import re
import os
import math

app = Flask(__name__)

# ── Load model and vectoriser once at startup ──────────────────────────────
BASE       = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, "models", "best_model.joblib")
VEC_PATH   = os.path.join(BASE, "models", "bow_vectorizer.joblib")

model      = joblib.load(MODEL_PATH)
vectoriser = joblib.load(VEC_PATH)

# ── Text cleaning (same as build_dataset.py) ───────────────────────────────
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+", " URL ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ── HTML template ──────────────────────────────────────────────────────────
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Phishing Email Detector</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: Arial, sans-serif;
      background: #f0f4f8;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      min-height: 100vh;
      padding: 40px 16px;
    }

    .card {
      background: white;
      border-radius: 12px;
      box-shadow: 0 2px 16px rgba(0,0,0,0.10);
      padding: 36px 40px;
      width: 100%;
      max-width: 640px;
    }

    h1 {
      font-size: 22px;
      color: #1a2e4a;
      margin-bottom: 20px;
    }

    label {
      font-size: 14px;
      font-weight: bold;
      color: #374151;
      display: block;
      margin-bottom: 8px;
    }

    textarea {
      width: 100%;
      height: 180px;
      border: 1.5px solid #d1d5db;
      border-radius: 8px;
      padding: 12px;
      font-size: 14px;
      font-family: Arial, sans-serif;
      resize: vertical;
      outline: none;
    }

    textarea:focus { border-color: #2563eb; }

    /* Error message */
    .error-msg {
      margin-top: 8px;
      font-size: 13px;
      color: #dc2626;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    /* Analyse button */
    button {
      margin-top: 16px;
      width: 100%;
      padding: 12px;
      background: #1a2e4a;
      color: white;
      font-size: 15px;
      font-weight: bold;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.2s;
    }

    button:hover { background: #2563eb; }

    /* Result box */
    .result {
      margin-top: 24px;
      border-radius: 10px;
      padding: 20px 24px;
      text-align: center;
    }

    .result.phishing {
      background: #fef2f2;
      border: 2px solid #ef4444;
    }

    .result.legitimate {
      background: #f0fdf4;
      border: 2px solid #22c55e;
    }

    .result .verdict {
      font-size: 26px;
      font-weight: bold;
      margin-bottom: 6px;
    }

    .result.phishing .verdict  { color: #dc2626; }
    .result.legitimate .verdict { color: #16a34a; }

    .result .confidence {
      font-size: 15px;
      color: #374151;
    }

    .result .icon {
      font-size: 40px;
      margin-bottom: 8px;
    }

    /* Clear link */
    .clear-link {
      display: block;
      margin-top: 12px;
      text-align: center;
      font-size: 13px;
      color: #6b7280;
      text-decoration: none;
      transition: color 0.2s;
    }

    .clear-link:hover { color: #374151; }

  </style>
</head>
<body>
<div class="card">

  <h1>&#128272; Phishing Email Detector</h1>

  <form method="POST" action="/">
    <label for="email_text">Paste email content below:</label>

    <textarea
      id="email_text"
      name="email_text"
      placeholder="Paste the full email text here (subject + body)..."
    >{{ email_text }}</textarea>

    {% if error %}
    <p class="error-msg">&#9888; {{ error }}</p>
    {% endif %}

    <button type="submit">&#128269; Analyse Email</button>
  </form>

  {% if result %}
  <div class="result {{ result.label_class }}">
    <div class="icon">{{ result.icon | safe }}</div>
    <div class="verdict">{{ result.label }}</div>
    <div class="confidence">Confidence: <strong>{{ result.confidence }}%</strong></div>
  </div>
  <a href="/" class="clear-link">&#10006; Clear and analyse another email</a>
  {% endif %}

</div>
</body>
</html>
"""

# ── Routes ─────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def index():
    result     = None
    email_text = ""
    error      = None

    if request.method == "POST":
        email_text = request.form.get("email_text", "").strip()

        # UC-04 Alternative Flow: empty input validation
        if not email_text:
            error = "Please enter email text before submitting."

        else:
            # Step 6: apply NLP preprocessing pipeline
            cleaned = clean_text(email_text)

            # Step 7: transform using fitted TF-IDF vectoriser
            features = vectoriser.transform([cleaned])

            # Step 8: pass to classifier and retrieve prediction
            prediction = model.predict(features)[0]

            # Get confidence score
            try:
                # Models with predict_proba: LR, Naive Bayes, RF, Neural Network
                proba      = model.predict_proba(features)[0]
                confidence = round(max(proba) * 100, 1)
            except AttributeError:
                # SVM LinearSVC: use decision_function as proxy
                score      = model.decision_function(features)[0]
                confidence = round(min(99.9, 50 + abs(score) * 10), 1)

            # Step 9: determine label and display class
            if prediction == "phishing" or prediction == 1 or str(prediction) == "1":
                label_class = "phishing"
                label       = "PHISHING DETECTED"
                icon        = "&#10060;"   # red X
            else:
                label_class = "legitimate"
                label       = "LEGITIMATE EMAIL"
                icon        = "&#9989;"    # green tick

            result = {
                "label_class": label_class,
                "label":       label,
                "confidence":  confidence,
                "icon":        icon,
            }

    return render_template_string(
        HTML,
        result=result,
        email_text=email_text,
        error=error,
    )

# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("Phishing Detector — Flask Web Interface")
    print("Open your browser at: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)
