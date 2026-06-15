import pandas as pd
import os
import re

class MarketInsights:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        if os.path.exists(csv_path):
            self.df = pd.read_csv(csv_path)
        else:
            self.df = pd.DataFrame()
            print(f"[WARNING] File {csv_path} not found. Analytics will be empty.")

    def get_job_counts_by_family(self):
        """Tổng số lượng job đang tuyển đếm theo từng Job Family."""
        if self.df.empty or "Job_Family" not in self.df.columns:
            return {}
        return self.df["Job_Family"].value_counts().to_dict()

    def get_level_percentages(self):
        """Tỷ lệ % tuyển dụng theo Level."""
        if self.df.empty or "Level_Clean" not in self.df.columns:
            return {}
        counts = self.df["Level_Clean"].value_counts(normalize=True) * 100
        return counts.round(2).to_dict()

    def get_industry_counts(self):
        """Số lượng job theo Industry."""
        if self.df.empty or "Industry" not in self.df.columns:
            return {}
        return self.df["Industry"].value_counts().head(10).to_dict()

    def get_average_salary(self):
        """
        Mức lương trung bình (Min-Max) nhóm theo từng Level và Job Family
        (bỏ qua giá trị -1 "Thỏa thuận").
        """
        if self.df.empty or "Min_Salary" not in self.df.columns:
            return {}
            
        df_valid = self.df[(self.df["Min_Salary"] != -1) & (self.df["Max_Salary"] != -1)]
        
        if df_valid.empty:
            return {}
            
        grouped = df_valid.groupby(["Job_Family", "Level_Clean"])[["Min_Salary", "Max_Salary"]].mean().round(2)
        
        # Chuyển về dạng dict thân thiện với JSON
        result = {}
        for (family, level), row in grouped.iterrows():
            if family not in result:
                result[family] = {}
            result[family][level] = {
                "Avg_Min_Salary": row["Min_Salary"],
                "Avg_Max_Salary": row["Max_Salary"]
            }
        return result

    def extract_top_skills(self):
        """
        Phân tích cột JD_Text, đếm tần suất xuất hiện của các từ khóa kỹ năng.
        Trả về Top 10 Required Skills.
        """
        if self.df.empty or "JD_Text" not in self.df.columns:
            return {}
            
        skills_keywords = [
            # Tech & Data
            "python", "sql", "excel", "powerpoint", "powerbi", "power bi", "tableau", 
            "spss", "r", "agile", "scrum", "sap", "erp",
            # Design & Media
            "capcut", "canva", "photoshop", "illustrator", "figma", "premiere",
            # Soft Skills
            "english", "communication", "giao tiếp", "tiếng anh", "làm việc nhóm", "teamwork"
        ]
        
        # Khởi tạo dict đếm skill
        skill_counts = {skill: 0 for skill in skills_keywords}
        
        # Gộp powerbi và power bi
        
        for jd in self.df["JD_Text"].dropna():
            jd_lower = str(jd).lower()
            for skill in skills_keywords:
                # Dùng regex cơ bản tìm từ nguyên vẹn để tránh trùng lặp substring
                # ví dụ: " r " thay vì "r" trong từ khác
                # Tuy nhiên, tiếng Việt và các từ dính dấu câu có thể làm khó regex \b
                # Nên ta dùng thủ thuật đơn giản hơn: kiểm tra chuỗi có trong text
                
                # Với từ quá ngắn như 'r', bắt buộc phải dùng \b
                if skill == 'r':
                    if re.search(r'\br\b', jd_lower):
                        skill_counts[skill] += 1
                else:
                    if skill in jd_lower:
                        skill_counts[skill] += 1
                        
        # Gộp các keyword đồng nghĩa
        if "power bi" in skill_counts:
            skill_counts["powerbi"] += skill_counts.pop("power bi")
            
        # Sắp xếp và lấy top 10
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_skills[:10])

    def extract_top_skills_by_family(self):
        """
        Phân tích cột JD_Text theo từng Job Family, đếm tần suất xuất hiện của kỹ năng.
        Trả về dictionary dạng {family: {skill: count}} cho Top 10 skills.
        """
        if self.df.empty or "JD_Text" not in self.df.columns or "Job_Family" not in self.df.columns:
            return {}
            
        skills_keywords = [
            # Tech & Data
            "python", "sql", "excel", "powerpoint", "powerbi", "power bi", "tableau", 
            "spss", "r", "agile", "scrum", "sap", "erp",
            # Design & Media
            "capcut", "canva", "photoshop", "illustrator", "figma", "premiere",
            # Soft Skills
            "english", "communication", "giao tiếp", "tiếng anh", "làm việc nhóm", "teamwork"
        ]
        
        result = {}
        for family, group in self.df.groupby("Job_Family"):
            skill_counts = {skill: 0 for skill in skills_keywords}
            for jd in group["JD_Text"].dropna():
                jd_lower = str(jd).lower()
                for skill in skills_keywords:
                    if skill == 'r':
                        if re.search(r'\br\b', jd_lower):
                            skill_counts[skill] += 1
                    else:
                        if skill in jd_lower:
                            skill_counts[skill] += 1
                            
            if "power bi" in skill_counts:
                skill_counts["powerbi"] += skill_counts.pop("power bi")
                
            sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
            result[family] = dict(sorted_skills[:10])
            
        return result

    def generate_full_report(self):
        """Trích xuất toàn bộ report dạng JSON-like Dict"""
        return {
            "Job_Counts_By_Family": self.get_job_counts_by_family(),
            "Level_Percentages": self.get_level_percentages(),
            "Top_Industries": self.get_industry_counts(),
            "Average_Salary": self.get_average_salary(),
            "Top_10_Skills": self.extract_top_skills(),
            "Top_10_Skills_By_Family": self.extract_top_skills_by_family()
        }

if __name__ == "__main__":
    # Test nhanh
    insight = MarketInsights(os.path.join("data", "processed", "neu_jobs_clean.csv"))
    report = insight.generate_full_report()
    import json
    print(json.dumps(report, indent=4, ensure_ascii=False))
