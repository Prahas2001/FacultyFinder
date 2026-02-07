# FacultyFinder: DA-IICT Faculty Data Pipeline

## Project Overview
**FacultyFinder** is a robust Data Engineering pipeline designed to harvest, clean, validate, and serve faculty profiles from the DA-IICT website.

This project utilizes a **Pure Selenium scraping engine** to handle dynamic content rendering and extraction. Unlike hybrid approaches, this system uses Selenium's native `XPath` and `CSS Selectors` to navigate the DOM directly, consolidating data from multiple directories into a unified schema. The system includes a modular transformation layer, a data health analysis suite, and a FastAPI serving layer for downstream applications.

## Key Features
* **Selenium-Native Extraction:** Uses a headless browser for both navigation and data extraction (XPath/CSS), eliminating the need for external HTML parsers.
* **Smart Traversal:** Handles varying HTML structures across Faculty, Adjunct, and Distinguished Professor pages using adaptive locators.
* **Modular Architecture:** Splits responsibilities into ingestion, transformation, database management, and analysis.
* **Data Health & Analysis:** Includes a standalone script (`analysis.py`) to generate statistical reports on data quality.
* **Multi-Format Storage:** Persists data to **SQLite** (`faculty.db`), **JSON** (`final_faculty_data.json`), and **CSV** (`final_faculty_data.csv`) for maximum compatibility.
* **REST API:** A high-performance `FastAPI` server (`serving.py`) that exposes the curated dataset.

## Tech Stack
* **Language:** Python 3.10+
* **Web Scraping:** `Selenium` (WebDriver & Extraction)
* **Data Processing:** `Pandas`, `NumPy`
* **Database:** `SQLite3`
* **API Framework:** `FastAPI`, `Uvicorn`

---

## Setup & Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/faculty-assignment.git](https://github.com/YOUR_USERNAME/faculty-assignment.git)
    cd faculty-assignment
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---

## Workflow & Usage

### Step 1: Ingestion (Scrape & Transform)
Run the main ingestion script. This launches the Selenium driver, scrapes the target pages, applies transformations, and saves the data.
```bash
python ingestion.py
```
* **Process:** Scrapes (Selenium) -> Cleans (via transformation.py) -> Saves to DB (via faculty_db.py) -> Exports CSV/JSON.

* **Output:** faculty.db, final_faculty_data.json, final_faculty_data.csv.

### Step 2: Quality Assurance (Data Analysis)
Run the analysis script to verify data integrity and view distribution metrics.
```bash
python analysis.py
```
* **Action:** Loads the generated data and prints a health report (null counts, unique values, data types) to the console.

### Step 3: Serving (Start API)
Launch the FastAPI server to expose the validated data.
```bash
uvicorn serving:app --reload
```
* **Action:** Loads `final_faculty_data.json` into memory and starts a local web server.
* **Output:** Server starts at http://127.0.0.1:8000.

### Step 4: Verification
Open your web browser and navigate to the interactive API documentation to test the system.
* **Link:** http://127.0.0.1:8000/docs

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | **Health Check.** Returns API status and total record count. |
| `GET` | `/faculty/all` | **Bulk Fetch.** Returns the complete dataset. (Used for vector embedding generation). |
| `GET` | `/faculty/search` | **Search.** specific faculty profiles based on query parameters. |

---

## Project Structure
```
FacultyFinder/
├── ingestion.py             # Main entry point: Selenium extraction logic
├── transformation.py        # Logic: Data cleaning, email sanitization, text normalization
├── faculty_db.py            # Logic: Database connection, schema creation, & CRUD ops
├── analysis.py              # Logic: Generates data health checks & statistical summaries
├── serving.py               # API: FastAPI application to serve the cleaned data
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
├── faculty.db               # (Output) SQLite database containing structured profiles
├── final_faculty_data.json  # (Output) JSON artifact for web portability
├── final_faculty_data.csv   # (Output) CSV artifact for data analysis/Excel
```

## Dataset Statistics & Analysis


| Attribute | Value |
| :--- | :--- |
| **Total Observations** | 112 |
| **Total Columns** | 10 |
| **Data Types** | `int64` (1), `object` (9) |
| **Memory Usage** | 8.9+ KB |

---

### Column Schema & Completeness

| # | Column Name | Non-Null Count | Data Type | Status |
| :-- | :--- | :--- | :--- | :--- |
| 0 | **id** | 112 | `int64` | Full |
| 1 | **name** | 112 | `object` | Full |
| 2 | **designation** | 110 | `object` | Minor Missing |
| 3 | **email** | 112 | `object` | Full |
| 4 | **bio** | 72 | `object` | High Missing |
| 5 | **research** | 112 | `object` | Full |
| 6 | **publications** | 63 | `object` | High Missing |
| 7 | **teaching** | 72 | `object` | High Missing |
| 8 | **specialization** | 109 | `object` | Minor Missing |
| 9 | **profile_url** | 112 | `object` | Full |

---

### MISSING DATA BREAKDOWN

| Column | Missing (NaN) | Empty String | Total Empty | % Complete |
| :--- | :--- | :--- | :--- | :--- |
| **id** | 0 | 0 | 0 | **100.0%** |
| **name** | 0 | 0 | 0 | **100.0%** |
| **designation** | 2 | 0 | 2 | **98.2%** |
| **email** | 0 | 0 | 0 | **100.0%** |
| **bio** | 40 | 0 | 40 | **64.3%** |
| **research** | 0 | 0 | 0 | **100.0%** |
| **publications** | 49 | 0 | 49 | **56.2%** |
| **teaching** | 40 | 0 | 40 | **64.3%** |
| **specialization** | 3 | 0 | 3 | **97.3%** |
| **profile_url** | 0 | 0 | 0 | **100.0%** |
