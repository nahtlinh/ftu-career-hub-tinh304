import json
import os
import sys

# Ensure src directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.scraper.market_insights import MarketInsights

def export_data():
    print("Exporting data for Web App...")
    
    # 1. Market Insights
    csv_path = os.path.join("data", "processed", "neu_jobs_clean.csv")
    
    insights_data = {}
    if os.path.exists(csv_path):
        insight_engine = MarketInsights(csv_path)
        insights_data = insight_engine.generate_full_report()
    else:
        print("[WARNING] neu_jobs_clean.csv not found! Emitting empty insights.")
        insights_data = {
            "Job_Counts_By_Family": {},
            "Level_Percentages": {},
            "Industry_Counts": {},
            "Average_Salary": {},
            "Top_10_Skills": {}
        }
        
    # 2. Syllabi Data (Course Data)
    course_path = os.path.join("data", "raw", "course_data.txt")
    courses = []
    if os.path.exists(course_path):
        with open(course_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        # Assuming the format is roughly: CourseName | Code | Credits | Description
                        parts = line.split('|')
                        if len(parts) >= 2:
                            courses.append({
                                "code": parts[1].strip(),
                                "name": parts[0].strip(),
                                "description": parts[3].strip() if len(parts) > 3 else ""
                            })
                    except Exception:
                        pass
                        
    # 3. Forage Categories Definition
    forage_categories = [
        {"id": "banking", "name": "Banking & Finance", "family_map": "Finance", "qfilter": "Banking"},
        {"id": "career", "name": "Career Development & Interview Skills", "family_map": "HR", "qfilter": "Career"},
        {"id": "consulting", "name": "Consulting & Strategy", "family_map": "BA", "qfilter": "Consulting"},
        {"id": "customer", "name": "Customer Success & Account Management", "family_map": "Sales", "qfilter": "Customer+Success"},
        {"id": "data", "name": "Data & Analytics", "family_map": "Data", "qfilter": "Data"},
        {"id": "gov", "name": "Government & Public Service", "family_map": "Government", "qfilter": "Government"},
        {"id": "hr", "name": "Human Resources & Recruiting", "family_map": "HR", "qfilter": "Human+Resources"},
        {"id": "insurance", "name": "Insurance", "family_map": "Finance", "qfilter": "Insurance"},
        {"id": "pm", "name": "Product Management", "family_map": "BA", "qfilter": "Product+Management"},
        {"id": "project", "name": "Project Management", "family_map": "BA", "qfilter": "Project+Management"},
        {"id": "sales", "name": "Sales Accounting & Advisory", "family_map": "Sales", "qfilter": "Sales"}
    ]
    
    # We also add our scraped categories if they aren't fully covered
    existing_families = [c["family_map"] for c in forage_categories]
    for family in insights_data.get("Job_Counts_By_Family", {}).keys():
        if family not in existing_families:
            forage_categories.append({
                "id": family.lower(),
                "name": family,
                "family_map": family,
                "qfilter": family
            })

    # 3.5 FTU Courses & External Courses
    ftu_courses = []
    ftu_csv_path = os.path.join("data", "processed", "ftu_skills_database.csv")
    if os.path.exists(ftu_csv_path):
        import csv
        with open(ftu_csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ftu_courses.append({
                    "code": row.get('course_code', ''),
                    "name": row.get('course_name', ''),
                    "domain_knowledge": [s.strip().lower() for s in row.get('domain_knowledge', '').split(',') if s.strip()],
                    "jd_skills": [s.strip().lower() for s in row.get('jd_skills', '').split(',') if s.strip()],
                    "tools": [s.strip().lower() for s in row.get('tools', '').split(',') if s.strip()]
                })
                
    external_courses = []
    ext_csv_path = os.path.join("data", "processed", "external_courses_db.csv")
    if os.path.exists(ext_csv_path):
        import csv
        with open(ext_csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                external_courses.append({
                    "provider": row.get('Provider_Name', ''),
                    "title": row.get('Course_Name', ''),
                    "url": row.get('Course_Link', ''),
                    "category": row.get('Target_Skill', '')
                })

    # Combine all
    export_payload = {
        "market_insights": insights_data,
        "courses": courses,
        "categories": forage_categories,
        "jobs": [],
        "ftu_courses": ftu_courses,
        "external_courses": external_courses
    }
    
    # 4. Jobs List (for Col 1 of Job View)
    if os.path.exists(csv_path):
        import csv
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Required fields: id, title, company, family, required_skills (array), desc
                skills_str = row.get('Skills', '')
                skills_list = [s.strip().lower() for s in skills_str.split(',') if s.strip()]
                
                export_payload["jobs"].append({
                    "id": str(reader.line_num),
                    "title": row.get('Job_Title', ''),
                    "company": row.get('Company', ''),
                    "logo": row.get('Logo_URL', ''),
                    "family": row.get('Job_Family', ''),
                    "required_skills": skills_list,
                    "desc": row.get('JD_Text', ''),
                    "url": row.get('URL', ''),
                    "salary": row.get('Salary_Range', 'Thỏa thuận'),
                    "location": row.get('Location', '')
                })
    
    # Ensure web/data folder exists
    os.makedirs(os.path.join("web", "data"), exist_ok=True)
    out_path = os.path.join("web", "data", "app_data.json")
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(export_payload, f, ensure_ascii=False, indent=4)
        
    print(f"Data exported successfully to {out_path}!")

if __name__ == "__main__":
    export_data()
