import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import urllib.parse
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
# Ensure ref directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ref')))
try:
    from build_skill_database import extract_skills
except Exception:
    def extract_skills(text):
        return ["python", "giao tiếp", "tiếng anh"] # fallback
        return ["python", "giao tiếp", "tiếng anh"] # fallback

def clean_text(text):
    if not text: return ""
    return "\n".join([line.strip() for line in text.split('\n') if line.strip()])

def scrape_jobs():
    base_url = "https://jobs.neu.edu.vn"
    keywords = ["Data Analyst", "Marketing", "Nhân viên kinh doanh", "HR", "Kế toán"]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    all_jobs = []
    
    for kw in keywords:
        print(f"Scraping keyword: {kw}")
        encoded_kw = urllib.parse.quote_plus(kw)
        page_url = f"{base_url}/jobs?titleJob={encoded_kw}&categoryJob=&companyName=&page=1"
        
        try:
            resp = requests.get(page_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            job_cards = soup.find_all('div', class_='twm-jobs-grid-style1')
            print(f"  Found {len(job_cards)} jobs on page 1 for {kw}")
            
            for card in job_cards:
                title_elem = card.find('a', class_='twm-job-title')
                title = title_elem.find('h4').text.strip() if title_elem and title_elem.find('h4') else "N/A"
                
                company_elem = card.find('a', class_='twm-job-websites')
                company = company_elem.text.strip() if company_elem else "N/A"
                
                salary_elem = card.find('div', class_='twm-right-content')
                salary = salary_elem.text.strip() if salary_elem else "Thỏa thuận"
                
                link = ""
                if title_elem and 'href' in title_elem.attrs:
                    link = title_elem['href']
                    if link.startswith('/'):
                        link = base_url + link
                
                if link and title != "N/A":
                    # Fetch JD
                    try:
                        jd_resp = requests.get(link, headers=headers, timeout=10)
                        jd_soup = BeautifulSoup(jd_resp.text, 'html.parser')
                        jd_container = jd_soup.find('div', class_='cabdidate-de-info')
                        
                        jd_text = ""
                        if jd_container:
                            jd_elem = jd_container.find('div', class_='content')
                            if jd_elem:
                                jd_text = clean_text(jd_elem.get_text(separator='\n'))
                        else:
                            jd_elem = jd_soup.find('div', class_='content')
                            if jd_elem:
                                jd_text = clean_text(jd_elem.get_text(separator='\n'))
                                
                        if not jd_text or len(jd_text) < 50:
                            print(f"  -> Skipping {title} (No JD text found)")
                            continue
                            
                        print(f"  -> Extracted JD for {title}")
                        
                        # Use build_skill_database logic to extract skills!
                        skills = extract_skills(jd_text)
                        
                        # Determine family
                        family = "Other"
                        if "data" in kw.lower() or "phân tích" in title.lower() or "data" in title.lower():
                            family = "Data/Business Analysis"
                        elif "marketing" in kw.lower() or "seo" in title.lower():
                            family = "Marketing"
                        elif "kinh doanh" in kw.lower() or "sale" in title.lower():
                            family = "Business Development"
                        elif "hr" in kw.lower() or "nhân sự" in title.lower():
                            family = "HR"
                        elif "kế toán" in kw.lower() or "tài chính" in title.lower():
                            family = "Finance"
                            
                        all_jobs.append({
                            "Job_Title": title,
                            "Company": company,
                            "Salary_Range": salary,
                            "URL": link,
                            "JD_Text": jd_text,
                            "Skills": ",".join(skills),
                            "Job_Family": family,
                            "Location": "Hà Nội" # Defaulting for now
                        })
                    except Exception as e:
                        print(f"  -> Error fetching JD for {title}: {e}")
        except Exception as e:
            print(f"Error fetching list page for {kw}: {e}")
            
    # Save to processed directly
    os.makedirs("data/processed", exist_ok=True)
    df = pd.DataFrame(all_jobs)
    # Deduplicate
    df.drop_duplicates(subset=["Job_Title", "Company"], inplace=True)
    
    out_csv = "data/processed/neu_jobs_clean.csv"
    df.to_csv(out_csv, index=False, encoding='utf-8')
    print(f"\nSaved {len(df)} jobs with full JD to {out_csv}")

if __name__ == "__main__":
    scrape_jobs()
