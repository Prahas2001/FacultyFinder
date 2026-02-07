import sqlite3
import logging
import pandas as pd
import os
from pathlib import Path

# --- DYNAMIC PATH SETUP ---
# 1. Get the directory where THIS script is located (Scraper folder)
BASE_DIR = Path(__file__).resolve().parent

# 2. Define the subfolder for data
DATA_DIR = BASE_DIR / "Scraped_data"

# 3. Create the folder if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 4. Define Full Paths (Use these in your functions!)
DB_PATH = DATA_DIR / "faculty.db"
CSV_PATH = DATA_DIR / "final_faculty_data.csv"
JSON_PATH = DATA_DIR / "final_faculty_data.json"

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# --------------------------

def get_db_connection():
    """Helper to get a connection using the FULL PATH."""
    # Use DB_PATH, not "faculty.db"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates the table schema."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faculty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                designation TEXT,
                email TEXT,
                bio TEXT,
                research TEXT,
                publications TEXT,
                teaching TEXT,
                specialization TEXT,
                profile_url TEXT UNIQUE
            )
        ''')
        conn.commit()
        conn.close()
        logging.info(f"Storage Layer Initialized at: {DB_PATH}")
    except Exception as e:
        logging.error(f"Database Initialization Failed: {e}")

def save_profile(data: dict):
    """Upsert: Insert new or Update existing."""
    try:
        conn = get_db_connection() # Uses DB_PATH internally
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO faculty 
            (name, designation, email, bio, research, publications, teaching, specialization, profile_url)
            VALUES (:name, :designation, :email, :bio, :research, :publications, :teaching, :specialization, :url)
            ON CONFLICT(profile_url) DO UPDATE SET
                bio=excluded.bio,
                research=excluded.research,
                publications=excluded.publications,
                teaching=excluded.teaching,
                specialization=excluded.specialization,
                email=excluded.email
        ''', data)
        
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Storage Error: {e}")

def export_to_files():
    """Exports DB data to CSV and JSON in the Scraped_data folder."""
    try:
        conn = get_db_connection() # Uses DB_PATH
        df = pd.read_sql_query("SELECT * FROM faculty", conn)
        conn.close()
        
        # Save to files using the FULL PATHS
        df.to_csv(CSV_PATH, index=False)
        df.to_json(JSON_PATH, orient="records", indent=4)
        logging.info(f"Data exported to:\n - {CSV_PATH}\n - {JSON_PATH}")
    except Exception as e:
        logging.error(f"Export failed: {e}")

def get_all_faculty():
    """Retrieves all faculty records."""
    conn = get_db_connection() # Uses DB_PATH
    rows = conn.execute("SELECT * FROM faculty").fetchall()
    conn.close()
    return rows

def search_faculty(query: str):
    """Simple SQL-based search."""
    conn = get_db_connection() # Uses DB_PATH
    wildcard = f"%{query}%"
    rows = conn.execute("""
        SELECT * FROM faculty 
        WHERE name LIKE ? OR bio LIKE ? OR research LIKE ?
    """, (wildcard, wildcard, wildcard)).fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()