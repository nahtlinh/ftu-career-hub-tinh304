import time
import urllib.parse
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def scrape_neu_jobs(keyword, num_pages=2):
    """
    Scrapes job listings from jobs.neu.edu.vn using Selenium and BeautifulSoup.
    """
    # Setup Chrome Options
    chrome_options = Options()
    # Add a User-Agent to prevent bot blocking
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Optional: run in headless mode if you don't want the browser UI to pop up
    # chrome_options.add_argument("--headless") 

    # Initialize WebDriver
    # Note: make sure chromedriver is installed/configured in your environment
    driver = webdriver.Chrome(options=chrome_options)
    
    # URL-encode the keyword (e.g., "Data Analyst" -> "Data+Analyst")
    encoded_keyword = urllib.parse.quote_plus(keyword)
    
    all_jobs_data = []

    try:
        for page in range(1, num_pages + 1):
            url = f"https://jobs.neu.edu.vn/jobs?titleJob={encoded_keyword}&categoryJob=&companyName=&page={page}"
            print(f"Scraping page {page}: {url}")
            
            driver.get(url)
            
            # Wait for 5 seconds to ensure JavaScript has fully rendered the job list
            time.sleep(5) 
            
            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find all job cards
            job_cards = soup.find_all('div', class_='twm-jobs-grid-style1')
            
            for card in job_cards:
                # 1. Extract Job Title
                try:
                    job_title_elem = card.find('a', class_='twm-job-title')
                    job_title = job_title_elem.find('h4').text.strip() if job_title_elem and job_title_elem.find('h4') else "N/A"
                except Exception:
                    job_title = "N/A"
                    
                # 2. Extract Company Name
                try:
                    # Note: The provided HTML snippet uses twm-job-websites for the company website.
                    # We will try to extract it from there, as it might be the closest identifier in this block.
                    company_name_elem = card.find('a', class_='twm-job-websites')
                    company_name = company_name_elem.text.strip() if company_name_elem else "N/A"
                except Exception:
                    company_name = "N/A"
                    
                # 3. Extract Salary
                try:
                    # Note: Salary is not explicitly in the snippet, but might be inside twm-right-content.
                    salary_elem = card.find('div', class_='twm-right-content')
                    salary = salary_elem.text.strip() if salary_elem and salary_elem.text.strip() else "N/A"
                except Exception:
                    salary = "N/A"
                    
                # 4. Extract Job Link
                try:
                    link_elem = card.find('a', class_='twm-job-title')
                    if link_elem and 'href' in link_elem.attrs:
                        href = link_elem['href']
                        # Prepend base URL if it's a relative link
                        job_link = f"https://jobs.neu.edu.vn{href}" if href.startswith('/') else href
                    else:
                        job_link = "N/A"
                except Exception:
                    job_link = "N/A"
                    
                all_jobs_data.append({
                    'Job_Title': job_title,
                    'Company_Name': company_name,
                    'Salary': salary,
                    'Job_Link': job_link,
                    'Job_Description': "N/A"
                })
                
        # Loop through the collected job links to extract Job Descriptions
        print(f"\nFetching Job Descriptions for {len(all_jobs_data)} jobs...")
        for i, job in enumerate(all_jobs_data, 1):
            if job['Job_Link'] != "N/A":
                print(f"[{i}/{len(all_jobs_data)}] Fetching JD: {job['Job_Link']}")
                try:
                    driver.get(job['Job_Link'])
                    time.sleep(3) # Wait for JD page to load
                    jd_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Extracted from user's HTML snippet
                    jd_container = jd_soup.find('div', class_='cabdidate-de-info')
                    if jd_container:
                        jd_elem = jd_container.find('div', class_='content')
                    else:
                        jd_elem = jd_soup.find('div', class_='content')
                    
                    if jd_elem:
                        job['Job_Description'] = jd_elem.text.strip()
                    else:
                        job['Job_Description'] = "Could not locate JD container"
                except Exception as e:
                    print(f"Error fetching JD for {job['Job_Link']}: {e}")
                    job['Job_Description'] = "Error extracting JD"

    finally:
        # Always make sure to quit the driver
        driver.quit()
        
    # Save to CSV using pandas
    df = pd.DataFrame(all_jobs_data)
    output_file = "neu_jobs_raw.csv"
    
    # Using utf-8-sig encoding for proper Vietnamese character rendering in Excel
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nScraping completed. Extracted {len(all_jobs_data)} jobs.")
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    # Example usage
    search_keyword = "Data Analyst"
    scrape_neu_jobs(keyword=search_keyword, num_pages=2)
