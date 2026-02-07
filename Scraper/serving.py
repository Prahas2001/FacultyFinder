from fastapi import FastAPI, HTTPException
import sys
from pathlib import Path

# --- ROBUST IMPORT SETUP ---
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
sys.path.append(str(CURRENT_DIR))
sys.path.append(str(ROOT_DIR))

# --- IMPORTS ---
import faculty_db as storage 
from Recommender.chat_engine import chat_with_faculty 

app = FastAPI(title="DA-IICT Faculty AI", description="Hybrid Search: SQL + RAG AI")

@app.get("/")
def home():
    return {
        "status": "Active", 
        "endpoints": [
            "/faculty (List all)", 
            "/faculty/search?q=AI (Keyword Search)",
            "/recommend?q=Deep Learning (AI Analysis)"
        ]
    }

@app.get("/faculty")
def get_all():
    """Return the entire dataset (SQL Source)."""
    return storage.get_all_faculty()

@app.get("/faculty/search")
def search(q: str):
    """
    Legacy SQL Search.
    Finds exact text matches (e.g., 'Mishra' finds 'Biswajit Mishra').
    """
    results = storage.search_faculty(q)
    if not results:
        raise HTTPException(status_code=404, detail="No matches found.")
    return results

@app.get("/recommend")
def recommend(q: str):
    """
    Smart RAG Search.
    Uses Gemini AI to explain WHY professors are a match.
    """
    # Call your Self-Healing AI Engine
    response_text = chat_with_faculty(q)
    
    # Simple error check to pass 404s correctly
    if "couldn't find" in response_text and "Error" in response_text:
         raise HTTPException(status_code=404, detail="No matches found.")
    
    return {
        "query": q, 
        "ai_response": response_text
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)