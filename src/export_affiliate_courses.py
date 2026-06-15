import pandas as pd
import json
import os
import sys

def export_affiliate_courses():
    csv_path = "data/processed/external_courses_db.csv"
    json_path = "web/data/affiliate_courses.json"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        sys.exit(1)
        
    df = pd.read_csv(csv_path)
    
    courses = []
    for _, row in df.iterrows():
        courses.append({
            "title": row.get('Course_Name', 'Khóa học'),
            "provider": row.get('Provider_Name', 'Trung tâm'),
            "category": row.get('Target_Skill', ''),
            "url": row.get('Course_Link', '#')
        })
        
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(courses, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully exported {len(courses)} courses to {json_path}")

if __name__ == "__main__":
    export_affiliate_courses()
