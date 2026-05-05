<<<<<<< HEAD
"""
==============================================================================
    PHISHING DETECTION PROJECT - COMPLETE STEP-BY-STEP GUIDE
    CS6P05 - NLP and Machine Learning for Phishing Classification
==============================================================================

This guide explains every script in the project pipeline.
Run each script in order (Step 1 -> Step 5) from the project folder.

COMMAND TO RUN ANY SCRIPT:
    & env/Scripts/python.exe <script_name>.py

==============================================================================
PROJECT STRUCTURE
==============================================================================

phishing_project/
|-- data/                          # Raw datasets
|   |-- uci_sms/                   #   UCI SMS Spam Collection (text data)
|   |   |-- SMSSpamCollection      #   Tab-separated: label<TAB>message
|   |-- kaggle_phishing/           #   Kaggle dataset (numeric features)
|   |   |-- email_phishing_data.csv
|   |-- enron/                     #   Enron email corpus (optional)
|
|-- output/                        # All generated outputs
|   |-- emails_balanced.csv        #   Balanced dataset (Step 1)
|   |-- features.joblib            #   Feature matrices (Step 2)
|   |-- training_results.joblib    #   Training metrics (Step 3)
|   |-- evaluation_report.txt      #   Full evaluation report (Step 4)
|   |-- model_comparison.png       #   Bar chart comparing models (Step 4)
|   |-- confusion_matrix_*.png     #   Confusion matrices (Step 4)
|
|-- models/                        # All saved models & vectorisers
|   |-- tfidf_vectorizer.joblib    #   TF-IDF vectoriser (Step 2)
|   |-- bow_vectorizer.joblib      #   Bag of Words vectoriser (Step 2)
|   |-- svd_embedder.joblib        #   SVD embedder (Step 2)
|   |-- label_encoder.joblib       #   Label encoder (Step 2)
|   |-- model_*.joblib             #   Individual trained models (Step 3)
|   |-- best_model.joblib          #   Best performing model (Step 3)
|
|-- build_dataset.py               # Step 1: Data Preprocessing
|-- feature_engineering.py         # Step 2: Feature Engineering
|-- train_model.py                 # Step 3: Model Training
|-- evaluate_model.py              # Step 4: Model Evaluation
|-- app.py                         # Step 5a: Flask
|-- dashboard.py                   
|-- test_pipeline.py               # End-to-end test
|-- requirements.txt               # Python dependencies


==============================================================================
STEP 1: DATA PREPROCESSING  (build_dataset.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe build_dataset.py

WHAT IT DOES:
    This script collects raw data from two different sources, cleans it,
    and creates a single balanced dataset ready for machine learning.

HOW IT WORKS (line by line):

1. IMPORTS (lines 1-4):
    - re:       Python's regular expression library for text pattern matching
    - random:   For reproducible random sampling (seed=42)
    - pathlib:  Modern file path handling
    - pandas:   Data manipulation library (DataFrames = tables of data)

2. clean_text() FUNCTION (lines 6-20):
    PURPOSE: Normalise raw text so the AI model sees consistent input.

    Steps performed:
    a) text.lower()               -> Convert to lowercase
                                     "URGENT Account" -> "urgent account"

    b) re.sub(r"https?://\\S+",   -> Replace all URLs with the word "URL"
       " URL ", text)                "click http://evil.com" -> "click URL"
                                     WHY: The actual URL doesn't matter,
                                     but the PRESENCE of a URL is a signal.

    c) re.sub(r"[^a-z0-9\\s]",    -> Remove all special characters
       " ", text)                    "Hello!!! $$$" -> "Hello    "
                                     WHY: Punctuation adds noise, not signal.

    d) re.sub(r"\\s+"," ",text)   -> Collapse multiple spaces into one
       .strip()                      "hello    world  " -> "hello world"

3. load_uni_sms() FUNCTION (lines 21-51):
    PURPOSE: Load the UCI SMS Spam Collection dataset.

    This dataset has one message per line in format: label<TAB>message
    Example line: "spam\tFree entry to win..."

    Steps:
    a) Opens the file and reads line by line
    b) Splits each line by TAB character into [label, text]
    c) Converts labels: "spam" -> "phishing", "ham" -> "legitimate"
    d) Cleans each text using clean_text()
    e) Returns a pandas DataFrame with columns: text, label, source

4. load_kaggle_csv() FUNCTION (lines 52-120):
    PURPOSE: Load the Kaggle phishing dataset.

    IMPORTANT: The Kaggle CSV has numeric features (num_words, num_links,
    etc.) but NO raw text. So this function detects that and saves the
    numeric features separately.

    Steps:
    a) Reads CSV with pandas
    b) Searches for a label column (label, class, phishing, etc.)
    c) Searches for a text column (email, text, message, etc.)
    d) If NO text column found -> saves as numeric feature dataset
    e) If text column found -> cleans text and returns DataFrame

5. main() FUNCTION (lines 121-end):
    PURPOSE: Orchestrate the full data preparation pipeline.

    Steps:
    a) Load UCI SMS dataset (5,574 messages: 4,827 legitimate + 747 spam)
    b) Load Kaggle dataset (saved separately as numeric features)
    c) Combine text datasets
    d) BALANCE the dataset:
       - Count phishing vs legitimate
       - Take equal samples from each class (747 each)
       - WHY: If 90% of data is legitimate, the model would just predict
         "legitimate" always and get 90% accuracy. Balancing forces
         the model to actually learn the difference.
    e) Save to output/emails_balanced.csv
    f) Print statistics

OUTPUT: output/emails_balanced.csv (1,494 emails: 747 phishing + 747 legitimate)


==============================================================================
STEP 2: FEATURE ENGINEERING  (feature_engineering.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe feature_engineering.py

WHAT IT DOES:
    Converts raw text into numbers that ML models can understand.
    Machines cannot read text directly — they need numerical vectors.

HOW IT WORKS:

1. LABEL ENCODING:
    Converts text labels to numbers:
        "legitimate" -> 0
        "phishing"   -> 1
    The encoder is saved so we can convert back later.

2. TRAIN/TEST SPLIT (70/30):
    Splits data into:
        - Training set (70%): Used to TRAIN the models
        - Test set (30%):     Used to EVALUATE model performance
    WHY: If you test on the same data you trained on, the model just
    memorises answers. The test set simulates unseen emails.
    stratify=y ensures both sets have the same ratio of phishing/legitimate.

3. TF-IDF (Term Frequency - Inverse Document Frequency):
    WHAT: Scores how important each word is to a document.

    HOW:
    - TF (Term Frequency): How often a word appears in ONE email
      "urgent" appears 3 times in a 20-word email -> TF = 3/20 = 0.15
    - IDF (Inverse Document Frequency): How rare a word is across ALL emails
      "the" appears in 90% of emails -> low IDF (common, not useful)
      "suspended" appears in 2% of emails -> high IDF (rare, informative)
    - TF-IDF = TF x IDF

    PARAMETERS:
    - max_features=5000:  Keep only the 5000 most important words
    - ngram_range=(1,2):  Look at single words AND two-word phrases
                          WHY: "account suspended" is more suspicious than
                          "account" or "suspended" alone
    - min_df=2:           Ignore words that appear in fewer than 2 emails
    - max_df=0.95:        Ignore words that appear in >95% of emails
    - sublinear_tf=True:  Uses log(1+TF) instead of raw TF to reduce the
                          impact of very frequent words

4. BAG OF WORDS (BoW):
    WHAT: Simply counts how many times each word appears.

    DIFFERENCE FROM TF-IDF:
    - BoW: "urgent" appears 3 times -> value is 3
    - TF-IDF: "urgent" appears 3 times -> value depends on how rare
      "urgent" is across all emails

    BoW is simpler but less nuanced. We include both so you can compare.

5. DENSE EMBEDDINGS (TruncatedSVD):
    WHAT: Compresses the TF-IDF matrix into a smaller, dense representation.

    WHY: TF-IDF creates 5000 features, most of which are zero (sparse).
    SVD reduces this to 100 dimensions that capture the most important
    patterns. This is similar to how word embeddings (Word2Vec, GloVe)
    create dense representations.

    Explained variance tells you how much information is preserved.
    ~35% is typical for text data with this number of components.

OUTPUT FILES:
    - models/tfidf_vectorizer.joblib  (the trained TF-IDF converter)
    - models/bow_vectorizer.joblib    (the trained BoW converter)
    - models/svd_embedder.joblib      (the SVD compressor)
    - models/label_encoder.joblib     (label text <-> number converter)
    - output/features.joblib          (all feature matrices + labels)


==============================================================================
STEP 3: MODEL TRAINING  (train_model.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe train_model.py

WHAT IT DOES:
    Trains 5 different machine learning models on the TF-IDF features
    and selects the best one.

THE 5 MODELS EXPLAINED:

1. NAIVE BAYES (MultinomialNB):
    HOW: Uses probability theory (Bayes' Theorem).
    Calculates: P(phishing | words in email)
    "If the email contains 'urgent', 'suspended', and 'verify',
     what is the probability it is phishing?"
    PROS: Very fast, works well with text data, good baseline
    CONS: Assumes words are independent (which they are not)

2. LOGISTIC REGRESSION:
    HOW: Draws a line (hyperplane) between phishing and legitimate emails
    in the feature space. Each word gets a weight:
        "urgent" -> high positive weight (points toward phishing)
        "meeting" -> high negative weight (points toward legitimate)
    PROS: Fast, interpretable, good for text classification
    CONS: Only learns linear boundaries

3. RANDOM FOREST:
    HOW: Builds 200 decision trees, each making its own prediction.
    Final answer = majority vote of all trees.
    Each tree asks questions like:
        "Does TF-IDF of 'verify' > 0.3? YES -> probably phishing"
    PROS: Handles non-linear patterns, hard to overfit
    CONS: Slower, less interpretable, can be large

4. SVM (Support Vector Machine - LinearSVC):
    HOW: Finds the hyperplane that creates the MAXIMUM margin between
    the two classes. Like Logistic Regression but optimises for the
    widest possible gap between phishing and legitimate.
    PROS: Excellent for high-dimensional text data (5000 features)
    CONS: Hard to interpret, no probability output by default

5. NEURAL NETWORK (MLPClassifier - Multi-Layer Perceptron):
    HOW: Two hidden layers (256 neurons -> 128 neurons) that learn
    complex, non-linear patterns in the data.
    Architecture: Input(5000) -> Dense(256) -> ReLU -> Dense(128) -> ReLU -> Output(2)
    Uses early_stopping=True to prevent overfitting.
    PROS: Can learn very complex patterns
    CONS: Slower to train, needs more data to shine

BEST MODEL SELECTION:
    The model with the highest accuracy on the test set is automatically
    saved as "best_model.joblib". This is the model used by the API
    and dashboard.

OUTPUT FILES:
    - models/model_naive_bayes.joblib
    - models/model_logistic_regression.joblib
    - models/model_random_forest.joblib
    - models/model_svm_linearsvc.joblib
    - models/model_neural_network_mlp.joblib
    - models/best_model.joblib           (copy of the winning model)
    - models/best_model_name.joblib      (name of the winning model)
    - output/training_results.joblib     (accuracy scores for all models)


==============================================================================
STEP 4: MODEL EVALUATION  (evaluate_model.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe evaluate_model.py

WHAT IT DOES:
    Evaluates all trained models using 4 key metrics and generates
    visual reports (charts and confusion matrices).

THE 4 METRICS EXPLAINED:

1. ACCURACY: What percentage of predictions were correct?
    Formula: (Correct predictions) / (Total predictions)
    Example: 289 correct out of 299 = 96.66%
    LIMITATION: Can be misleading with unbalanced data
    (which is why we balanced our dataset in Step 1)

2. PRECISION: Of all emails flagged as "phishing", how many really were?
    Formula: True Phishing / (True Phishing + False Alarms)
    HIGH precision = Few false alarms
    Example: 97% precision means only 3% of phishing alerts are wrong

3. RECALL: Of all actual phishing emails, how many did we catch?
    Formula: True Phishing / (True Phishing + Missed Phishing)
    HIGH recall = Few missed threats
    Example: 95% recall means we catch 95% of phishing emails

4. F1-SCORE: The harmonic mean of Precision and Recall.
    Formula: 2 * (Precision * Recall) / (Precision + Recall)
    WHY: Balances both metrics. A model with 100% precision but 1%
    recall (catches almost nothing) would have a low F1.

CONFUSION MATRIX:
    A 2x2 grid showing predictions vs reality:

                        Predicted Legitimate  |  Predicted Phishing
    Actually Legitimate |   True Negative      |   False Positive (false alarm)
    Actually Phishing   |   False Negative      |   True Positive (caught it!)

    Good model: High numbers on the diagonal (top-left + bottom-right)

OUTPUT FILES:
    - output/evaluation_report.txt          (detailed text report)
    - output/model_comparison.png           (bar chart of all models)
    - output/confusion_matrix_*.png         (one per model)


==============================================================================
STEP 5a: FastAPI BACKEND  (app.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe app.py

WHAT IT DOES:
    Starts a web server at http://127.0.0.1:5000 that provides a REST API
    for phishing detection. Other applications can send HTTP requests
    to classify emails programmatically.

ENDPOINTS:
    GET  /          -> Service info
    POST /predict   -> Classify text

    Example request (using curl or Postman):
        POST http://127.0.0.1:5000/predict
        Body: {"text": "URGENT: Click here to verify your account"}
        Response: {"label": "phishing", "confidence": 0.98, "model": "..."}

HOW IT WORKS:
    1. On startup, loads the best model + TF-IDF vectoriser
    2. When a POST /predict request arrives:
       a) Cleans the input text (same clean_text function)
       b) Transforms text to TF-IDF vector
       c) Model predicts: phishing or legitimate
       d) Returns JSON with label + confidence score


==============================================================================
STEP 5b: STREAMLIT DASHBOARD  (dashboard.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe -m streamlit run dashboard.py

WHAT IT DOES:
    Launches a visual web dashboard in your browser where you can
    paste any email or SMS text and get an instant verdict.

FEATURES:
    - Text input area to paste suspicious messages
    - "Analyse" button to classify
    - Red alert for phishing, green checkmark for legitimate
    - Confidence percentage
    - Model performance table showing all 5 models
    - Comparison chart and confusion matrix visualisations

HOW TO USE:
    1. Run the command above
    2. Browser opens automatically at http://localhost:8501
    3. Paste an email or SMS in the text area
    4. Click "Analyse"
    5. See the verdict


==============================================================================
FULL PIPELINE - RUN ALL STEPS
==============================================================================

    # Step 1: Prepare dataset
    & env/Scripts/python.exe build_dataset.py

    # Step 2: Extract features
    & env/Scripts/python.exe feature_engineering.py

    # Step 3: Train models
    & env/Scripts/python.exe train_model.py

    # Step 4: Evaluate models
    & env/Scripts/python.exe evaluate_model.py

    # Step 5: Launch dashboard
    & env/Scripts/python.exe -m streamlit run dashboard.py

    # (Optional) Run tests
    & env/Scripts/python.exe test_pipeline.py


==============================================================================
RESULTS ACHIEVED
==============================================================================

    Best Model:       Logistic Regression
    Accuracy:         96.66%
    Precision:        96.69%
    Recall:           96.66%
    F1-Score:         96.65%
    Dataset Size:     1,494 balanced emails (747 phishing + 747 legitimate)
    Features:         4,987 TF-IDF features (unigrams + bigrams)

==============================================================================
"""
=======
"""
==============================================================================
    PHISHING DETECTION PROJECT - COMPLETE STEP-BY-STEP GUIDE
    CS6P05 - NLP and Machine Learning for Phishing Classification
==============================================================================

This guide explains every script in the project pipeline.
Run each script in order (Step 1 -> Step 5) from the project folder.

COMMAND TO RUN ANY SCRIPT:
    & env/Scripts/python.exe <script_name>.py

==============================================================================
PROJECT STRUCTURE
==============================================================================

phishing_project/
|-- data/                          # Raw datasets
|   |-- uci_sms/                   #   UCI SMS Spam Collection (text data)
|   |   |-- SMSSpamCollection      #   Tab-separated: label<TAB>message
|   |-- kaggle_phishing/           #   Kaggle dataset (numeric features)
|   |   |-- email_phishing_data.csv
|   |-- enron/                     #   Enron email corpus (optional)
|
|-- output/                        # All generated outputs
|   |-- emails_balanced.csv        #   Balanced dataset (Step 1)
|   |-- features.joblib            #   Feature matrices (Step 2)
|   |-- training_results.joblib    #   Training metrics (Step 3)
|   |-- evaluation_report.txt      #   Full evaluation report (Step 4)
|   |-- model_comparison.png       #   Bar chart comparing models (Step 4)
|   |-- confusion_matrix_*.png     #   Confusion matrices (Step 4)
|
|-- models/                        # All saved models & vectorisers
|   |-- tfidf_vectorizer.joblib    #   TF-IDF vectoriser (Step 2)
|   |-- bow_vectorizer.joblib      #   Bag of Words vectoriser (Step 2)
|   |-- svd_embedder.joblib        #   SVD embedder (Step 2)
|   |-- label_encoder.joblib       #   Label encoder (Step 2)
|   |-- model_*.joblib             #   Individual trained models (Step 3)
|   |-- best_model.joblib          #   Best performing model (Step 3)
|
|-- build_dataset.py               # Step 1: Data Preprocessing
|-- feature_engineering.py         # Step 2: Feature Engineering
|-- train_model.py                 # Step 3: Model Training
|-- evaluate_model.py              # Step 4: Model Evaluation
|-- app.py                         # Step 5a: Flask
|-- dashboard.py                   
|-- test_pipeline.py               # End-to-end test
|-- requirements.txt               # Python dependencies


==============================================================================
STEP 1: DATA PREPROCESSING  (build_dataset.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe build_dataset.py

WHAT IT DOES:
    This script collects raw data from two different sources, cleans it,
    and creates a single balanced dataset ready for machine learning.

HOW IT WORKS (line by line):

1. IMPORTS (lines 1-4):
    - re:       Python's regular expression library for text pattern matching
    - random:   For reproducible random sampling (seed=42)
    - pathlib:  Modern file path handling
    - pandas:   Data manipulation library (DataFrames = tables of data)

2. clean_text() FUNCTION (lines 6-20):
    PURPOSE: Normalise raw text so the AI model sees consistent input.

    Steps performed:
    a) text.lower()               -> Convert to lowercase
                                     "URGENT Account" -> "urgent account"

    b) re.sub(r"https?://\\S+",   -> Replace all URLs with the word "URL"
       " URL ", text)                "click http://evil.com" -> "click URL"
                                     WHY: The actual URL doesn't matter,
                                     but the PRESENCE of a URL is a signal.

    c) re.sub(r"[^a-z0-9\\s]",    -> Remove all special characters
       " ", text)                    "Hello!!! $$$" -> "Hello    "
                                     WHY: Punctuation adds noise, not signal.

    d) re.sub(r"\\s+"," ",text)   -> Collapse multiple spaces into one
       .strip()                      "hello    world  " -> "hello world"

3. load_uni_sms() FUNCTION (lines 21-51):
    PURPOSE: Load the UCI SMS Spam Collection dataset.

    This dataset has one message per line in format: label<TAB>message
    Example line: "spam\tFree entry to win..."

    Steps:
    a) Opens the file and reads line by line
    b) Splits each line by TAB character into [label, text]
    c) Converts labels: "spam" -> "phishing", "ham" -> "legitimate"
    d) Cleans each text using clean_text()
    e) Returns a pandas DataFrame with columns: text, label, source

4. load_kaggle_csv() FUNCTION (lines 52-120):
    PURPOSE: Load the Kaggle phishing dataset.

    IMPORTANT: The Kaggle CSV has numeric features (num_words, num_links,
    etc.) but NO raw text. So this function detects that and saves the
    numeric features separately.

    Steps:
    a) Reads CSV with pandas
    b) Searches for a label column (label, class, phishing, etc.)
    c) Searches for a text column (email, text, message, etc.)
    d) If NO text column found -> saves as numeric feature dataset
    e) If text column found -> cleans text and returns DataFrame

5. main() FUNCTION (lines 121-end):
    PURPOSE: Orchestrate the full data preparation pipeline.

    Steps:
    a) Load UCI SMS dataset (5,574 messages: 4,827 legitimate + 747 spam)
    b) Load Kaggle dataset (saved separately as numeric features)
    c) Combine text datasets
    d) BALANCE the dataset:
       - Count phishing vs legitimate
       - Take equal samples from each class (747 each)
       - WHY: If 90% of data is legitimate, the model would just predict
         "legitimate" always and get 90% accuracy. Balancing forces
         the model to actually learn the difference.
    e) Save to output/emails_balanced.csv
    f) Print statistics

OUTPUT: output/emails_balanced.csv (1,494 emails: 747 phishing + 747 legitimate)


==============================================================================
STEP 2: FEATURE ENGINEERING  (feature_engineering.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe feature_engineering.py

WHAT IT DOES:
    Converts raw text into numbers that ML models can understand.
    Machines cannot read text directly — they need numerical vectors.

HOW IT WORKS:

1. LABEL ENCODING:
    Converts text labels to numbers:
        "legitimate" -> 0
        "phishing"   -> 1
    The encoder is saved so we can convert back later.

2. TRAIN/TEST SPLIT (70/30):
    Splits data into:
        - Training set (70%): Used to TRAIN the models
        - Test set (30%):     Used to EVALUATE model performance
    WHY: If you test on the same data you trained on, the model just
    memorises answers. The test set simulates unseen emails.
    stratify=y ensures both sets have the same ratio of phishing/legitimate.

3. TF-IDF (Term Frequency - Inverse Document Frequency):
    WHAT: Scores how important each word is to a document.

    HOW:
    - TF (Term Frequency): How often a word appears in ONE email
      "urgent" appears 3 times in a 20-word email -> TF = 3/20 = 0.15
    - IDF (Inverse Document Frequency): How rare a word is across ALL emails
      "the" appears in 90% of emails -> low IDF (common, not useful)
      "suspended" appears in 2% of emails -> high IDF (rare, informative)
    - TF-IDF = TF x IDF

    PARAMETERS:
    - max_features=5000:  Keep only the 5000 most important words
    - ngram_range=(1,2):  Look at single words AND two-word phrases
                          WHY: "account suspended" is more suspicious than
                          "account" or "suspended" alone
    - min_df=2:           Ignore words that appear in fewer than 2 emails
    - max_df=0.95:        Ignore words that appear in >95% of emails
    - sublinear_tf=True:  Uses log(1+TF) instead of raw TF to reduce the
                          impact of very frequent words

4. BAG OF WORDS (BoW):
    WHAT: Simply counts how many times each word appears.

    DIFFERENCE FROM TF-IDF:
    - BoW: "urgent" appears 3 times -> value is 3
    - TF-IDF: "urgent" appears 3 times -> value depends on how rare
      "urgent" is across all emails

    BoW is simpler but less nuanced. We include both so you can compare.

5. DENSE EMBEDDINGS (TruncatedSVD):
    WHAT: Compresses the TF-IDF matrix into a smaller, dense representation.

    WHY: TF-IDF creates 5000 features, most of which are zero (sparse).
    SVD reduces this to 100 dimensions that capture the most important
    patterns. This is similar to how word embeddings (Word2Vec, GloVe)
    create dense representations.

    Explained variance tells you how much information is preserved.
    ~35% is typical for text data with this number of components.

OUTPUT FILES:
    - models/tfidf_vectorizer.joblib  (the trained TF-IDF converter)
    - models/bow_vectorizer.joblib    (the trained BoW converter)
    - models/svd_embedder.joblib      (the SVD compressor)
    - models/label_encoder.joblib     (label text <-> number converter)
    - output/features.joblib          (all feature matrices + labels)


==============================================================================
STEP 3: MODEL TRAINING  (train_model.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe train_model.py

WHAT IT DOES:
    Trains 5 different machine learning models on the TF-IDF features
    and selects the best one.

THE 5 MODELS EXPLAINED:

1. NAIVE BAYES (MultinomialNB):
    HOW: Uses probability theory (Bayes' Theorem).
    Calculates: P(phishing | words in email)
    "If the email contains 'urgent', 'suspended', and 'verify',
     what is the probability it is phishing?"
    PROS: Very fast, works well with text data, good baseline
    CONS: Assumes words are independent (which they are not)

2. LOGISTIC REGRESSION:
    HOW: Draws a line (hyperplane) between phishing and legitimate emails
    in the feature space. Each word gets a weight:
        "urgent" -> high positive weight (points toward phishing)
        "meeting" -> high negative weight (points toward legitimate)
    PROS: Fast, interpretable, good for text classification
    CONS: Only learns linear boundaries

3. RANDOM FOREST:
    HOW: Builds 200 decision trees, each making its own prediction.
    Final answer = majority vote of all trees.
    Each tree asks questions like:
        "Does TF-IDF of 'verify' > 0.3? YES -> probably phishing"
    PROS: Handles non-linear patterns, hard to overfit
    CONS: Slower, less interpretable, can be large

4. SVM (Support Vector Machine - LinearSVC):
    HOW: Finds the hyperplane that creates the MAXIMUM margin between
    the two classes. Like Logistic Regression but optimises for the
    widest possible gap between phishing and legitimate.
    PROS: Excellent for high-dimensional text data (5000 features)
    CONS: Hard to interpret, no probability output by default

5. NEURAL NETWORK (MLPClassifier - Multi-Layer Perceptron):
    HOW: Two hidden layers (256 neurons -> 128 neurons) that learn
    complex, non-linear patterns in the data.
    Architecture: Input(5000) -> Dense(256) -> ReLU -> Dense(128) -> ReLU -> Output(2)
    Uses early_stopping=True to prevent overfitting.
    PROS: Can learn very complex patterns
    CONS: Slower to train, needs more data to shine

BEST MODEL SELECTION:
    The model with the highest accuracy on the test set is automatically
    saved as "best_model.joblib". This is the model used by the API
    and dashboard.

OUTPUT FILES:
    - models/model_naive_bayes.joblib
    - models/model_logistic_regression.joblib
    - models/model_random_forest.joblib
    - models/model_svm_linearsvc.joblib
    - models/model_neural_network_mlp.joblib
    - models/best_model.joblib           (copy of the winning model)
    - models/best_model_name.joblib      (name of the winning model)
    - output/training_results.joblib     (accuracy scores for all models)


==============================================================================
STEP 4: MODEL EVALUATION  (evaluate_model.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe evaluate_model.py

WHAT IT DOES:
    Evaluates all trained models using 4 key metrics and generates
    visual reports (charts and confusion matrices).

THE 4 METRICS EXPLAINED:

1. ACCURACY: What percentage of predictions were correct?
    Formula: (Correct predictions) / (Total predictions)
    Example: 289 correct out of 299 = 96.66%
    LIMITATION: Can be misleading with unbalanced data
    (which is why we balanced our dataset in Step 1)

2. PRECISION: Of all emails flagged as "phishing", how many really were?
    Formula: True Phishing / (True Phishing + False Alarms)
    HIGH precision = Few false alarms
    Example: 97% precision means only 3% of phishing alerts are wrong

3. RECALL: Of all actual phishing emails, how many did we catch?
    Formula: True Phishing / (True Phishing + Missed Phishing)
    HIGH recall = Few missed threats
    Example: 95% recall means we catch 95% of phishing emails

4. F1-SCORE: The harmonic mean of Precision and Recall.
    Formula: 2 * (Precision * Recall) / (Precision + Recall)
    WHY: Balances both metrics. A model with 100% precision but 1%
    recall (catches almost nothing) would have a low F1.

CONFUSION MATRIX:
    A 2x2 grid showing predictions vs reality:

                        Predicted Legitimate  |  Predicted Phishing
    Actually Legitimate |   True Negative      |   False Positive (false alarm)
    Actually Phishing   |   False Negative      |   True Positive (caught it!)

    Good model: High numbers on the diagonal (top-left + bottom-right)

OUTPUT FILES:
    - output/evaluation_report.txt          (detailed text report)
    - output/model_comparison.png           (bar chart of all models)
    - output/confusion_matrix_*.png         (one per model)


==============================================================================
STEP 5a: FastAPI BACKEND  (app.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe app.py

WHAT IT DOES:
    Starts a web server at http://127.0.0.1:5000 that provides a REST API
    for phishing detection. Other applications can send HTTP requests
    to classify emails programmatically.

ENDPOINTS:
    GET  /          -> Service info
    POST /predict   -> Classify text

    Example request (using curl or Postman):
        POST http://127.0.0.1:5000/predict
        Body: {"text": "URGENT: Click here to verify your account"}
        Response: {"label": "phishing", "confidence": 0.98, "model": "..."}

HOW IT WORKS:
    1. On startup, loads the best model + TF-IDF vectoriser
    2. When a POST /predict request arrives:
       a) Cleans the input text (same clean_text function)
       b) Transforms text to TF-IDF vector
       c) Model predicts: phishing or legitimate
       d) Returns JSON with label + confidence score


==============================================================================
STEP 5b: STREAMLIT DASHBOARD  (dashboard.py)
==============================================================================
COMMAND:  & env/Scripts/python.exe -m streamlit run dashboard.py

WHAT IT DOES:
    Launches a visual web dashboard in your browser where you can
    paste any email or SMS text and get an instant verdict.

FEATURES:
    - Text input area to paste suspicious messages
    - "Analyse" button to classify
    - Red alert for phishing, green checkmark for legitimate
    - Confidence percentage
    - Model performance table showing all 5 models
    - Comparison chart and confusion matrix visualisations

HOW TO USE:
    1. Run the command above
    2. Browser opens automatically at http://localhost:8501
    3. Paste an email or SMS in the text area
    4. Click "Analyse"
    5. See the verdict


==============================================================================
FULL PIPELINE - RUN ALL STEPS
==============================================================================

    # Step 1: Prepare dataset
    & env/Scripts/python.exe build_dataset.py

    # Step 2: Extract features
    & env/Scripts/python.exe feature_engineering.py

    # Step 3: Train models
    & env/Scripts/python.exe train_model.py

    # Step 4: Evaluate models
    & env/Scripts/python.exe evaluate_model.py

    # Step 5: Launch dashboard
    & env/Scripts/python.exe -m streamlit run dashboard.py

    # (Optional) Run tests
    & env/Scripts/python.exe test_pipeline.py


==============================================================================
RESULTS ACHIEVED
==============================================================================

    Best Model:       Logistic Regression
    Accuracy:         96.66%
    Precision:        96.69%
    Recall:           96.66%
    F1-Score:         96.65%
    Dataset Size:     1,494 balanced emails (747 phishing + 747 legitimate)
    Features:         4,987 TF-IDF features (unigrams + bigrams)

==============================================================================
"""
>>>>>>> 13d69a23734bbe47eb1db6598bc86b5975a7a2ec
