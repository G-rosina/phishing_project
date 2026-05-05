<<<<<<< HEAD
"""
Feature Engineering for Phishing Detection
Activity 5: Apply TF-IDF, Bag of Words, and embeddings.

Loads the balanced dataset and creates three feature representations:
1. TF-IDF (Term Frequency - Inverse Document Frequency)
2. Bag of Words (BoW)
3. Dense Embeddings via TruncatedSVD on TF-IDF
Also prepares Kaggle numeric features (num_words, num_links, etc.)

Saves all vectorisers and feature matrices for model training.
"""
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import LabelEncoder, StandardScaler


def main():
    output_dir = Path("output")
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    # ── Load balanced dataset ──────────────────────────────────
    print("=" * 60)
    print("FEATURE ENGINEERING")
    print("=" * 60)
    print()

    data_file = output_dir / "emails_balanced.csv"
    if not data_file.exists():
        print(f"Error: {data_file} not found. Run build_dataset.py first.")
        return

    df = pd.read_csv(data_file)
    print(f"Loaded {len(df)} emails from {data_file}")
    print(f"Label distribution: {df['label'].value_counts().to_dict()}")
    print()

    # ── Encode labels ──────────────────────────────────────────
    le = LabelEncoder()
    y = le.fit_transform(df["label"])  # legitimate=0, phishing=1
    print(f"Label encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}")
    joblib.dump(le, models_dir / "label_encoder.joblib")

    # ── Train/Test split ───────────────────────────────────────
    X_text = df["text"].fillna("")
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train set: {len(X_train_text)} samples")
    print(f"Test set:  {len(X_test_text)} samples")
    print()

    # ── 1. TF-IDF Features ────────────────────────────────────
    print("Building TF-IDF features...")
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),   # unigrams + bigrams
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )
    X_train_tfidf = tfidf.fit_transform(X_train_text)
    X_test_tfidf = tfidf.transform(X_test_text)
    print(f"  TF-IDF shape: {X_train_tfidf.shape}")
    print(f"  Top features: {tfidf.get_feature_names_out()[:10].tolist()}")
    joblib.dump(tfidf, models_dir / "tfidf_vectorizer.joblib")
    print("  Saved: tfidf_vectorizer.joblib")
    print()

    # ── 2. Bag of Words Features ──────────────────────────────
    print("Building Bag of Words features...")
    bow = CountVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95
    )
    X_train_bow = bow.fit_transform(X_train_text)
    X_test_bow = bow.transform(X_test_text)
    print(f"  BoW shape: {X_train_bow.shape}")
    joblib.dump(bow, models_dir / "bow_vectorizer.joblib")
    print("  Saved: bow_vectorizer.joblib")
    print()

    # ── 3. Dense Embeddings (SVD on TF-IDF) ───────────────────
    print("Building dense embeddings (TruncatedSVD on TF-IDF)...")
    n_components = min(100, X_train_tfidf.shape[1] - 1)
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    X_train_emb = svd.fit_transform(X_train_tfidf)
    X_test_emb = svd.transform(X_test_tfidf)
    explained = svd.explained_variance_ratio_.sum()
    print(f"  Embedding shape: {X_train_emb.shape}")
    print(f"  Explained variance: {explained:.2%}")
    joblib.dump(svd, models_dir / "svd_embedder.joblib")
    print("  Saved: svd_embedder.joblib")
    print()

    # ── 4. Kaggle Numeric Features ────────────────────────────
    kaggle_file = output_dir / "kaggle_numeric_features.csv"
    kaggle_data = None
    if kaggle_file.exists():
        print("Loading Kaggle numeric features...")
        df_kaggle = pd.read_csv(kaggle_file)
        # Get numeric columns (exclude label and source)
        feature_cols = [c for c in df_kaggle.columns if c not in ["label", "source"]]
        print(f"  Numeric features: {feature_cols}")

        X_kaggle = df_kaggle[feature_cols].values
        y_kaggle = LabelEncoder().fit_transform(df_kaggle["label"])

        # Split Kaggle data
        X_train_kg, X_test_kg, y_train_kg, y_test_kg = train_test_split(
            X_kaggle, y_kaggle, test_size=0.2, random_state=42, stratify=y_kaggle
        )

        # Scale numeric features
        scaler = StandardScaler()
        X_train_kg = np.array(scaler.fit_transform(X_train_kg))
        X_test_kg = np.array(scaler.transform(X_test_kg))

        print(f"  Kaggle train: {X_train_kg.shape}")
        print(f"  Kaggle test:  {X_test_kg.shape}")
        print(f"  Kaggle labels: {np.bincount(y_kaggle)} (legitimate/phishing)")
        joblib.dump(scaler, models_dir / "kaggle_scaler.joblib")
        joblib.dump(feature_cols, models_dir / "kaggle_feature_cols.joblib")
        print("  Saved: kaggle_scaler.joblib")

        kaggle_data = {
            "X_train_kaggle": X_train_kg,
            "X_test_kaggle": X_test_kg,
            "y_train_kaggle": y_train_kg,
            "y_test_kaggle": y_test_kg,
            "feature_cols": feature_cols,
        }
        print()
    else:
        print("No Kaggle numeric features found (skipping).")
        print()

    # ── Save feature matrices and labels ──────────────────────
    print("Saving feature matrices...")
    save_data = {
        "X_train_tfidf": X_train_tfidf,
        "X_test_tfidf": X_test_tfidf,
        "X_train_bow": X_train_bow,
        "X_test_bow": X_test_bow,
        "X_train_emb": X_train_emb,
        "X_test_emb": X_test_emb,
        "y_train": y_train,
        "y_test": y_test,
    }
    if kaggle_data:
        save_data.update(kaggle_data)
    joblib.dump(save_data, output_dir / "features.joblib")
    print(f"  Saved: output/features.joblib")

    # ── Summary ───────────────────────────────────────────────
    print()
    print("=" * 60)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 60)
    print(f"  TF-IDF:       {X_train_tfidf.shape[1]} features")
    print(f"  Bag of Words: {X_train_bow.shape[1]} features")
    print(f"  Embeddings:   {X_train_emb.shape[1]} dimensions")
    if kaggle_data:
        print(f"  Kaggle:       {kaggle_data['X_train_kaggle'].shape[1]} numeric features")
    print(f"  Train/Test:   {len(y_train)}/{len(y_test)} samples (text)")
    if kaggle_data:
        print(f"  Train/Test:   {kaggle_data['X_train_kaggle'].shape[0]}/{kaggle_data['X_test_kaggle'].shape[0]} samples (Kaggle)")
    print(f"  Models dir:   {models_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
=======
"""
Feature Engineering for Phishing Detection
Activity 5: Apply TF-IDF, Bag of Words, and embeddings.

Loads the balanced dataset and creates three feature representations:
1. TF-IDF (Term Frequency - Inverse Document Frequency)
2. Bag of Words (BoW)
3. Dense Embeddings via TruncatedSVD on TF-IDF
Also prepares Kaggle numeric features (num_words, num_links, etc.)

Saves all vectorisers and feature matrices for model training.
"""
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import LabelEncoder, StandardScaler


def main():
    output_dir = Path("output")
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    # ── Load balanced dataset ──────────────────────────────────
    print("=" * 60)
    print("FEATURE ENGINEERING")
    print("=" * 60)
    print()

    data_file = output_dir / "emails_balanced.csv"
    if not data_file.exists():
        print(f"Error: {data_file} not found. Run build_dataset.py first.")
        return

    df = pd.read_csv(data_file)
    print(f"Loaded {len(df)} emails from {data_file}")
    print(f"Label distribution: {df['label'].value_counts().to_dict()}")
    print()

    # ── Encode labels ──────────────────────────────────────────
    le = LabelEncoder()
    y = le.fit_transform(df["label"])  # legitimate=0, phishing=1
    print(f"Label encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}")
    joblib.dump(le, models_dir / "label_encoder.joblib")

    # ── Train/Test split ───────────────────────────────────────
    X_text = df["text"].fillna("")
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train set: {len(X_train_text)} samples")
    print(f"Test set:  {len(X_test_text)} samples")
    print()

    # ── 1. TF-IDF Features ────────────────────────────────────
    print("Building TF-IDF features...")
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),   # unigrams + bigrams
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )
    X_train_tfidf = tfidf.fit_transform(X_train_text)
    X_test_tfidf = tfidf.transform(X_test_text)
    print(f"  TF-IDF shape: {X_train_tfidf.shape}")
    print(f"  Top features: {tfidf.get_feature_names_out()[:10].tolist()}")
    joblib.dump(tfidf, models_dir / "tfidf_vectorizer.joblib")
    print("  Saved: tfidf_vectorizer.joblib")
    print()

    # ── 2. Bag of Words Features ──────────────────────────────
    print("Building Bag of Words features...")
    bow = CountVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95
    )
    X_train_bow = bow.fit_transform(X_train_text)
    X_test_bow = bow.transform(X_test_text)
    print(f"  BoW shape: {X_train_bow.shape}")
    joblib.dump(bow, models_dir / "bow_vectorizer.joblib")
    print("  Saved: bow_vectorizer.joblib")
    print()

    # ── 3. Dense Embeddings (SVD on TF-IDF) ───────────────────
    print("Building dense embeddings (TruncatedSVD on TF-IDF)...")
    n_components = min(100, X_train_tfidf.shape[1] - 1)
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    X_train_emb = svd.fit_transform(X_train_tfidf)
    X_test_emb = svd.transform(X_test_tfidf)
    explained = svd.explained_variance_ratio_.sum()
    print(f"  Embedding shape: {X_train_emb.shape}")
    print(f"  Explained variance: {explained:.2%}")
    joblib.dump(svd, models_dir / "svd_embedder.joblib")
    print("  Saved: svd_embedder.joblib")
    print()

    # ── 4. Kaggle Numeric Features ────────────────────────────
    kaggle_file = output_dir / "kaggle_numeric_features.csv"
    kaggle_data = None
    if kaggle_file.exists():
        print("Loading Kaggle numeric features...")
        df_kaggle = pd.read_csv(kaggle_file)
        # Get numeric columns (exclude label and source)
        feature_cols = [c for c in df_kaggle.columns if c not in ["label", "source"]]
        print(f"  Numeric features: {feature_cols}")

        X_kaggle = df_kaggle[feature_cols].values
        y_kaggle = LabelEncoder().fit_transform(df_kaggle["label"])

        # Split Kaggle data
        X_train_kg, X_test_kg, y_train_kg, y_test_kg = train_test_split(
            X_kaggle, y_kaggle, test_size=0.2, random_state=42, stratify=y_kaggle
        )

        # Scale numeric features
        scaler = StandardScaler()
        X_train_kg = np.array(scaler.fit_transform(X_train_kg))
        X_test_kg = np.array(scaler.transform(X_test_kg))

        print(f"  Kaggle train: {X_train_kg.shape}")
        print(f"  Kaggle test:  {X_test_kg.shape}")
        print(f"  Kaggle labels: {np.bincount(y_kaggle)} (legitimate/phishing)")
        joblib.dump(scaler, models_dir / "kaggle_scaler.joblib")
        joblib.dump(feature_cols, models_dir / "kaggle_feature_cols.joblib")
        print("  Saved: kaggle_scaler.joblib")

        kaggle_data = {
            "X_train_kaggle": X_train_kg,
            "X_test_kaggle": X_test_kg,
            "y_train_kaggle": y_train_kg,
            "y_test_kaggle": y_test_kg,
            "feature_cols": feature_cols,
        }
        print()
    else:
        print("No Kaggle numeric features found (skipping).")
        print()

    # ── Save feature matrices and labels ──────────────────────
    print("Saving feature matrices...")
    save_data = {
        "X_train_tfidf": X_train_tfidf,
        "X_test_tfidf": X_test_tfidf,
        "X_train_bow": X_train_bow,
        "X_test_bow": X_test_bow,
        "X_train_emb": X_train_emb,
        "X_test_emb": X_test_emb,
        "y_train": y_train,
        "y_test": y_test,
    }
    if kaggle_data:
        save_data.update(kaggle_data)
    joblib.dump(save_data, output_dir / "features.joblib")
    print(f"  Saved: output/features.joblib")

    # ── Summary ───────────────────────────────────────────────
    print()
    print("=" * 60)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 60)
    print(f"  TF-IDF:       {X_train_tfidf.shape[1]} features")
    print(f"  Bag of Words: {X_train_bow.shape[1]} features")
    print(f"  Embeddings:   {X_train_emb.shape[1]} dimensions")
    if kaggle_data:
        print(f"  Kaggle:       {kaggle_data['X_train_kaggle'].shape[1]} numeric features")
    print(f"  Train/Test:   {len(y_train)}/{len(y_test)} samples (text)")
    if kaggle_data:
        print(f"  Train/Test:   {kaggle_data['X_train_kaggle'].shape[0]}/{kaggle_data['X_test_kaggle'].shape[0]} samples (Kaggle)")
    print(f"  Models dir:   {models_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
>>>>>>> 13d69a23734bbe47eb1db6598bc86b5975a7a2ec
