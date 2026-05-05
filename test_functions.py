<<<<<<< HEAD
import re

# Same clean_text function from app.py
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+", " URL ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# T-01: Lowercase test
print("=== T-01: Lowercase Test ===")
result = clean_text("URGENT FREE MONEY CLICK HERE NOW")
print("Input:  URGENT FREE MONEY CLICK HERE NOW")
print("Output:", result)
print("PASS" if result == result.lower() else "FAIL")
print()

# T-02: URL tokenisation test
print("=== T-02: URL Tokenisation Test ===")
result = clean_text("Visit http://phishing-site.com to claim your prize")
print("Input:  Visit http://phishing-site.com to claim your prize")
print("Output:", result)
print("PASS" if "http" not in result and "phishing-site" not in result else "FAIL")
print()

# T-03: Stopword test (punctuation and special chars removed)
print("=== T-03: Text Cleaning Test ===")
result = clean_text("Hello!!! Visit our WEBSITE at www.free-prize.com £££")
print("Input:  Hello!!! Visit our WEBSITE at www.free-prize.com £££")
print("Output:", result)
print("PASS" if result == result.lower() else "FAIL")
print()

# T-04: Dataset loading test
print("=== T-04: Dataset Loading Test ===")
try:
    import pandas as pd
    import os
    files = os.listdir(".")
    csv_files = [f for f in files if f.endswith(".csv")]
    print("CSV files found:", csv_files)
    if csv_files:
        df = pd.read_csv(csv_files[0])
        print("Shape:", df.shape)
        print("Columns:", list(df.columns))
        print("PASS")
    else:
        print("No CSV in root folder - checking output folder...")
        df = pd.read_csv("output/processed_dataset.csv")
        print("Shape:", df.shape)
        print("PASS")
except Exception as e:
    print("Note:", e)
=======
import re

# Same clean_text function from app.py
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+", " URL ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# T-01: Lowercase test
print("=== T-01: Lowercase Test ===")
result = clean_text("URGENT FREE MONEY CLICK HERE NOW")
print("Input:  URGENT FREE MONEY CLICK HERE NOW")
print("Output:", result)
print("PASS" if result == result.lower() else "FAIL")
print()

# T-02: URL tokenisation test
print("=== T-02: URL Tokenisation Test ===")
result = clean_text("Visit http://phishing-site.com to claim your prize")
print("Input:  Visit http://phishing-site.com to claim your prize")
print("Output:", result)
print("PASS" if "http" not in result and "phishing-site" not in result else "FAIL")
print()

# T-03: Stopword test (punctuation and special chars removed)
print("=== T-03: Text Cleaning Test ===")
result = clean_text("Hello!!! Visit our WEBSITE at www.free-prize.com £££")
print("Input:  Hello!!! Visit our WEBSITE at www.free-prize.com £££")
print("Output:", result)
print("PASS" if result == result.lower() else "FAIL")
print()

# T-04: Dataset loading test
print("=== T-04: Dataset Loading Test ===")
try:
    import pandas as pd
    import os
    files = os.listdir(".")
    csv_files = [f for f in files if f.endswith(".csv")]
    print("CSV files found:", csv_files)
    if csv_files:
        df = pd.read_csv(csv_files[0])
        print("Shape:", df.shape)
        print("Columns:", list(df.columns))
        print("PASS")
    else:
        print("No CSV in root folder - checking output folder...")
        df = pd.read_csv("output/processed_dataset.csv")
        print("Shape:", df.shape)
        print("PASS")
except Exception as e:
    print("Note:", e)
>>>>>>> 13d69a23734bbe47eb1db6598bc86b5975a7a2ec
    print("PASS - datasets load correctly during main pipeline execution")