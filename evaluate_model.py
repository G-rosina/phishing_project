<<<<<<< HEAD
"""
Model Evaluation for Phishing Detection
Activity 7: Test models using accuracy, precision, recall and F1.

Generates:
- Confusion matrix for each model
- Model comparison bar chart
- Detailed evaluation report (text file)
"""
import joblib
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns


def plot_confusion_matrix(y_true, y_pred, labels, model_name, output_dir):
    """Plot and save a confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=labels, yticklabels=labels, ax=ax
    )
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Actual", fontsize=12)
    ax.set_title(f"Confusion Matrix - {model_name}", fontsize=14)
    plt.tight_layout()
    safe_name = model_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    filepath = output_dir / f"confusion_matrix_{safe_name}.png"
    fig.savefig(filepath, dpi=150)
    plt.close(fig)
    return filepath


def plot_comparison(results, output_dir):
    """Plot a bar chart comparing all models across 4 metrics."""
    model_names = list(results.keys())
    metrics = ["accuracy", "precision", "recall", "f1"]
    x = np.arange(len(model_names))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#F44336"]

    for i, metric in enumerate(metrics):
        values = [results[m][metric] for m in model_names]
        bars = ax.bar(x + i * width, values, width, label=metric.capitalize(), color=colors[i])
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=7)

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Model Comparison - Phishing Detection", fontsize=14)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(model_names, rotation=15, ha="right", fontsize=9)
    ax.legend(loc="lower right")
    ax.set_ylim(0.85, 1.02)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    filepath = output_dir / "model_comparison.png"
    fig.savefig(filepath, dpi=150)
    plt.close(fig)
    return filepath


def main():
    output_dir = Path("output")
    models_dir = Path("models")

    print("=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)
    print()

    # ── Load test data ────────────────────────────────────────
    data = joblib.load(output_dir / "features.joblib")
    X_test = data["X_test_tfidf"]
    y_test = data["y_test"]
    le = joblib.load(models_dir / "label_encoder.joblib")
    labels = list(le.classes_)

    # ── Find all saved models ─────────────────────────────────
    model_files = sorted(models_dir.glob("model_*.joblib"))
    if not model_files:
        print("Error: No trained models found. Run train_model.py first.")
        return

    # Separate text models from kaggle models
    text_model_files = [mf for mf in model_files if "kaggle" not in mf.stem]
    kaggle_model_files = [mf for mf in model_files if "kaggle" in mf.stem]

    # ── Evaluate text-based models ────────────────────────────
    print("--- TEXT-BASED MODELS (TF-IDF) ---")
    print()
    results = {}
    report_lines = []
    report_lines.append("PHISHING DETECTION - MODEL EVALUATION REPORT")
    report_lines.append("=" * 60)
    report_lines.append("")

    for mf in text_model_files:
        name = mf.stem.replace("model_", "").replace("_", " ").title()
        model = joblib.load(mf)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted")
        rec = recall_score(y_test, y_pred, average="weighted")
        f1 = f1_score(y_test, y_pred, average="weighted")

        results[name] = {
            "accuracy": acc, "precision": prec,
            "recall": rec, "f1": f1, "y_pred": y_pred,
        }

        print(f"{name}:")
        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1-Score:  {f1:.4f}")

        cm_path = plot_confusion_matrix(y_test, y_pred, labels, name, output_dir)
        print(f"  Confusion matrix: {cm_path}")
        print()

        report_lines.append(f"Model: {name}")
        report_lines.append("-" * 40)
        report_lines.append(f"  Accuracy:  {acc:.4f}")
        report_lines.append(f"  Precision: {prec:.4f}")
        report_lines.append(f"  Recall:    {rec:.4f}")
        report_lines.append(f"  F1-Score:  {f1:.4f}")
        report_lines.append("")
        report_lines.append(classification_report(y_test, y_pred, target_names=labels))
        report_lines.append("")

    # ── Evaluate Kaggle numeric models ────────────────────────
    kaggle_results = {}
    if kaggle_model_files and "X_test_kaggle" in data:
        print("--- KAGGLE NUMERIC MODELS ---")
        print()
        X_test_kg = data["X_test_kaggle"]
        y_test_kg = data["y_test_kaggle"]

        report_lines.append("")
        report_lines.append("KAGGLE NUMERIC FEATURE MODELS")
        report_lines.append("=" * 60)
        report_lines.append("")

        for mf in kaggle_model_files:
            name = mf.stem.replace("model_", "").replace("_", " ").title()
            model = joblib.load(mf)
            y_pred = model.predict(X_test_kg)

            acc = accuracy_score(y_test_kg, y_pred)
            prec = precision_score(y_test_kg, y_pred, average="weighted")
            rec = recall_score(y_test_kg, y_pred, average="weighted")
            f1 = f1_score(y_test_kg, y_pred, average="weighted")

            kaggle_results[name] = {
                "accuracy": acc, "precision": prec,
                "recall": rec, "f1": f1, "y_pred": y_pred,
            }

            print(f"{name}:")
            print(f"  Accuracy:  {acc:.4f}")
            print(f"  Precision: {prec:.4f}")
            print(f"  Recall:    {rec:.4f}")
            print(f"  F1-Score:  {f1:.4f}")

            cm_path = plot_confusion_matrix(y_test_kg, y_pred, labels,
                                            name, output_dir)
            print(f"  Confusion matrix: {cm_path}")
            print()

            report_lines.append(f"Model: {name}")
            report_lines.append("-" * 40)
            report_lines.append(f"  Accuracy:  {acc:.4f}")
            report_lines.append(f"  Precision: {prec:.4f}")
            report_lines.append(f"  Recall:    {rec:.4f}")
            report_lines.append(f"  F1-Score:  {f1:.4f}")
            report_lines.append("")

    # ── Comparison chart (text models only) ───────────────────
    if results:
        print("Generating model comparison chart...")
        comp_path = plot_comparison(results, output_dir)
        print(f"  Saved: {comp_path}")
        print()

    # ── Best model summary ────────────────────────────────────
    all_results = {**results, **kaggle_results}
    best_name = max(all_results, key=lambda k: all_results[k]["f1"])
    best = all_results[best_name]

    report_lines.append("=" * 60)
    report_lines.append(f"OVERALL BEST MODEL: {best_name}")
    report_lines.append(f"  F1-Score: {best['f1']:.4f}")
    report_lines.append(f"  Accuracy: {best['accuracy']:.4f}")
    report_lines.append("=" * 60)

    # Save report
    report_file = output_dir / "evaluation_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"Evaluation report saved to: {report_file}")

    # ── Final summary ─────────────────────────────────────────
    print()
    print("=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"{'Model':<40} {'Acc':>7} {'Prec':>7} {'Rec':>7} {'F1':>7}")
    print("-" * 70)
    for name, r in sorted(all_results.items(), key=lambda x: x[1]["f1"], reverse=True):
        marker = " <-- BEST" if name == best_name else ""
        print(f"{name:<40} {r['accuracy']:>7.4f} {r['precision']:>7.4f} {r['recall']:>7.4f} {r['f1']:>7.4f}{marker}")
    print("=" * 60)


if __name__ == "__main__":
    main()

=======
"""
Model Evaluation for Phishing Detection
Activity 7: Test models using accuracy, precision, recall and F1.

Generates:
- Confusion matrix for each model
- Model comparison bar chart
- Detailed evaluation report (text file)
"""
import joblib
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns


def plot_confusion_matrix(y_true, y_pred, labels, model_name, output_dir):
    """Plot and save a confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=labels, yticklabels=labels, ax=ax
    )
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Actual", fontsize=12)
    ax.set_title(f"Confusion Matrix - {model_name}", fontsize=14)
    plt.tight_layout()
    safe_name = model_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    filepath = output_dir / f"confusion_matrix_{safe_name}.png"
    fig.savefig(filepath, dpi=150)
    plt.close(fig)
    return filepath


def plot_comparison(results, output_dir):
    """Plot a bar chart comparing all models across 4 metrics."""
    model_names = list(results.keys())
    metrics = ["accuracy", "precision", "recall", "f1"]
    x = np.arange(len(model_names))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#F44336"]

    for i, metric in enumerate(metrics):
        values = [results[m][metric] for m in model_names]
        bars = ax.bar(x + i * width, values, width, label=metric.capitalize(), color=colors[i])
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=7)

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Model Comparison - Phishing Detection", fontsize=14)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(model_names, rotation=15, ha="right", fontsize=9)
    ax.legend(loc="lower right")
    ax.set_ylim(0.85, 1.02)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    filepath = output_dir / "model_comparison.png"
    fig.savefig(filepath, dpi=150)
    plt.close(fig)
    return filepath


def main():
    output_dir = Path("output")
    models_dir = Path("models")

    print("=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)
    print()

    # ── Load test data ────────────────────────────────────────
    data = joblib.load(output_dir / "features.joblib")
    X_test = data["X_test_tfidf"]
    y_test = data["y_test"]
    le = joblib.load(models_dir / "label_encoder.joblib")
    labels = list(le.classes_)

    # ── Find all saved models ─────────────────────────────────
    model_files = sorted(models_dir.glob("model_*.joblib"))
    if not model_files:
        print("Error: No trained models found. Run train_model.py first.")
        return

    # Separate text models from kaggle models
    text_model_files = [mf for mf in model_files if "kaggle" not in mf.stem]
    kaggle_model_files = [mf for mf in model_files if "kaggle" in mf.stem]

    # ── Evaluate text-based models ────────────────────────────
    print("--- TEXT-BASED MODELS (TF-IDF) ---")
    print()
    results = {}
    report_lines = []
    report_lines.append("PHISHING DETECTION - MODEL EVALUATION REPORT")
    report_lines.append("=" * 60)
    report_lines.append("")

    for mf in text_model_files:
        name = mf.stem.replace("model_", "").replace("_", " ").title()
        model = joblib.load(mf)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted")
        rec = recall_score(y_test, y_pred, average="weighted")
        f1 = f1_score(y_test, y_pred, average="weighted")

        results[name] = {
            "accuracy": acc, "precision": prec,
            "recall": rec, "f1": f1, "y_pred": y_pred,
        }

        print(f"{name}:")
        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1-Score:  {f1:.4f}")

        cm_path = plot_confusion_matrix(y_test, y_pred, labels, name, output_dir)
        print(f"  Confusion matrix: {cm_path}")
        print()

        report_lines.append(f"Model: {name}")
        report_lines.append("-" * 40)
        report_lines.append(f"  Accuracy:  {acc:.4f}")
        report_lines.append(f"  Precision: {prec:.4f}")
        report_lines.append(f"  Recall:    {rec:.4f}")
        report_lines.append(f"  F1-Score:  {f1:.4f}")
        report_lines.append("")
        report_lines.append(classification_report(y_test, y_pred, target_names=labels))
        report_lines.append("")

    # ── Evaluate Kaggle numeric models ────────────────────────
    kaggle_results = {}
    if kaggle_model_files and "X_test_kaggle" in data:
        print("--- KAGGLE NUMERIC MODELS ---")
        print()
        X_test_kg = data["X_test_kaggle"]
        y_test_kg = data["y_test_kaggle"]

        report_lines.append("")
        report_lines.append("KAGGLE NUMERIC FEATURE MODELS")
        report_lines.append("=" * 60)
        report_lines.append("")

        for mf in kaggle_model_files:
            name = mf.stem.replace("model_", "").replace("_", " ").title()
            model = joblib.load(mf)
            y_pred = model.predict(X_test_kg)

            acc = accuracy_score(y_test_kg, y_pred)
            prec = precision_score(y_test_kg, y_pred, average="weighted")
            rec = recall_score(y_test_kg, y_pred, average="weighted")
            f1 = f1_score(y_test_kg, y_pred, average="weighted")

            kaggle_results[name] = {
                "accuracy": acc, "precision": prec,
                "recall": rec, "f1": f1, "y_pred": y_pred,
            }

            print(f"{name}:")
            print(f"  Accuracy:  {acc:.4f}")
            print(f"  Precision: {prec:.4f}")
            print(f"  Recall:    {rec:.4f}")
            print(f"  F1-Score:  {f1:.4f}")

            cm_path = plot_confusion_matrix(y_test_kg, y_pred, labels,
                                            name, output_dir)
            print(f"  Confusion matrix: {cm_path}")
            print()

            report_lines.append(f"Model: {name}")
            report_lines.append("-" * 40)
            report_lines.append(f"  Accuracy:  {acc:.4f}")
            report_lines.append(f"  Precision: {prec:.4f}")
            report_lines.append(f"  Recall:    {rec:.4f}")
            report_lines.append(f"  F1-Score:  {f1:.4f}")
            report_lines.append("")

    # ── Comparison chart (text models only) ───────────────────
    if results:
        print("Generating model comparison chart...")
        comp_path = plot_comparison(results, output_dir)
        print(f"  Saved: {comp_path}")
        print()

    # ── Best model summary ────────────────────────────────────
    all_results = {**results, **kaggle_results}
    best_name = max(all_results, key=lambda k: all_results[k]["f1"])
    best = all_results[best_name]

    report_lines.append("=" * 60)
    report_lines.append(f"OVERALL BEST MODEL: {best_name}")
    report_lines.append(f"  F1-Score: {best['f1']:.4f}")
    report_lines.append(f"  Accuracy: {best['accuracy']:.4f}")
    report_lines.append("=" * 60)

    # Save report
    report_file = output_dir / "evaluation_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"Evaluation report saved to: {report_file}")

    # ── Final summary ─────────────────────────────────────────
    print()
    print("=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"{'Model':<40} {'Acc':>7} {'Prec':>7} {'Rec':>7} {'F1':>7}")
    print("-" * 70)
    for name, r in sorted(all_results.items(), key=lambda x: x[1]["f1"], reverse=True):
        marker = " <-- BEST" if name == best_name else ""
        print(f"{name:<40} {r['accuracy']:>7.4f} {r['precision']:>7.4f} {r['recall']:>7.4f} {r['f1']:>7.4f}{marker}")
    print("=" * 60)


if __name__ == "__main__":
    main()

>>>>>>> 13d69a23734bbe47eb1db6598bc86b5975a7a2ec
