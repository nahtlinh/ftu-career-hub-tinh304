import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def clean_course_name(name):
    # Remove redundant spaces and newlines
    return re.sub(r'\s+', ' ', name).strip()

def extract_course_name_from_url(url):
    parts = [p for p in url.strip('/').split('/') if p]
    if parts:
        last_part = parts[-1]
        name = last_part.replace('-', ' ').title()
        return name
    return "Khóa học chuyên sâu"

def scrape_training_centers(input_csv, output_csv):
    try:
        df_urls = pd.read_csv(input_csv, header=None)
        urls = df_urls[1].dropna().tolist()
    except Exception as e:
        print(f"Lỗi khi đọc file {input_csv}: {e}")
        return

    # Mappings để dò kỹ năng
    skill_keywords = {
        'sql': 'SQL',
        'python': 'Python',
        'data': 'Data Analysis',
        'powerbi': 'Data Analysis',
        'marketing': 'Digital Marketing',
        'content': 'Content Marketing',
        'acca': 'Financial Modeling',
        'cfa': 'Financial Modeling',
        'sbl': 'Strategic Planning',
        'presentation': 'Presentation'
    }

    all_courses = []

    for base_url in urls:
        if not str(base_url).startswith('http'):
            continue
            
        print(f"Đang phân tích cấu trúc DOM sâu từ: {base_url}")
        
        provider_name = ""
        base_url_lower = base_url.lower()
        if 'datapot' in base_url_lower:
            provider_name = "Datapot"
        elif 'tomorrowmarketer' in base_url_lower or 'tomorrow' in base_url_lower:
            provider_name = "Tomorrow Marketers"
        elif 'bisconline' in base_url_lower:
            provider_name = "BISC"
        elif 'unitrain' in base_url_lower:
            provider_name = "UniTrain"
        else:
            provider_name = "Trung tâm đào tạo"
 
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124'
            }
            response = requests.get(base_url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            extracted_links = set()
            for a in links:
                href = a['href']
                text = a.get_text(strip=True)
                text_lower = text.lower()
                
                # Check heuristics to see if this link leads to a course
                is_course = False
                
                # Datapot Logic
                if provider_name == 'Datapot':
                    if '/khoa-hoc/' in href or '/chuyen-de/' in href:
                        is_course = True
                
                # BISC Logic
                elif provider_name == 'BISC':
                    if 'acca-' in href.lower() or 'cfa-' in href.lower() or '/chuyen-muc/cfa' in href.lower():
                        is_course = True
                
                # Tomorrow Marketers Logic
                elif provider_name == 'Tomorrow Marketers':
                    if '-course' in href.lower() or '-system' in href.lower() or '-marketing' in href.lower() or 'foundation' in href.lower():
                        is_course = True
                        
                # UniTrain Logic
                elif provider_name == 'UniTrain':
                    if '/khoa-hoc/' in href.lower() or 'khoa-hoc' in href.lower() or 'course' in href.lower():
                        is_course = True
                
                else:
                    if '/khoa-hoc/' in href.lower() or 'course' in href.lower():
                        is_course = True
                
                if is_course:
                    full_link = urljoin(base_url, href)
                    if not full_link.startswith('http'): continue
                    
                    if full_link in extracted_links:
                        continue
                    extracted_links.add(full_link)
                    
                    # Fix Course Name if it's hidden behind "Tìm hiểu thêm" or "Đăng ký"
                    noisy_keywords = ['tìm hiểu', 'đăng ký', 'kích hoạt', 'hướng dẫn', 'xem chương trình', 'giáo trình', 'của chúng tôi', 'học thử', 'tất cả', '-']
                    course_name = clean_course_name(text)
                    
                    if not course_name or any(noise in course_name.lower() for noise in noisy_keywords) or len(course_name) < 5:
                        course_name = extract_course_name_from_url(href)
                        course_name = f"Khóa học {course_name}"
                        
                    # Map to Skill
                    target_skill = "Data Analysis" # Default
                    search_string = (href + " " + course_name).lower()
                    
                    # Score-based mapping to be more accurate
                    best_match = None
                    for kw, skill in skill_keywords.items():
                        if kw in search_string:
                            best_match = skill
                            # Prioritize exact matches like python or sql over generic data
                            if kw in ['python', 'sql', 'cfa', 'acca']:
                                break
                    
                    if best_match:
                        target_skill = best_match
                        
                    all_courses.append({
                        'Provider_Name': provider_name,
                        'Course_Name': course_name,
                        'Course_Link': full_link,
                        'Target_Skill': target_skill
                    })
                    
        except Exception as e:
            print(f"  -> Lỗi khi truy cập {base_url}: {e}")

    df = pd.DataFrame(all_courses)
    if not df.empty:
        # Drop duplicates primarily by Link
        df = df.drop_duplicates(subset=['Course_Link'])
        
        # Clean up course names
        df['Course_Name'] = df['Course_Name'].str.replace('Khoa Hoc', 'Khóa học', case=False)
        
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"\n[+] Deep Scraper hoàn tất! Đã lưu {len(df)} khóa học thực tế vào Database.")
    else:
        print("[-] Không tìm thấy dữ liệu khóa học.")

if __name__ == "__main__":
    print("--- BẮT ĐẦU DEEP CRAWLING ---")
    scrape_training_centers("data/extra course.csv", "data/processed/external_courses_db.csv")
