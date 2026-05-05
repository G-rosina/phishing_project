<<<<<<< HEAD
import re
import random
from pathlib import Path
import pandas as pd
random.seed(42)
def clean_text(text):
    """ 
     clean and normalize email text
     Args:
         text: Raw email text (string)
     Return:
         cleaned text (string)    
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+", " URL ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+"," ",text).strip()
    return text
def load_uni_sms(path):
    """
    load UCI sms spam collection dataset
    format: Each line is "label<TAB>message"
    Args:
        path: Path to SMSSpamCollection file
    returns:
        DataFrame with 'text' and 'label' columns
     """
    rows = []
    
    if not Path(path).exists():
        raise FileNotFoundError(f"UCI SMS file not found: {path}")
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
            try:
                parts = line.strip().split("\t", 1)
                if len(parts) != 2:
                    print(f"warning: skipping malformed line {line_num}")
                    continue
                label, text = parts
                label = "phishing" if label.lower() == "spam" else "legitimate"
                rows.append({
                    "text": clean_text(text),
                    "label": label,
                    "source": "UCI_SMS"
                })
            except Exception as e:
                print(f"warning: Error processing line {line_num}: {e}")
                continue
    return pd.DataFrame(rows)
def load_enron(enron_dir, max_emails=2000):
    """
    Load Enron email corpus as legitimate emails.
    Parses raw email files and extracts the body text.
    Args:
        enron_dir: Path to enron directory containing user folders
        max_emails: Maximum number of emails to load (to keep balanced)
    Returns:
        DataFrame with 'text' and 'label' columns
    """
    rows = []
    enron_path = Path(enron_dir)
    if not enron_path.exists():
        raise FileNotFoundError(f"Enron directory not found: {enron_dir}")
    # Recursively find all files in enron subfolders
    all_files = [f for f in enron_path.rglob("*") if f.is_file()]
    random.shuffle(all_files)  # Shuffle to get variety
    for filepath in all_files:
        if len(rows) >= max_emails:
            break
        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # Enron emails: headers separated from body by a blank line
            # Find the first blank line that separates headers from body
            parts = content.split("\n\n", 1)
            if len(parts) < 2:
                continue
            body = parts[1].strip()
            # Skip very short or empty emails
            if len(body) < 20:
                continue
            # Skip forwarded email chains that are mostly headers
            cleaned = clean_text(body)
            if len(cleaned.split()) < 5:
                continue
            rows.append({
                "text": cleaned,
                "label": "legitimate",
                "source": "enron"
            })
        except Exception:
            continue
    return pd.DataFrame(rows)
def load_kaggle_csv(path):
    """
    load kaggle phishing dataset from CSV
    Handles both text-based and numeric-feature CSVs
    Args:
        path: Path to kaggle CSV file 
    returns:
        DataFrame with 'text' and 'label' columns (text CSV)
        or DataFrame with numeric features and 'label' column (numeric CSV)
    """
    try:
        df = pd.read_csv(path, encoding="utf-8", on_bad_lines='skip')
    except Exception as e:
        raise ValueError(f"Error reading kaggle CSV {path}: {e}")
    if len(df) == 0:
        raise ValueError(f"CSV file is empty: {path}")
    df.columns = [c.lower().strip() for c in df.columns]
    # Find label column
    label_col = None
    for c in ["label", "class", "phishing", "is_phishing", "spam", "target"]:
        if c in df.columns:
            label_col = c 
            break
    if label_col is None:
        print(f"available columns: {df.columns.tolist()}")
        raise ValueError(f"cannot find label column in {path}")
    # Find text column
    text_col = None
    for c in ["email", "text", "message", "body", "email_text", "content"]:
        if c in df.columns:
            text_col = c 
            break
    # If no text column found, treat as numeric feature dataset
    if text_col is None:
        print(f"  No text column found — treating as numeric feature dataset")
        df["label"] = df[label_col].astype(str).str.lower().str.strip()
        df["label"] = df["label"].replace({
            "1": "phishing", "0": "legitimate",
            "spam": "phishing", "ham": "legitimate"
        })
        valid_labels = {"phishing", "legitimate"}
        df = df[df["label"].isin(valid_labels)]
        df["source"] = "kaggle_numeric"
        return df
    # Text-based CSV path
    df = df[[text_col, label_col]].copy()
    df.columns = ["text", "label"] 
    df = df.dropna(subset=["text", "label"])
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df["label"] = df["label"].replace({
        "1": "phishing",
        "0": "legitimate",
        "phishing": "phishing",
        "legitimate": "legitimate",
        "ham": "legitimate",
        "spam": "phishing",
        "true": "phishing",
        "false": "legitimate",
        "yes": "phishing",
        "no": "legitimate"
    })
    valid_labels = {"phishing", "legitimate"}
    invalid_labels = set(df["label"].unique()) - valid_labels
    if invalid_labels:
        print(f"warning: found unexpected label values: {invalid_labels}")
        print(f"removing {len(df[~df['label'].isin(valid_labels)])} rows with invalid labels")
        df = df[df["label"].isin(valid_labels)]
    df["text"] = df["text"].apply(clean_text)
    df = df[df["text"].str.len() > 0]
    df["source"] = "kaggle"
    return df
def main():
    """
    Main function to load, combine, balance, and save dataset
    """
    base = Path("data")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print("="*60)
    print("PHISHING DETECTOR - DATA PREPARATION")
    print("="*60)
    print()
    # Load UCI SMS dataset
    print("Loading UCI SMS dataset...")
    uci_path = base / "uci_sms" / "SMSSpamCollection"
    if not uci_path.exists():
        print(f" Warning: UCI SMS file not found at {uci_path}")
        print("Skipping UCI dataset...")
        df_uci = pd.DataFrame(columns=["text", "label", "source"])
    else:
        try:
            df_uci = load_uni_sms(uci_path)
            print(f" loaded {len(df_uci)} emails from UCI dataset")
        except Exception as e:
            print(f" Error loading UCI dataset: {e}")
            df_uci = pd.DataFrame(columns=["text", "label", "source"])
    # LOAD KAGGLE DATASET
    print("\nLoading Kaggle phishing dataset...")
    kaggle_dir = base / "kaggle_phishing"
    df_kaggle_text = pd.DataFrame(columns=["text", "label", "source"])
    df_kaggle_numeric = None
    if not kaggle_dir.exists():
        print(f" Warning: kaggle directory not found: {kaggle_dir}")
    else:
        kaggle_files = list(kaggle_dir.glob("*.csv"))
        if not kaggle_files:
            print(f" Warning: No CSV files found in {kaggle_dir}")
        else:
            print(f"Found {len(kaggle_files)} CSV file(s)")
            print(f"Loading: {kaggle_files[0].name}")
            try:
                df_kaggle = load_kaggle_csv(kaggle_files[0])
                if "source" in df_kaggle.columns and df_kaggle["source"].iloc[0] == "kaggle_numeric":
                    df_kaggle_numeric = df_kaggle
                    print(f" Loaded {len(df_kaggle_numeric)} rows of numeric features")
                    # Save numeric features separately
                    numeric_file = output_dir / "kaggle_numeric_features.csv"
                    df_kaggle_numeric.to_csv(numeric_file, index=False)
                    print(f" Numeric features saved to {numeric_file}")
                else:
                    df_kaggle_text = df_kaggle
                    print(f" Loaded {len(df_kaggle_text)} emails from kaggle dataset")
            except Exception as e:
                print(f" Error loading kaggle dataset: {e}")
    # LOAD ENRON DATASET
    print("\nLoading Enron email corpus...")
    enron_dir = base / "enron"
    df_enron = pd.DataFrame(columns=["text", "label", "source"])
    if not enron_dir.exists():
        print(f" Warning: Enron directory not found at {enron_dir}")
    else:
        try:
            df_enron = load_enron(enron_dir, max_emails=2000)
            print(f" Loaded {len(df_enron)} legitimate emails from Enron corpus")
        except Exception as e:
            print(f" Error loading Enron dataset: {e}")
    # COMBINE TEXT DATASETS
    print("\nCombining text datasets...")
    df = pd.concat([df_uci, df_kaggle_text, df_enron], ignore_index=True)
    print(f"Total emails before balancing: {len(df)}")
    print(f"Distribution before balancing:")
    print(df["label"].value_counts())
    print()

    if "source" in df.columns:
        print("Distribution by source:")
        print(df["source"].value_counts())
        print()
    # BALANCE DATASET
    print("Balancing dataset...")
    phishing = df[df.label == "phishing"]
    legit = df[df.label == "legitimate"]
    print(f"Phishing emails: {len(phishing)}")
    print(f"Legitimate emails: {len(legit)}")
    n = min(len(phishing), len(legit))
    print(f"Sampling {n} from each class...")
    df_balanced = pd.concat([
        phishing.sample(n, random_state=42),
        legit.sample(n, random_state=42)
    ])
    df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
    # SAVE DATASET
    output_file = output_dir / "emails_balanced.csv"
    print(f"\nSaving to {output_file}...")
    df_balanced.to_csv(output_file, index=False)
    print(" Dataset created successfully!")
    print()
    # SUMMARY STATISTICS
    print("="*60)
    print("FINAL DATASET SUMMARY")
    print("="*60)
    print(f"Total emails: {len(df_balanced)}")
    print(f"Label distribution:")
    print(df_balanced["label"].value_counts())
    print()
    df_balanced["text_length"] = df_balanced["text"].str.split().str.len()
    print("Text length statistics (words):")
    print(f"  Mean: {df_balanced['text_length'].mean():.1f}")
    print(f"  Min: {df_balanced['text_length'].min()}")
    print(f"  Max: {df_balanced['text_length'].max()}")
    print()
    stats_file = output_dir / "dataset_statistics.txt"
    with open(stats_file, "w") as f:
        f.write("DATASET STATISTICS\n")
        f.write("="*60 + "\n\n")
        f.write(f"Creation date: {pd.Timestamp.now()}\n\n")
        f.write(f"Total emails: {len(df_balanced)}\n")
        f.write(f"Phishing: {len(df_balanced[df_balanced.label == 'phishing'])}\n")
        f.write(f"Legitimate: {len(df_balanced[df_balanced.label == 'legitimate'])}\n\n")
        f.write(f"Average text length: {df_balanced['text_length'].mean():.1f} words\n")
        f.write(f"Min text length: {df_balanced['text_length'].min()} words\n")
        f.write(f"Max text length: {df_balanced['text_length'].max()} words\n")
    print(f" statistics saved to {stats_file}")
    print("="*60)
if __name__ == "__main__":
=======
import re
import random
from pathlib import Path
import pandas as pd
random.seed(42)
def clean_text(text):
    """ 
     clean and normalize email text
     Args:
         text: Raw email text (string)
     Return:
         cleaned text (string)    
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+", " URL ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+"," ",text).strip()
    return text
def load_uni_sms(path):
    """
    load UCI sms spam collection dataset
    format: Each line is "label<TAB>message"
    Args:
        path: Path to SMSSpamCollection file
    returns:
        DataFrame with 'text' and 'label' columns
     """
    rows = []
    
    if not Path(path).exists():
        raise FileNotFoundError(f"UCI SMS file not found: {path}")
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
            try:
                parts = line.strip().split("\t", 1)
                if len(parts) != 2:
                    print(f"warning: skipping malformed line {line_num}")
                    continue
                label, text = parts
                label = "phishing" if label.lower() == "spam" else "legitimate"
                rows.append({
                    "text": clean_text(text),
                    "label": label,
                    "source": "UCI_SMS"
                })
            except Exception as e:
                print(f"warning: Error processing line {line_num}: {e}")
                continue
    return pd.DataFrame(rows)
def load_enron(enron_dir, max_emails=2000):
    """
    Load Enron email corpus as legitimate emails.
    Parses raw email files and extracts the body text.
    Args:
        enron_dir: Path to enron directory containing user folders
        max_emails: Maximum number of emails to load (to keep balanced)
    Returns:
        DataFrame with 'text' and 'label' columns
    """
    rows = []
    enron_path = Path(enron_dir)
    if not enron_path.exists():
        raise FileNotFoundError(f"Enron directory not found: {enron_dir}")
    # Recursively find all files in enron subfolders
    all_files = [f for f in enron_path.rglob("*") if f.is_file()]
    random.shuffle(all_files)  # Shuffle to get variety
    for filepath in all_files:
        if len(rows) >= max_emails:
            break
        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # Enron emails: headers separated from body by a blank line
            # Find the first blank line that separates headers from body
            parts = content.split("\n\n", 1)
            if len(parts) < 2:
                continue
            body = parts[1].strip()
            # Skip very short or empty emails
            if len(body) < 20:
                continue
            # Skip forwarded email chains that are mostly headers
            cleaned = clean_text(body)
            if len(cleaned.split()) < 5:
                continue
            rows.append({
                "text": cleaned,
                "label": "legitimate",
                "source": "enron"
            })
        except Exception:
            continue
    return pd.DataFrame(rows)
def load_kaggle_csv(path):
    """
    load kaggle phishing dataset from CSV
    Handles both text-based and numeric-feature CSVs
    Args:
        path: Path to kaggle CSV file 
    returns:
        DataFrame with 'text' and 'label' columns (text CSV)
        or DataFrame with numeric features and 'label' column (numeric CSV)
    """
    try:
        df = pd.read_csv(path, encoding="utf-8", on_bad_lines='skip')
    except Exception as e:
        raise ValueError(f"Error reading kaggle CSV {path}: {e}")
    if len(df) == 0:
        raise ValueError(f"CSV file is empty: {path}")
    df.columns = [c.lower().strip() for c in df.columns]
    # Find label column
    label_col = None
    for c in ["label", "class", "phishing", "is_phishing", "spam", "target"]:
        if c in df.columns:
            label_col = c 
            break
    if label_col is None:
        print(f"available columns: {df.columns.tolist()}")
        raise ValueError(f"cannot find label column in {path}")
    # Find text column
    text_col = None
    for c in ["email", "text", "message", "body", "email_text", "content"]:
        if c in df.columns:
            text_col = c 
            break
    # If no text column found, treat as numeric feature dataset
    if text_col is None:
        print(f"  No text column found — treating as numeric feature dataset")
        df["label"] = df[label_col].astype(str).str.lower().str.strip()
        df["label"] = df["label"].replace({
            "1": "phishing", "0": "legitimate",
            "spam": "phishing", "ham": "legitimate"
        })
        valid_labels = {"phishing", "legitimate"}
        df = df[df["label"].isin(valid_labels)]
        df["source"] = "kaggle_numeric"
        return df
    # Text-based CSV path
    df = df[[text_col, label_col]].copy()
    df.columns = ["text", "label"] 
    df = df.dropna(subset=["text", "label"])
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df["label"] = df["label"].replace({
        "1": "phishing",
        "0": "legitimate",
        "phishing": "phishing",
        "legitimate": "legitimate",
        "ham": "legitimate",
        "spam": "phishing",
        "true": "phishing",
        "false": "legitimate",
        "yes": "phishing",
        "no": "legitimate"
    })
    valid_labels = {"phishing", "legitimate"}
    invalid_labels = set(df["label"].unique()) - valid_labels
    if invalid_labels:
        print(f"warning: found unexpected label values: {invalid_labels}")
        print(f"removing {len(df[~df['label'].isin(valid_labels)])} rows with invalid labels")
        df = df[df["label"].isin(valid_labels)]
    df["text"] = df["text"].apply(clean_text)
    df = df[df["text"].str.len() > 0]
    df["source"] = "kaggle"
    return df
def main():
    """
    Main function to load, combine, balance, and save dataset
    """
    base = Path("data")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print("="*60)
    print("PHISHING DETECTOR - DATA PREPARATION")
    print("="*60)
    print()
    # Load UCI SMS dataset
    print("Loading UCI SMS dataset...")
    uci_path = base / "uci_sms" / "SMSSpamCollection"
    if not uci_path.exists():
        print(f" Warning: UCI SMS file not found at {uci_path}")
        print("Skipping UCI dataset...")
        df_uci = pd.DataFrame(columns=["text", "label", "source"])
    else:
        try:
            df_uci = load_uni_sms(uci_path)
            print(f" loaded {len(df_uci)} emails from UCI dataset")
        except Exception as e:
            print(f" Error loading UCI dataset: {e}")
            df_uci = pd.DataFrame(columns=["text", "label", "source"])
    # LOAD KAGGLE DATASET
    print("\nLoading Kaggle phishing dataset...")
    kaggle_dir = base / "kaggle_phishing"
    df_kaggle_text = pd.DataFrame(columns=["text", "label", "source"])
    df_kaggle_numeric = None
    if not kaggle_dir.exists():
        print(f" Warning: kaggle directory not found: {kaggle_dir}")
    else:
        kaggle_files = list(kaggle_dir.glob("*.csv"))
        if not kaggle_files:
            print(f" Warning: No CSV files found in {kaggle_dir}")
        else:
            print(f"Found {len(kaggle_files)} CSV file(s)")
            print(f"Loading: {kaggle_files[0].name}")
            try:
                df_kaggle = load_kaggle_csv(kaggle_files[0])
                if "source" in df_kaggle.columns and df_kaggle["source"].iloc[0] == "kaggle_numeric":
                    df_kaggle_numeric = df_kaggle
                    print(f" Loaded {len(df_kaggle_numeric)} rows of numeric features")
                    # Save numeric features separately
                    numeric_file = output_dir / "kaggle_numeric_features.csv"
                    df_kaggle_numeric.to_csv(numeric_file, index=False)
                    print(f" Numeric features saved to {numeric_file}")
                else:
                    df_kaggle_text = df_kaggle
                    print(f" Loaded {len(df_kaggle_text)} emails from kaggle dataset")
            except Exception as e:
                print(f" Error loading kaggle dataset: {e}")
    # LOAD ENRON DATASET
    print("\nLoading Enron email corpus...")
    enron_dir = base / "enron"
    df_enron = pd.DataFrame(columns=["text", "label", "source"])
    if not enron_dir.exists():
        print(f" Warning: Enron directory not found at {enron_dir}")
    else:
        try:
            df_enron = load_enron(enron_dir, max_emails=2000)
            print(f" Loaded {len(df_enron)} legitimate emails from Enron corpus")
        except Exception as e:
            print(f" Error loading Enron dataset: {e}")
    # COMBINE TEXT DATASETS
    print("\nCombining text datasets...")
    df = pd.concat([df_uci, df_kaggle_text, df_enron], ignore_index=True)
    print(f"Total emails before balancing: {len(df)}")
    print(f"Distribution before balancing:")
    print(df["label"].value_counts())
    print()

    if "source" in df.columns:
        print("Distribution by source:")
        print(df["source"].value_counts())
        print()
    # BALANCE DATASET
    print("Balancing dataset...")
    phishing = df[df.label == "phishing"]
    legit = df[df.label == "legitimate"]
    print(f"Phishing emails: {len(phishing)}")
    print(f"Legitimate emails: {len(legit)}")
    n = min(len(phishing), len(legit))
    print(f"Sampling {n} from each class...")
    df_balanced = pd.concat([
        phishing.sample(n, random_state=42),
        legit.sample(n, random_state=42)
    ])
    df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
    # SAVE DATASET
    output_file = output_dir / "emails_balanced.csv"
    print(f"\nSaving to {output_file}...")
    df_balanced.to_csv(output_file, index=False)
    print(" Dataset created successfully!")
    print()
    # SUMMARY STATISTICS
    print("="*60)
    print("FINAL DATASET SUMMARY")
    print("="*60)
    print(f"Total emails: {len(df_balanced)}")
    print(f"Label distribution:")
    print(df_balanced["label"].value_counts())
    print()
    df_balanced["text_length"] = df_balanced["text"].str.split().str.len()
    print("Text length statistics (words):")
    print(f"  Mean: {df_balanced['text_length'].mean():.1f}")
    print(f"  Min: {df_balanced['text_length'].min()}")
    print(f"  Max: {df_balanced['text_length'].max()}")
    print()
    stats_file = output_dir / "dataset_statistics.txt"
    with open(stats_file, "w") as f:
        f.write("DATASET STATISTICS\n")
        f.write("="*60 + "\n\n")
        f.write(f"Creation date: {pd.Timestamp.now()}\n\n")
        f.write(f"Total emails: {len(df_balanced)}\n")
        f.write(f"Phishing: {len(df_balanced[df_balanced.label == 'phishing'])}\n")
        f.write(f"Legitimate: {len(df_balanced[df_balanced.label == 'legitimate'])}\n\n")
        f.write(f"Average text length: {df_balanced['text_length'].mean():.1f} words\n")
        f.write(f"Min text length: {df_balanced['text_length'].min()} words\n")
        f.write(f"Max text length: {df_balanced['text_length'].max()} words\n")
    print(f" statistics saved to {stats_file}")
    print("="*60)
if __name__ == "__main__":
>>>>>>> 13d69a23734bbe47eb1db6598bc86b5975a7a2ec
    main()