import csv
import json
import os
import requests
from bs4 import BeautifulSoup

def scrape_affiliate_courses():
    csv_path = os.path.join("data", "raw", "extra_course.csv")
    out_path = os.path.join("web", "data", "affiliate_courses.json")
    
    if not os.path.exists(csv_path):
        print(f"[ERROR] Cannot find {csv_path}")
        return
        
    print(f"[INFO] Reading affiliate URLs from {csv_path}")
    courses = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row['URL'].strip()
            center = row['Center'].strip()
            category = row['Category'].strip()
            
            print(f" -> Scraping: {url}")
            try:
                # Basic bot request
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string.strip() if soup.title else "Khóa học chưa rõ tên"
                    courses.append({
                        "title": title,
                        "provider": center,
                        "category": category,
                        "url": url
                    })
                    print(f"    [Success] Found title: {title}")
                else:
                    print(f"    [Failed] Status code {response.status_code}")
                    courses.append({
                        "title": f"Khóa học {category} ({center})",
                        "provider": center,
                        "category": category,
                        "url": url
                    })
            except Exception as e:
                print(f"    [Error] {e}")
                courses.append({
                    "title": f"Khóa học {category} ({center})",
                    "provider": center,
                    "category": category,
                    "url": url
                })
                
    # Save to web/data for the frontend to use
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(courses, f, ensure_ascii=False, indent=4)
        
    print(f"[INFO] Successfully exported {len(courses)} courses to {out_path}")

if __name__ == "__main__":
    scrape_affiliate_courses()
