<<<<<<< HEAD
"""
Model Training for Phishing Detection
Activity 6: Train ML and deep learning models.

Trains 5 classifiers on TF-IDF features:
1. Multinomial Naive Bayes
2. Logistic Regression
3. Random Forest
4. Support Vector Machine (LinearSVC)
5. Multi-Layer Perceptron (Neural Network)

Selects the best model and saves all models to models/ directory.
"""
import joblib
import numpy as np
from pathlib import Path
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report


def main():
    output_dir = Path("output")
    models_dir = Path("models")

    print("=" * 60)
    print("MODEL TRAINING")
    print("=" * 60)
    print()

    # ── Load features ─────────────────────────────────────────
    features_file = output_dir / "features.joblib"
    if not features_file.exists():
        print(f"Error: {features_file} not found. Run feature_engineering.py first.")
        return

    data = joblib.load(features_file)
    X_train = data["X_train_tfidf"]
    X_test = data["X_test_tfidf"]
    y_train = data["y_train"]
    y_test = data["y_test"]

    le = joblib.load(models_dir / "label_encoder.joblib")
    print(f"Train samples: {X_train.shape[0]}")
    print(f"Test samples:  {X_test.shape[0]}")
    print(f"Features:      {X_train.shape[1]}")
    print(f"Labels:        {list(le.classes_)}")
    print()

    # ── Define models ─────────────────────────────────────────
    models = {
        "Naive Bayes": MultinomialNB(alpha=1.0),
        "Logistic Regression": LogisticRegression(
            max_iter=1000, random_state=42, C=1.0
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=50, random_state=42, n_jobs=-1
        ),
        "SVM (LinearSVC)": LinearSVC(
            max_iter=2000, random_state=42, C=1.0
        ),
        "Neural Network (MLP)": MLPClassifier(
            hidden_layer_sizes=(256, 128),
            activation="relu",
            max_iter=300,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1,
            verbose=False
        ),
    }

    # ── Train and evaluate each model ─────────────────────────
    results = {}
    best_acc = 0
    best_name = ""

    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        results[name] = {
            "model": model,
            "accuracy": acc,
            "y_pred": y_pred,
        }

        print(f"  Accuracy: {acc:.4f}")

        if acc > best_acc:
            best_acc = acc
            best_name = name

        # Save individual model
        safe_name = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        joblib.dump(model, models_dir / f"model_{safe_name}.joblib")
        print(f"  Saved: model_{safe_name}.joblib")
        print()

    # ── Best model ────────────────────────────────────────────
    print("=" * 60)
    print(f"BEST MODEL: {best_name} (Accuracy: {best_acc:.4f})")
    print("=" * 60)
    print()

    # Save best model separately
    best_model = results[best_name]["model"]
    joblib.dump(best_model, models_dir / "best_model.joblib")
    joblib.dump(best_name, models_dir / "best_model_name.joblib")
    print(f"Best model saved to: models/best_model.joblib")
    print()

    # Classification report for best model
    print(f"Classification Report ({best_name}):")
    print("-" * 40)
    y_pred_best = results[best_name]["y_pred"]
    print(classification_report(y_test, y_pred_best, target_names=le.classes_))

    # ── Save results summary ──────────────────────────────────
    results_summary = {
        name: {"accuracy": r["accuracy"]}
        for name, r in results.items()
    }
    joblib.dump(results_summary, output_dir / "training_results.joblib")

    # Summary table
    print("=" * 60)
    print("ALL TEXT-BASED MODELS")
    print("=" * 60)
    print(f"{'Model':<30} {'Accuracy':>10}")
    print("-" * 42)
    for name, r in sorted(results.items(), key=lambda x: x[1]["accuracy"], reverse=True):
        marker = " <-- BEST" if name == best_name else ""
        print(f"{name:<30} {r['accuracy']:>10.4f}{marker}")
    print("=" * 60)

    # ── Train on Kaggle numeric features ──────────────────────
    if "X_train_kaggle" in data:
        print()
        print("=" * 60)
        print("KAGGLE NUMERIC FEATURES - MODEL TRAINING")
        print("=" * 60)
        print()

        X_train_kg = data["X_train_kaggle"]
        X_test_kg = data["X_test_kaggle"]
        y_train_kg = data["y_train_kaggle"]
        y_test_kg = data["y_test_kaggle"]

        print(f"Kaggle train: {X_train_kg.shape[0]} samples, {X_train_kg.shape[1]} features")
        print(f"Kaggle test:  {X_test_kg.shape[0]} samples")
        print(f"Features: {data.get('feature_cols', 'N/A')}")
        print()

        kaggle_models = {
            "Kaggle - Logistic Regression": LogisticRegression(
                max_iter=1000, random_state=42
            ),
            "Kaggle - Random Forest": RandomForestClassifier(
                n_estimators=200, max_depth=50, random_state=42, n_jobs=-1
            ),
            "Kaggle - Neural Network": MLPClassifier(
                hidden_layer_sizes=(128, 64),
                activation="relu", max_iter=300,
                random_state=42, early_stopping=True,
                validation_fraction=0.1, verbose=False
            ),
        }

        kaggle_results = {}
        for name, model in kaggle_models.items():
            print(f"Training {name}...")
            model.fit(X_train_kg, y_train_kg)
            y_pred = model.predict(X_test_kg)
            acc = accuracy_score(y_test_kg, y_pred)
            kaggle_results[name] = {"accuracy": acc}
            safe_name = name.lower().replace(" ", "_").replace("-", "").replace("(", "").replace(")", "")
            joblib.dump(model, models_dir / f"model_{safe_name}.joblib")
            print(f"  Accuracy: {acc:.4f}")
            print(f"  Saved: model_{safe_name}.joblib")
            print()

        # Add Kaggle results to overall summary
        results_summary.update(kaggle_results)
        joblib.dump(results_summary, output_dir / "training_results.joblib")

        print("=" * 60)
        print("KAGGLE NUMERIC MODELS SUMMARY")
        print("=" * 60)
        print(f"{'Model':<40} {'Accuracy':>10}")
        print("-" * 52)
        for name, r in sorted(kaggle_results.items(), key=lambda x: x[1]["accuracy"], reverse=True):
            print(f"{name:<40} {r['accuracy']:>10.4f}")
        print("=" * 60)
    else:
        print("\nNo Kaggle numeric features found (skipping).")


if __name__ == "__main__":
    main()
=======
"""
Model Training for Phishing Detection
Activity 6: Train ML and deep learning models.

Trains 5 classifiers on TF-IDF features:
1. Multinomial Naive Bayes
2. Logistic Regression
3. Random Forest
4. Support Vector Machine (LinearSVC)
5. Multi-Layer Perceptron (Neural Network)

Selects the best model and saves all models to models/ directory.
"""
import joblib
import numpy as np
from pathlib import Path
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report


def main():
    output_dir = Path("output")
    models_dir = Path("models")

    print("=" * 60)
    print("MODEL TRAINING")
    print("=" * 60)
    print()

    # ── Load features ─────────────────────────────────────────
    features_file = output_dir / "features.joblib"
    if not features_file.exists():
        print(f"Error: {features_file} not found. Run feature_engineering.py first.")
        return

    data = joblib.load(features_file)
    X_train = data["X_train_tfidf"]
    X_test = data["X_test_tfidf"]
    y_train = data["y_train"]
    y_test = data["y_test"]

    le = joblib.load(models_dir / "label_encoder.joblib")
    print(f"Train samples: {X_train.shape[0]}")
    print(f"Test samples:  {X_test.shape[0]}")
    print(f"Features:      {X_train.shape[1]}")
    print(f"Labels:        {list(le.classes_)}")
    print()

    # ── Define models ─────────────────────────────────────────
    models = {
        "Naive Bayes": MultinomialNB(alpha=1.0),
        "Logistic Regression": LogisticRegression(
            max_iter=1000, random_state=42, C=1.0
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=50, random_state=42, n_jobs=-1
        ),
        "SVM (LinearSVC)": LinearSVC(
            max_iter=2000, random_state=42, C=1.0
        ),
        "Neural Network (MLP)": MLPClassifier(
            hidden_layer_sizes=(256, 128),
            activation="relu",
            max_iter=300,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1,
            verbose=False
        ),
    }

    # ── Train and evaluate each model ─────────────────────────
    results = {}
    best_acc = 0
    best_name = ""

    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        results[name] = {
            "model": model,
            "accuracy": acc,
            "y_pred": y_pred,
        }

        print(f"  Accuracy: {acc:.4f}")

        if acc > best_acc:
            best_acc = acc
            best_name = name

        # Save individual model
        safe_name = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        joblib.dump(model, models_dir / f"model_{safe_name}.joblib")
        print(f"  Saved: model_{safe_name}.joblib")
        print()

    # ── Best model ────────────────────────────────────────────
    print("=" * 60)
    print(f"BEST MODEL: {best_name} (Accuracy: {best_acc:.4f})")
    print("=" * 60)
    print()

    # Save best model separately
    best_model = results[best_name]["model"]
    joblib.dump(best_model, models_dir / "best_model.joblib")
    joblib.dump(best_name, models_dir / "best_model_name.joblib")
    print(f"Best model saved to: models/best_model.joblib")
    print()

    # Classification report for best model
    print(f"Classification Report ({best_name}):")
    print("-" * 40)
    y_pred_best = results[best_name]["y_pred"]
    print(classification_report(y_test, y_pred_best, target_names=le.classes_))

    # ── Save results summary ──────────────────────────────────
    results_summary = {
        name: {"accuracy": r["accuracy"]}
        for name, r in results.items()
    }
    joblib.dump(results_summary, output_dir / "training_results.joblib")

    # Summary table
    print("=" * 60)
    print("ALL TEXT-BASED MODELS")
    print("=" * 60)
    print(f"{'Model':<30} {'Accuracy':>10}")
    print("-" * 42)
    for name, r in sorted(results.items(), key=lambda x: x[1]["accuracy"], reverse=True):
        marker = " <-- BEST" if name == best_name else ""
        print(f"{name:<30} {r['accuracy']:>10.4f}{marker}")
    print("=" * 60)

    # ── Train on Kaggle numeric features ──────────────────────
    if "X_train_kaggle" in data:
        print()
        print("=" * 60)
        print("KAGGLE NUMERIC FEATURES - MODEL TRAINING")
        print("=" * 60)
        print()

        X_train_kg = data["X_train_kaggle"]
        X_test_kg = data["X_test_kaggle"]
        y_train_kg = data["y_train_kaggle"]
        y_test_kg = data["y_test_kaggle"]

        print(f"Kaggle train: {X_train_kg.shape[0]} samples, {X_train_kg.shape[1]} features")
        print(f"Kaggle test:  {X_test_kg.shape[0]} samples")
        print(f"Features: {data.get('feature_cols', 'N/A')}")
        print()

        kaggle_models = {
            "Kaggle - Logistic Regression": LogisticRegression(
                max_iter=1000, random_state=42
            ),
            "Kaggle - Random Forest": RandomForestClassifier(
                n_estimators=200, max_depth=50, random_state=42, n_jobs=-1
            ),
            "Kaggle - Neural Network": MLPClassifier(
                hidden_layer_sizes=(128, 64),
                activation="relu", max_iter=300,
                random_state=42, early_stopping=True,
                validation_fraction=0.1, verbose=False
            ),
        }

        kaggle_results = {}
        for name, model in kaggle_models.items():
            print(f"Training {name}...")
            model.fit(X_train_kg, y_train_kg)
            y_pred = model.predict(X_test_kg)
            acc = accuracy_score(y_test_kg, y_pred)
            kaggle_results[name] = {"accuracy": acc}
            safe_name = name.lower().replace(" ", "_").replace("-", "").replace("(", "").replace(")", "")
            joblib.dump(model, models_dir / f"model_{safe_name}.joblib")
            print(f"  Accuracy: {acc:.4f}")
            print(f"  Saved: model_{safe_name}.joblib")
            print()

        # Add Kaggle results to overall summary
        results_summary.update(kaggle_results)
        joblib.dump(results_summary, output_dir / "training_results.joblib")

        print("=" * 60)
        print("KAGGLE NUMERIC MODELS SUMMARY")
        print("=" * 60)
        print(f"{'Model':<40} {'Accuracy':>10}")
        print("-" * 52)
        for name, r in sorted(kaggle_results.items(), key=lambda x: x[1]["accuracy"], reverse=True):
            print(f"{name:<40} {r['accuracy']:>10.4f}")
        print("=" * 60)
    else:
        print("\nNo Kaggle numeric features found (skipping).")


if __name__ == "__main__":
    main()
>>>>>>> 13d69a23734bbe47eb1db6598bc86b5975a7a2ec
