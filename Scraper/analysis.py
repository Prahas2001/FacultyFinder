import pandas as pd
import os
import sys
from pathlib import Path

# --- ROBUST PATH SETUP ---
# 1. Get the directory where THIS script is located
BASE_DIR = Path(__file__).resolve().parent

# 2. Define the path to the CSV file relative to this script
CSV_FILE = BASE_DIR / "final_faculty_data.csv"
# -------------------------

def analyze_data():
    # 1. Check if file exists
    if not CSV_FILE.exists():
        print(f"Error: '{CSV_FILE}' not found. Run 'ingestion.py' first.")
        return

    # 2. Load Data
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"Successfully loaded {len(df)} records from {CSV_FILE.name}\n")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 3. Overall Health Check
    print("="*40)
    print(" DATA HEALTH REPORT")
    print("="*40)
    print(df.info())
    print("\n")

    # 4. Missing Value Analysis (NaN vs Empty Strings)
    print("="*40)
    print(" MISSING DATA BREAKDOWN")
    print("="*40)
    print(f"{'Column':<20} | {'Missing (NaN)':<15} | {'Empty String':<15} | {'Total Empty':<15} | {'% Complete':<15}")
    print("-" * 90)

    for col in df.columns:
        # Count actual NaNs
        nan_count = df[col].isnull().sum()
        
        # Count empty strings (often happens in scraping)
        empty_str_count = 0
        if df[col].dtype == object:
            empty_str_count = (df[col].astype(str).str.strip() == '').sum()
            # Note: Pandas sometimes reads empty CSV cells as NaN, so we handle both
        
        total_empty = nan_count + empty_str_count
        completeness = 100 - ((total_empty / len(df)) * 100)
        
        print(f"{col:<20} | {nan_count:<15} | {empty_str_count:<15} | {total_empty:<15} | {completeness:.1f}%")

    # 5. Content Sampling (Quality Check)
    print("\n" + "="*40)
    print("CONTENT SAMPLING (First 3 Valid Entries)")
    print("="*40)
    
    columns_to_check = ['specialization', 'teaching', 'bio', 'research']
    
    for col in columns_to_check:
        if col in df.columns:
            print(f"\n--- Sample Data for: {col.upper()} ---")
            # Get first 3 non-empty values
            valid_samples = df[df[col].notna() & (df[col].astype(str).str.strip() != '')][col].head(3)
            
            if len(valid_samples) > 0:
                for i, text in enumerate(valid_samples, 1):
                    # Truncate long text for display
                    display_text = (text[:90] + '...') if len(str(text)) > 90 else text
                    print(f"{i}. {display_text}")
            else:
                print("   (No data found in this column)")

    # 6. Duplicate Check
    print("\n" + "="*40)
    print(" 👯 DUPLICATE CHECK")
    print("="*40)
    if 'profile_url' in df.columns:
        dupes = df.duplicated(subset=['profile_url']).sum()
        if dupes == 0:
            print("No duplicate profiles found.")
        else:
            print(f"Found {dupes} duplicate profiles based on URL.")

if __name__ == "__main__":
    analyze_data()