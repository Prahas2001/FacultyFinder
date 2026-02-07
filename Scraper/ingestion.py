import logging
import time
import sys
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- ROBUST IMPORT SETUP ---
# This ensures Python finds 'transformation' and 'faculty_db' 
# whether you run this script from the root folder or the subfolder.
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
# ---------------------------

# --- IMPORTS ---
import transformation 
import faculty_db as storage

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_driver():
    """Launches a visible Chrome Browser using Native Selenium Manager."""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--log-level=3')
    # Native Selenium 4.6+ manager (No external install needed)
    return webdriver.Chrome(options=options)

def smart_extract(driver, keywords):
    """
    Searches for headers/divs/spans containing specific keywords.
    """
    for key in keywords:
        try:
            # XPath: Find a header/div/span/strong containing the keyword
            xpath = f"//*[self::h2 or self::h3 or self::div or self::strong or self::span or self::p][contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key}')]"
            
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                # 1. Try Next Sibling (Common in Drupal)
                try:
                    content = el.find_element(By.XPATH, "./following-sibling::div")
                    text = content.text.strip()
                    if len(text) > 5: return text
                except: pass
                
                # 2. Try Parent Text
                try:
                    text = el.find_element(By.XPATH, "..").text.strip()
                    # If parent text is huge (entire body), skip it
                    if 20 < len(text) < 1000: return text
                except: pass
        except:
            continue
    return ""

def run_pipeline():
    storage.init_db()
    driver = get_driver()
    
    base_urls = [
        "https://www.daiict.ac.in/faculty",
        "https://www.daiict.ac.in/adjunct-faculty",
        "https://www.daiict.ac.in/adjunct-faculty-international",
        "https://www.daiict.ac.in/professor-practice",
        "https://www.daiict.ac.in/distinguished-professor"
    ]

    try:
        # --- PHASE A: HARVEST LINKS & BASIC DATA ---
        profiles_to_visit = []
        logging.info("PIPELINE STARTED: Harvesting Links...")
        
        for url in base_urls:
            logging.info(f"   Visiting: {url}")
            driver.get(url)
            try:
                WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.CLASS_NAME, "facultyInformation")))
            except:
                logging.warning(f"Could not load list on {url}")
                continue
            
            cards = driver.find_elements(By.CSS_SELECTOR, ".facultyInformation li")

            for card in cards:
                p = {"name": "Unknown", "url": None, "email": None, "designation": None, "specialization": ""}
                
                # 1. Name
                try: p["name"] = card.find_element(By.TAG_NAME, "h3").text
                except: pass
                
                # 2. Email
                try: p["email"] = card.find_element(By.CLASS_NAME, "facultyemail").text
                except: pass

                # 3. Designation
                try: p["designation"] = card.find_element(By.CLASS_NAME, "facultyEducation").text
                except: pass

                # 4. Specialization (FROM LISTING - The Safety Net)
                try: 
                    # Try specific class first
                    p["specialization"] = card.find_element(By.CLASS_NAME, "areaSpecialization").text
                except: 
                    # Try generic div search if class missing
                    try:
                        all_divs = card.find_elements(By.TAG_NAME, "div")
                        for div in all_divs:
                            if "Specialization" in div.text:
                                p["specialization"] = div.text.replace("Area of Specialization", "").strip()
                                break
                    except: pass

                # 5. Link
                try: 
                    link_elem = card.find_element(By.TAG_NAME, "a")
                    link = link_elem.get_attribute("href")
                    valid_keywords = ["faculty", "node", "professor", "distinguished", "adjunct"]
                    if link and any(k in link for k in valid_keywords):
                        p["url"] = link
                except: pass
                
                profiles_to_visit.append(p)

        # --- PHASE B: DEEP SCRAPE ---
        linked_profiles = [p for p in profiles_to_visit if p['url']]
        logging.info(f"Found {len(linked_profiles)} profiles. Starting Deep Scrape...")

        for index, person in enumerate(linked_profiles):
            logging.info(f"   [{index+1}/{len(linked_profiles)}] {person['name']}...")
            try:
                driver.get(person['url'])
                time.sleep(1.2) 

                # 1. BIOGRAPHY
                bio_els = driver.find_elements(By.CSS_SELECTOR, ".field--name-field-biography, .about")
                if bio_els: raw_bio = bio_els[0].text
                else: raw_bio = smart_extract(driver, ["biography", "about"])

                # 2. RESEARCH
                res_els = driver.find_elements(By.CSS_SELECTOR, ".work-exp1, .field--name-field-research-interests")
                if res_els: raw_research = res_els[0].text
                else: raw_research = smart_extract(driver, ["research", "interest"])
                
                # Filter bad research grabs (like menu tabs)
                if "Research Overview" in raw_research and len(raw_research) < 50:
                    raw_research = ""

                # 3. TEACHING
                teach_els = driver.find_elements(By.CSS_SELECTOR, ".field--name-field-courses-taught, .field--name-field-teaching")
                if teach_els: raw_teach = teach_els[0].text
                else: raw_teach = smart_extract(driver, ["teaching", "courses"])

                # 4. PUBLICATIONS
                pub_els = driver.find_elements(By.CSS_SELECTOR, ".education.overflowContent ul.bulletText li")
                if pub_els: raw_pubs = [li.text for li in pub_els]
                else: 
                    raw_pubs_text = smart_extract(driver, ["publication"])
                    raw_pubs = [raw_pubs_text] if raw_pubs_text else []

                # 5. SPECIALIZATION (Merge Strategy)
                # Start with what we found on the Listing Page
                final_spec = person.get("specialization", "")
                
                # Check Profile Page
                spec_els = driver.find_elements(By.CSS_SELECTOR, ".field--name-field-area-of-specialization")
                if spec_els: 
                    deep_spec = spec_els[0].text
                    # Only overwrite if deep data is better/longer
                    if len(deep_spec) > len(final_spec):
                        final_spec = deep_spec
                else:
                    deep_spec = smart_extract(driver, ["specialization"])
                    if deep_spec and len(deep_spec) > len(final_spec):
                        final_spec = deep_spec

                person.update({
                    "bio": raw_bio,
                    "research": raw_research,
                    "publications": raw_pubs,
                    "teaching": raw_teach,
                    "specialization": final_spec
                })

                cleaned_data = transformation.clean_profile(person)
                storage.save_profile(cleaned_data)

            except Exception as e:
                logging.warning(f"Error on {person['name']}: {e}")

        logging.info("PIPELINE FINISHED.")
        storage.export_to_files()

    finally:
        driver.quit()

if __name__ == "__main__":
    run_pipeline()
    