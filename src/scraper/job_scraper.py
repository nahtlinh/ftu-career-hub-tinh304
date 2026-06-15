import time
import random
import re
import sys
import urllib.parse
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

KEYWORDS = [
    "Data Analyst", "Data Analysis", "Phân tích dữ liệu", "Chuyên viên dữ liệu", 
    "Data Scientist", "Khai phá dữ liệu",
    "Business Analyst", "Business Analysis", "Phân tích nghiệp vụ", 
    "Phân tích kinh doanh", "Chuyên viên BA", 
    "Marketing", "Tiếp thị", "Truyền thông", "Digital Marketing", 
    "Content Creator", "Quản trị thương hiệu", "SEO",
    "Business Development", "Phát triển kinh doanh", "Phát triển thị trường",
    "Sales", "Kinh doanh", "Nhân viên kinh doanh", "Quản lý tài khoản", "Account Executive"
]

def map_job_family(job_title):
    title_lower = job_title.lower()
    
    data_ba_keywords = ["data", "phân tích dữ liệu", "chuyên viên dữ liệu", "khai phá dữ liệu", "business analyst", "phân tích nghiệp vụ", "phân tích kinh doanh", "ba", "chuyên viên ba"]
    marketing_keywords = ["marketing", "tiếp thị", "truyền thông", "digital marketing", "content creator", "quản trị thương hiệu", "seo"]
    sales_keywords = ["business development", "phát triển kinh doanh", "phát triển thị trường", "sales", "kinh doanh", "nhân viên kinh doanh", "quản lý tài khoản", "account executive", "account"]
    
    for kw in data_ba_keywords:
        if kw in title_lower:
            return "Data/Business Analysis"
    for kw in marketing_keywords:
        if kw in title_lower:
            return "Marketing"
    for kw in sales_keywords:
        if kw in title_lower:
            return "Business Development"
            
    return "Other"

def extract_jobs_from_page(page, get_jd=False):
    """
    Extracts all jobs on the current list page.
    If get_jd is True, it will visit each job link to get JD_Text.
    """
    jobs = []
    
    # NEU jobs list on search page uses .twm-jobs-grid-style1
    try:
        page.wait_for_selector('.twm-jobs-grid-style1', timeout=5000)
    except:
        return jobs  # No jobs found on this page
        
    job_elements = page.query_selector_all('.twm-jobs-grid-style1')
    
    # We will collect job urls and basic info first to avoid stale elements if we navigate away
    job_links = []
    for el in job_elements:
        try:
            # Title element
            title_el = el.query_selector('a.twm-job-title h4')
            title = title_el.inner_text().strip() if title_el else "Unknown"
            
            # Company element
            company_el = el.query_selector('a.twm-job-websites') or el.query_selector('.twm-job-com-name')
            company = company_el.inner_text().strip() if company_el else "Unknown"
            
            # Salary element
            salary_el = el.query_selector('.twm-right-content') or el.query_selector('.twm-jobs-amount')
            salary_range = salary_el.inner_text().strip() if salary_el else "Thoả thuận"
            
            # Location/Address
            address_el = el.query_selector('.twm-job-address')
            location = address_el.inner_text().strip() if address_el else "Unknown"
            
            # Level/Type is in .twm-bg-green
            level = "Unknown"
            level_el = el.query_selector('.twm-bg-green')
            if level_el:
                level = level_el.inner_text().strip()
                
            industry = "Unknown"
            
            # Logo URL
            logo_el = el.query_selector('img')
            logo_url = logo_el.get_attribute('src') if logo_el else ""
            if logo_url and not logo_url.startswith('http'):
                logo_url = "https://jobs.neu.edu.vn" + logo_url
                
            # Job Link
            link_el = el.query_selector('a.twm-job-title')
            href = link_el.get_attribute('href') if link_el else None
            if href and not href.startswith('http'):
                href = "https://jobs.neu.edu.vn" + href
                
            job_links.append({
                "Job Title": title,
                "Company": company,
                "Salary_Range": salary_range,
                "Industry": industry,
                "Level": level,
                "Job_Family": map_job_family(title),
                "Location": location,
                "URL": href,
                "Logo_URL": logo_url,
                "JD_Text": ""  # To be filled if get_jd is True
            })
        except Exception as e:
            print(f"[Warning] Error extracting basic job info: {e}")
            continue

    if get_jd:
        for job in job_links:
            if not job['URL']:
                continue
            try:
                time.sleep(random.uniform(2, 4))  # Anti-bot delay
                print(f"    -> Extracting JD: {job['Job Title']}")
                page.goto(job['URL'], timeout=15000)
                
                # Wait for JD content
                try:
                    page.wait_for_selector('.cabdidate-de-info .content', timeout=5000)
                    jd_el = page.query_selector('.cabdidate-de-info .content')
                except:
                    # Fallback
                    try:
                        page.wait_for_selector('.content', timeout=5000)
                        jd_el = page.query_selector('.content')
                    except:
                        jd_el = page.query_selector('.twm-job-detail-2-wrap')

                if jd_el:
                    job['JD_Text'] = jd_el.inner_text().strip()
            except Exception as e:
                print(f"[Warning] Failed to extract JD for {job['Job Title']}: {e}")
    
    return job_links

def crawl_neu_jobs():
    all_jobs = []
    
    print("[INFO] Starting Playwright Scraper...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        for keyword in KEYWORDS:
            print(f"\n[INFO] Searching for keyword: '{keyword}'")
            # Pagination loop
            page_num = 1
            while True:
                print(f"  -> Scraping Page {page_num}...")
                url = f"https://jobs.neu.edu.vn/jobs?titleJob={urllib.parse.quote_plus(keyword)}&page={page_num}"
                try:
                    page.goto(url, timeout=20000)
                except Exception as e:
                    print(f"[ERROR] Failed to load page {url}: {e}")
                    break
                
                # Check if there's any job on this page
                try:
                    page.wait_for_selector('.twm-jobs-grid-style1', timeout=5000)
                except:
                    print(f"  -> No more jobs found on page {page_num}. Moving to next keyword.")
                    break
                    
                # User wants JD only for first 3 pages
                get_jd = True if page_num <= 3 else False
                
                jobs_on_page = extract_jobs_from_page(page, get_jd=get_jd)
                
                if not jobs_on_page:
                    print(f"  -> Extracted 0 jobs. Ending pagination for '{keyword}'.")
                    break
                    
                all_jobs.extend(jobs_on_page)
                print(f"  -> Found {len(jobs_on_page)} jobs.")
                
                # Check for 'Next' pagination button
                # Usually NEU jobs uses standard laravel pagination
                next_btn = page.query_selector('a[rel="next"]')
                if not next_btn:
                    print(f"  -> No 'Next' button found. Ending pagination for '{keyword}'.")
                    break
                    
                page_num += 1
                time.sleep(random.uniform(1, 3))
                
        browser.close()
        
    print(f"\n[INFO] Crawl completed. Total jobs collected: {len(all_jobs)}")
    return all_jobs

if __name__ == "__main__":
    crawl_neu_jobs()
