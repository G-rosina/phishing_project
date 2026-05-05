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
   text = re.sub(r"http\s+", " URL ", text)
   text = re.sub(r"[^a-z0-9\s]", " ", text)
   text = re.sub(r"\s+"," ",text).strip()
   return text
def load_uni_sms(path):
   """
   load UNCI sms spam collection dataset
   format: Each line is "label<TAB>meassage"
   Args:
       path: Path to SMSSpamCollection file
   returns:
       DataFrame with 'text' and 'label' columns
    """
   rows = []
   
   if not path(path).exists():
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
               "source":"UCI_SMS"
               })
          except exemption as e:
                print(f"warning: Error processing line {line_num}: {e}")
                continue
   return pd.DataFrame(rows)
def load_kaggle_csv(path):
    """
    load kaggle phishing dataset from CVS
    Handles various column naming convetions 
    Args:
        path: Path to kaggle CVS file 
    returns:
        DataFrame with 'text' and 'label' columns 
    """
    try:
        df = pd.read_csv(path, encoding="utf-8", on_bad_lines='skip')
    except Exception as e:
        raise ValueError(f"Error reading kaggle CVS {path}: {e}")
    if len(df) == 0:
        raise ValueError(f"CSV file is empty : {path}")
    df.columns = [c.lower().strip()for c in df.columns]
    text_col = None
    for c in ["email","text", "message", "body", "email_text", "content"]:
        if c in df.columns:
            text_col = c 
            break
    label_col = None
    for c in ["label","class", "phishing", "is_phishing", "spam", "target"]:
        if c in df.columns:
            label_col = c 
            break
    if text_col is None or label_col is None:
        print(f"available columns: {df.columns.tolist()}")
        raise ValueError(f"cannot find text or label column in {path}")
    df = df[[text_col, label_col]].copy()
    df.columns = ["text", "label"] 
    df = df.dropna(subset=["text","label"])
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df["label"] = df["label"].replace({
        "1": "phishing",
        "0": "legitimate",
        "phishing": "phishing",
        "legitimate": "legitimate",
        "ham": "legitimate",
        "spam": "phishing"
        "true": "phishing",
        "false": "legitimate",
        "yes": "phishing",
        "no": "legitimate"
    })
    
    valid_labels = {"phishing", "legitimate"}
    invalid_labels = set(df["label"].unique()) - valid_labels
    if invalid_labels:
        print(f"warning: found unexpcted label values:{ivalid_labels}")
        print(f"removing {len(df[~df['label'].isin(valid_labels)])} rows with invalid labels")
        df = df[df["label"].isin(valid_labels)]
    df["text"] = df["text"].apply(clean_text)
    df = df[df["text".str.len()>0]]
    df["source"] = "kaggle"
    return df
def main():
    """
    Main function to load, combine, balance, and save dataset
    """
    base = Path("data")
    output_dir = Path("output")
    output_dir.mkdir(exit_ok=True)
    print("="*60)
    print("PHISHING DETECTOR - DATA PREPARATION")
    print("="*60)
    print()
#load UCI sms dataset
    print("Loading UCI SMS dataset...")
    uci_path = base / "uci_sms" / "SMSSpamCollection"
    if not uci_path.exists():
        print(f" Warning: UCI SMS file not found at {uci_path}")
        print("Skipping UCI dataset...")
        df_uci = pd.DataFrame(columns=["text", "label", "source"])
    else:
        try:
            df_uci = load_uci_sms(uci_path)
            print(f" loaded {len(df_uci)} emails from UCI dataset")
        except Exception as e:
            print(f" Error loading UCI dataset: {e}")
            df_uci = pd.DataFrame(columns=["text", "label", "source"])
         #LOAD KAGGLE DATASET
    print("\nLoading Kaggle phishing dataset...")
    kaggle_dir = base / "kaggle_phishing"
    kaggle_files = list(kaggle_dir.glob("*.csv"))
if not kaggle_dir.exists():
    print(f" Error:kaggle directory not found: {kaggle_dir}")
    print("Please create the directory and add your kaggle dataset")
    return
if not kaggle_files:
    print(f" Error: No CSV files found in {kaggle_dir}")
    print("Please donwload and place kaggle dataset in this folder")
    return
#LOAD THE FIRST CSV FILE FOUND
print(f"Found {len(kaggle_files)} CSV file(s)")
print(f"Loading: {kaggle_file[0].name}")
try:
    df_kaggle =load_kaggle_csv(kaggle_files[0])
    print(f" Loaded{len(df_kaggle)} emails from kaggle dataset")
except Exception as e:
    print(f" Error loading kaggle dataset: {e}")
    return
#COMBINE DATASET
print("\nCombining datasets...")
df = pd.concat([df_uci, df_kaggle], ignore_index=True)
print(f"Total emails before balancing: {len(df)}")
print(f"Distribution before balancing:")
print(df["label"].value_counts())
print()
if "source" in df.columns:  
    print("Distribution by source:")
    print(df["source"].value_counts())
    print()
#BALANCE DATASET
print("Balancing dataset...")
phishing = df[df.label == "phishing"]
legit = df[df.label == "legitimate"]
print(f"Phishing emails:{len(phishing)}")
print(f"Legitimate emails: {len(legit)}")
n = min(len(phishing), len(legit))
print(f"Sampling {n} from each class...")
df_balanced = pd.concat([
    phishing.sample(n, random_state=42),
    legit.sample(n, random_state=42)
])      
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
#SAVE DATASET
output_file = output_dir / "emails_balanced.csv"
print(f"\nSaving to {output_file}...")
df_balanced.to_csv(output_file, index=False)
print(" Dataset created successfully!")
print()
#SUMMARY STATISTICS
print("="*60)
print("FINAL DATASET SUMMARY")
print("="*60)
print(f"Total emails: {len(df_balanced)}")
print(f"Label distribution:")
print(df_balanced["label"].value_counts())
print()
df_balanced["text_length"] = df_balanced["text"].str.split().str.len()
print("Text length statistics (words):")
print(f"  Mean:{df_balanced['text_length'].mean():.1f}")
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
    main()
        
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
   text = re.sub(r"http\s+", " URL ", text)
   text = re.sub(r"[^a-z0-9\s]", " ", text)
   text = re.sub(r"\s+"," ",text).strip()
   return text
def load_uni_sms(path):
   """
   load UNCI sms spam collection dataset
   format: Each line is "label<TAB>meassage"
   Args:
       path: Path to SMSSpamCollection file
   returns:
       DataFrame with 'text' and 'label' columns
    """
   rows = []
   
   if not path(path).exists():
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
               "source":"UCI_SMS"
               })
          except exemption as e:
                print(f"warning: Error processing line {line_num}: {e}")
                continue
   return pd.DataFrame(rows)
def load_kaggle_csv(path):
    """
    load kaggle phishing dataset from CVS
    Handles various column naming convetions 
    Args:
        path: Path to kaggle CVS file 
    returns:
        DataFrame with 'text' and 'label' columns 
    """
    try:
        df = pd.read_csv(path, encoding="utf-8", on_bad_lines='skip')
    except Exception as e:
        raise ValueError(f"Error reading kaggle CVS {path}: {e}")
    if len(df) == 0:
        raise ValueError(f"CSV file is empty : {path}")
    df.columns = [c.lower().strip()for c in df.columns]
    text_col = None
    for c in ["email","text", "message", "body", "email_text", "content"]:
        if c in df.columns:
            text_col = c 
            break
    label_col = None
    for c in ["label","class", "phishing", "is_phishing", "spam", "target"]:
        if c in df.columns:
            label_col = c 
            break
    if text_col is None or label_col is None:
        print(f"available columns: {df.columns.tolist()}")
        raise ValueError(f"cannot find text or label column in {path}")
    df = df[[text_col, label_col]].copy()
    df.columns = ["text", "label"] 
    df = df.dropna(subset=["text","label"])
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df["label"] = df["label"].replace({
        "1": "phishing",
        "0": "legitimate",
        "phishing": "phishing",
        "legitimate": "legitimate",
        "ham": "legitimate",
        "spam": "phishing"
        "true": "phishing",
        "false": "legitimate",
        "yes": "phishing",
        "no": "legitimate"
    })
    
    valid_labels = {"phishing", "legitimate"}
    invalid_labels = set(df["label"].unique()) - valid_labels
    if invalid_labels:
        print(f"warning: found unexpcted label values:{ivalid_labels}")
        print(f"removing {len(df[~df['label'].isin(valid_labels)])} rows with invalid labels")
        df = df[df["label"].isin(valid_labels)]
    df["text"] = df["text"].apply(clean_text)
    df = df[df["text".str.len()>0]]
    df["source"] = "kaggle"
    return df
def main():
    """
    Main function to load, combine, balance, and save dataset
    """
    base = Path("data")
    output_dir = Path("output")
    output_dir.mkdir(exit_ok=True)
    print("="*60)
    print("PHISHING DETECTOR - DATA PREPARATION")
    print("="*60)
    print()
#load UCI sms dataset
    print("Loading UCI SMS dataset...")
    uci_path = base / "uci_sms" / "SMSSpamCollection"
    if not uci_path.exists():
        print(f" Warning: UCI SMS file not found at {uci_path}")
        print("Skipping UCI dataset...")
        df_uci = pd.DataFrame(columns=["text", "label", "source"])
    else:
        try:
            df_uci = load_uci_sms(uci_path)
            print(f" loaded {len(df_uci)} emails from UCI dataset")
        except Exception as e:
            print(f" Error loading UCI dataset: {e}")
            df_uci = pd.DataFrame(columns=["text", "label", "source"])
         #LOAD KAGGLE DATASET
    print("\nLoading Kaggle phishing dataset...")
    kaggle_dir = base / "kaggle_phishing"
    kaggle_files = list(kaggle_dir.glob("*.csv"))
if not kaggle_dir.exists():
    print(f" Error:kaggle directory not found: {kaggle_dir}")
    print("Please create the directory and add your kaggle dataset")
    return
if not kaggle_files:
    print(f" Error: No CSV files found in {kaggle_dir}")
    print("Please donwload and place kaggle dataset in this folder")
    return
#LOAD THE FIRST CSV FILE FOUND
print(f"Found {len(kaggle_files)} CSV file(s)")
print(f"Loading: {kaggle_file[0].name}")
try:
    df_kaggle =load_kaggle_csv(kaggle_files[0])
    print(f" Loaded{len(df_kaggle)} emails from kaggle dataset")
except Exception as e:
    print(f" Error loading kaggle dataset: {e}")
    return
#COMBINE DATASET
print("\nCombining datasets...")
df = pd.concat([df_uci, df_kaggle], ignore_index=True)
print(f"Total emails before balancing: {len(df)}")
print(f"Distribution before balancing:")
print(df["label"].value_counts())
print()
if "source" in df.columns:  
    print("Distribution by source:")
    print(df["source"].value_counts())
    print()
#BALANCE DATASET
print("Balancing dataset...")
phishing = df[df.label == "phishing"]
legit = df[df.label == "legitimate"]
print(f"Phishing emails:{len(phishing)}")
print(f"Legitimate emails: {len(legit)}")
n = min(len(phishing), len(legit))
print(f"Sampling {n} from each class...")
df_balanced = pd.concat([
    phishing.sample(n, random_state=42),
    legit.sample(n, random_state=42)
])      
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
#SAVE DATASET
output_file = output_dir / "emails_balanced.csv"
print(f"\nSaving to {output_file}...")
df_balanced.to_csv(output_file, index=False)
print(" Dataset created successfully!")
print()
#SUMMARY STATISTICS
print("="*60)
print("FINAL DATASET SUMMARY")
print("="*60)
print(f"Total emails: {len(df_balanced)}")
print(f"Label distribution:")
print(df_balanced["label"].value_counts())
print()
df_balanced["text_length"] = df_balanced["text"].str.split().str.len()
print("Text length statistics (words):")
print(f"  Mean:{df_balanced['text_length'].mean():.1f}")
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
    main()
        
>>>>>>> 13d69a23734bbe47eb1db6598bc86b5975a7a2ec
        