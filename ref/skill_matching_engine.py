import pandas as pd
import re
from collections import defaultdict
import json

def calculate_match_score(student_profile, job_description_text, skill_mapping_db):
    """
    Calculates a Fit Score between a student's profile and a job description based on skills.
    
    Args:
        student_profile (dict): e.g., {'major': 'Finance', 'completed_courses': [...], 'skills_from_cv': [...]}
        job_description_text (str): Raw text of the job posting
        skill_mapping_db (pd.DataFrame): The database mapping Course_Name -> Skill_Tag -> Weight
        
    Returns:
        dict: Containing match_score, matched_skills, missing_skills, suggestions.
    """
    
    # ==========================================
    # 1. Student Skill Extraction
    # ==========================================
    # We use defaultdict so if a skill doesn't exist yet, it starts at 0.
    student_skill_vector = defaultdict(int)
    
    # A. Map skills from Completed Courses
    completed_courses = student_profile.get('completed_courses', [])
    for course in completed_courses:
        # Match course name case-insensitively
        course_data = skill_mapping_db[skill_mapping_db['Course_Name'].str.lower() == str(course).lower()]
        
        for _, row in course_data.iterrows():
            skill = row['Skill_Tag']
            # Ignore 'N/A' or invalid skills
            if pd.notna(skill) and not str(skill).startswith('N/A'):
                student_skill_vector[skill] += int(row['Weight'])
                
    # B. Add skills from CV (Self-declared)
    cv_skills = student_profile.get('skills_from_cv', [])
    for skill in cv_skills:
        # We assign a fixed weight of 5 for skills claimed on CV
        student_skill_vector[skill] += 5 
        
    # ==========================================
    # 2. Job Skill Extraction
    # ==========================================
    job_skill_vector = {}
    
    # We build a list of all potential skills to search for in the JD.
    # This includes all skills taught at the university + skills the student has on their CV.
    all_possible_skills = set(skill_mapping_db['Skill_Tag'].dropna().unique())
    all_possible_skills.update(cv_skills)
    all_possible_skills = {s for s in all_possible_skills if not str(s).startswith('N/A')}
    
    text_lower = job_description_text.lower()
    
    # Scan JD using Regex word boundaries \b
    for skill in all_possible_skills:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            job_skill_vector[skill] = 10  # Required job skill gets max weight of 10
            
    # ==========================================
    # 3. Matching Algorithm
    # ==========================================
    matched_skills = []
    missing_skills = []
    
    total_required_score = sum(job_skill_vector.values())
    sum_student_score_for_required = 0
    
    for required_skill, job_weight in job_skill_vector.items():
        if required_skill in student_skill_vector:
            matched_skills.append(required_skill)
            
            # Cap the student's skill score at the job's requirement weight (10)
            # This prevents a student with a score of 30 in SQL from exceeding 100% total match score
            capped_student_score = min(student_skill_vector[required_skill], job_weight)
            sum_student_score_for_required += capped_student_score
        else:
            missing_skills.append(required_skill)
            
    # Calculate Percentage Fit Score
    if total_required_score > 0:
        match_score = (sum_student_score_for_required / total_required_score) * 100
    else:
        # If no skills are detected in the JD, we can't reliably score it
        match_score = 0.0
        
    # ==========================================
    # 4. Generate Suggestions
    # ==========================================
    suggestions = []
    for m_skill in missing_skills:
        # Find university courses that teach this missing skill
        courses_teaching_skill = skill_mapping_db[skill_mapping_db['Skill_Tag'] == m_skill]
        
        if not courses_teaching_skill.empty:
            # Find the best course (highest weight) for this skill
            best_course = courses_teaching_skill.sort_values(by='Weight', ascending=False).iloc[0]['Course_Name']
            suggestions.append(f"You are missing '{m_skill}'. Consider taking '{best_course}' or adding '{m_skill}' to your CV.")
        else:
            suggestions.append(f"You are missing '{m_skill}'. Consider adding '{m_skill}' to your CV via external learning/certifications.")
            
    return {
        'match_score': round(match_score, 2),
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'suggestions': suggestions,
        # Included for debug/tracing purposes:
        'debug_student_vector': dict(student_skill_vector),
        'debug_job_vector': job_skill_vector
    }


# ==========================================
# TEST CASE / DUMMY EXECUTION
# ==========================================
if __name__ == "__main__":
    print("--- Running Skill Matching Algorithm Test ---\n")
    
    # 1. Dummy skill mapping DB (Simulating what comes from ftu_skills_database.csv)
    dummy_data = {
        'Course_Name': ['Introduction to Data', 'Advanced Python', 'Financial Markets', 'Business Stats'],
        'Skill_Tag': ['SQL', 'Python', 'Financial Modeling', 'Data Analysis'],
        'Weight': [8, 10, 7, 9]
    }
    skill_mapping_db = pd.DataFrame(dummy_data)
    
    # 2. Dummy Student Profile
    student_profile = {
        'major': 'Data Science',
        'completed_courses': ['Introduction to Data', 'Business Stats'], # Teaches SQL (8) and Data Analysis (9)
        'skills_from_cv': ['Communication', 'Excel']                     # Teaches Communication (5) and Excel (5)
    }
    
    # 3. Dummy Job Description (Requires SQL, Python, Communication)
    job_description_text = "We are looking for a Data Analyst. Requirements: Strong SQL and Python programming skills. Financial modeling is a plus. Excellent Communication is necessary."
    
    # 4. Run Function
    result = calculate_match_score(student_profile, job_description_text, skill_mapping_db)
    
    # 5. Output Results
    print(json.dumps(result, indent=4))
