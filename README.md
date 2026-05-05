# Phishing Detection Project

## Project Folder and File Structure

```text
phishing_project/
|
|-- data/                          # Raw datasets used by the project
|   |-- uci_sms/                   # UCI SMS Spam Collection dataset
|   |   |-- SMSSpamCollection      # SMS messages with spam/ham labels
|   |-- kaggle_phishing/           # Kaggle phishing dataset
|   |   |-- email_phishing_data.csv
|   |-- enron/                     # Optional Enron email corpus
|
|-- models/                        # Saved machine learning models and encoders
|   |-- tfidf_vectorizer.joblib    # TF-IDF vectorizer used for text features
|   |-- bow_vectorizer.joblib      # Bag of Words vectorizer
|   |-- svd_embedder.joblib        # SVD feature reducer
|   |-- label_encoder.joblib       # Converts labels to numeric values
|   |-- best_model.joblib          # Best trained phishing detection model
|   |-- best_model_name.joblib     # Name of the best model
|   |-- model_*.joblib             # Individual trained model files
|
|-- output/                        # Generated datasets, reports, and charts
|   |-- emails_balanced.csv        # Cleaned and balanced dataset
|   |-- features.joblib            # Extracted feature matrices
|   |-- training_results.joblib    # Model training results
|   |-- evaluation_report.txt      # Evaluation metrics report
|   |-- model_comparison.png       # Model comparison chart
|   |-- confusion_matrix_*.png     # Confusion matrix charts
|
|-- build_dataset.py               # Step 1: Load, clean, and balance datasets
|-- feature_engineering.py         # Step 2: Convert text into ML features
|-- train_model.py                 # Step 3: Train and save ML models
|-- evaluate_model.py              # Step 4: Evaluate trained models
|-- dashboard.py                   # Streamlit dashboard for user interaction
|-- app (1).py                     # Application/API file for prediction
|-- test_pipeline.py               # End-to-end pipeline test
|-- test_functions.py              # Function-level tests
|-- PROJECT_GUIDE.py               # Detailed project explanation and guide
|-- requirements.txt               # Required Python packages
|-- README.md                      # Project documentation
```

## Main Project Workflow

```text
Raw Data -> Data Cleaning -> Feature Engineering -> Model Training -> Model Evaluation -> Dashboard/API Prediction
```

## Key Files

- `build_dataset.py` prepares the raw datasets and creates the balanced dataset.
- `feature_engineering.py` converts cleaned text into numerical features.
- `train_model.py` trains multiple machine learning models and saves the best one.
- `evaluate_model.py` generates evaluation metrics and visual reports.
- `dashboard.py` provides a Streamlit interface for testing messages.
- `app (1).py` provides the application/API prediction logic.
<<<<<<< HEAD
- `PROJECT_GUIDE.py` contains the full step-by-step explanation of the project.
=======
- `PROJECT_GUIDE.py` contains the full step-by-step explanation of the project.
>>>>>>> 13d69a23734bbe47eb1db6598bc86b5975a7a2ec
