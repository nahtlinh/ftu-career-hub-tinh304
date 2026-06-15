import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse
from datetime import datetime
import base64
import os

def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# Configure the Streamlit page layout and theme
st.set_page_config(page_title="Job Recruitment MVP", layout="wide")

# -----------------------------------------------------------------------------
# CUSTOM CSS INJECTION
# -----------------------------------------------------------------------------
# 1. Imports Google Sans font
# 2. Imports Phosphor Icons
# 3. Tweaks Streamlit tabs to look like a robust top navigation bar
custom_css = """
<style>
@import url('https://fonts.cdnfonts.com/css/google-sans');
@import url('https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css');

:root {
    --primary-color: #00b14f;
    --primary-hover: #009944;
}

html, body, [class*="css"] {
    font-family: 'Product Sans', 'Google Sans', sans-serif !important;
}

/* Make tabs look more like a balanced top navigation bar */
.stTabs [data-baseweb="tab-list"] {
    gap: 32px;
    justify-content: center;
    border-bottom: 2px solid #f0f2f6;
    padding-top: 10px;
}
.stTabs [data-baseweb="tab"] {
    font-size: 1.15rem;
    font-weight: 500;
    padding-bottom: 12px;
}

/* Custom button for Job Cards */
.apply-btn {
    display: block;
    background-color: var(--primary-color);
    color: white !important;
    padding: 10px 20px;
    text-decoration: none;
    border-radius: 6px;
    font-weight: 500;
    text-align: center;
    transition: background-color 0.2s;
    margin-top: 10px;
}
.apply-btn:hover {
    background-color: var(--primary-hover);
}

/* Override Streamlit Primary Buttons */
div.stButton > button[kind="primary"] {
    background-color: var(--primary-color) !important;
    border-color: var(--primary-color) !important;
    color: white !important;
}
div.stButton > button[kind="primary"]:hover {
    background-color: var(--primary-hover) !important;
    border-color: var(--primary-hover) !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA LOADING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('market_insight_ready.csv')
        return df
    except FileNotFoundError:
        st.error("Dataset 'market_insight_ready.csv' not found. Please process the raw data first.")
        return pd.DataFrame()

# -----------------------------------------------------------------------------
# CORE ALGORITHM: SKILL MATCHING
# -----------------------------------------------------------------------------
import re
from collections import defaultdict

def calculate_match_score(student_profile, job_description_text, skill_mapping_db):
    """
    Calculates a Fit Score between a student's profile and a job description based on skills.
    Data Flow:
    1. Parse student's completed_courses -> fetch matched Skill_Tags & Weights from skill_mapping_db
    2. Add student's skills_from_cv with a fixed weight (e.g., 5).
    3. Compile all possible skills and regex-scan the job_description_text to detect required skills.
    4. Intersect the two vectors and compute the percentage match.
    """
    student_skill_vector = defaultdict(int)
    
    # 1. Student Skills from Courses
    completed_courses = student_profile.get('completed_courses', [])
    for course in completed_courses:
        course_data = skill_mapping_db[skill_mapping_db['Course_Name'].str.lower() == str(course).lower()]
        for _, row in course_data.iterrows():
            skill = row['Skill_Tag']
            if pd.notna(skill) and not str(skill).startswith('N/A'):
                student_skill_vector[skill] += int(row['Weight'])
                
    # 2. Student Skills from CV
    cv_skills = student_profile.get('skills_from_cv', [])
    for skill in cv_skills:
        student_skill_vector[skill] += 5 
        
    # APPLY FILTER: Remove skills that the user explicitly unticked in the UI
    if 'explicit_major_skills' in student_profile:
        allowed_skills = set(student_profile['explicit_major_skills'])
        allowed_skills.update(cv_skills)
        
        skills_to_remove = [sk for sk in student_skill_vector if sk not in allowed_skills]
        for sk in skills_to_remove:
            del student_skill_vector[sk]
        
    # 3. Job Skills Extraction (Regex) with Aliases
    job_skill_vector = {}
    
    # Load FTU skills
    all_possible_skills = set(skill_mapping_db['Skill_Tag'].dropna().unique())
    all_possible_skills.update(cv_skills)
    
    # Load External skills so we can detect skills NOT taught at the university
    try:
        external_db = pd.read_csv('external_courses_db.csv')
        all_possible_skills.update(external_db['Target_Skill'].dropna().unique())
    except FileNotFoundError:
        external_db = pd.DataFrame()
        
    all_possible_skills = {s for s in all_possible_skills if not str(s).startswith('N/A')}
    
    # Define keywords/aliases for skills to make extraction much smarter
    skill_aliases = {
        'Financial Modeling': ['finance', 'financial', 'accounting', 'acca', 'cfa', 'cma', 'financial modeling', 'audit'],
        'Data Analysis': ['data analysis', 'data analyst', 'analytics', 'dashboard', 'power bi', 'excel', 'data processing'],
        'SQL': ['sql', 'mysql', 'postgresql', 'query', 'database'],
        'Python': ['python', 'pandas', 'numpy', 'machine learning'],
        'Digital Marketing': ['marketing', 'digital marketing', 'seo', 'campaign', 'social media'],
        'Content Marketing': ['content', 'copywriting', 'content marketing', 'writing'],
        'Market Research': ['research', 'market research', 'competitor', 'insight'],
        'Strategic Planning': ['strategy', 'strategic', 'planning', 'sbl', 'management'],
        'Presentation': ['presentation', 'communication', 'present', 'public speaking', 'negotiation'],
        'Problem Solving': ['problem solving', 'problem-solving', 'analytical', 'solution'],
        'Logistics': ['logistics', 'supply chain', 'warehouse', 'freight', 'transportation', 'export', 'import']
    }
    
    text_lower = str(job_description_text).lower()
    for skill in all_possible_skills:
        # Check standard skill name
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            job_skill_vector[skill] = 10  # Max weight for required skill
            continue
            
        # Check aliases
        if skill in skill_aliases:
            for alias in skill_aliases[skill]:
                alias_pattern = r'\b' + re.escape(alias.lower()) + r'\b'
                if re.search(alias_pattern, text_lower):
                    job_skill_vector[skill] = 10
                    break
            
    # 4. Compare Vectors & Compute Score
    matched_skills = []
    missing_skills = []
    total_required_score = sum(job_skill_vector.values())
    sum_student_score_for_required = 0
    
    for required_skill, job_weight in job_skill_vector.items():
        if required_skill in student_skill_vector:
            matched_skills.append(required_skill)
            # Cap score so it doesn't exceed 100%
            capped_student_score = min(student_skill_vector[required_skill], job_weight)
            sum_student_score_for_required += capped_student_score
        else:
            missing_skills.append(required_skill)
            
    match_score = (sum_student_score_for_required / total_required_score * 100) if total_required_score > 0 else 0.0
        
    # 5. Generate Suggestions (FTU & External)
    suggestions_ftu = []
    suggestions_external = []
    
    for m_skill in missing_skills:
        # Search FTU Internal DB
        courses_teaching_skill = skill_mapping_db[skill_mapping_db['Skill_Tag'] == m_skill]
        if not courses_teaching_skill.empty:
            best_course = courses_teaching_skill.sort_values(by='Weight', ascending=False).iloc[0]['Course_Name']
            suggestions_ftu.append({'skill': m_skill, 'course': best_course})
            
        # Search External Training Centers DB
        if not external_db.empty:
            ext_courses = external_db[external_db['Target_Skill'] == m_skill]
            if not ext_courses.empty:
                # Get all matching external courses for this skill
                for _, ext_course in ext_courses.iterrows():
                    suggestions_external.append({
                        'skill': m_skill,
                        'provider': ext_course['Provider_Name'],
                        'course_name': ext_course['Course_Name'],
                        'link': ext_course['Course_Link']
                    })
            
    return {
        'match_score': round(match_score, 2),
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'suggestions_ftu': suggestions_ftu,
        'suggestions_external': suggestions_external
    }

# -----------------------------------------------------------------------------
# PAGE 1: TRADITIONAL JOB SEARCH & DETAIL
# -----------------------------------------------------------------------------
def render_job_detail(df, job_index, detail_col, match_col):
    # Retrieve job details
    row = df.loc[job_index]
    
    with detail_col:
        # Title and company header block
        header_html = f"""
        <div style="background-color: #f5f7fc; border-radius: 8px; padding: 20px; margin-bottom: 20px; border-left: 4px solid #2b3149;">
            <h3 style="margin-top: 0; color: #2b3149;">{row['Job_Title']}</h3>
            <div style="font-size: 15px; color: #555; margin-bottom: 8px;"><b>{row['Company_Name']}</b></div>
            <div style="font-size: 14px; display: inline-block; background-color: #e3e8f8; color: #2b3149; padding: 4px 10px; border-radius: 4px; margin-right: 10px;">Full-time</div>
            <div style="font-size: 14px; display: inline-block; color: #e91e63; font-weight: bold;">{row['Salary']}</div>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        
        # Display full Job Description
        st.markdown("### Mô tả công việc")
        st.info(str(row['Job_Description']).replace('\n', '\n\n'))
    
    with match_col:
        st.markdown("### 🎯 Phân tích Độ Phù Hợp")
        
        # Fetch Student Data from Profile
        if 'student_profile' not in st.session_state or (not st.session_state.student_profile['name'] and not st.session_state.student_profile['completed_courses']):
            st.warning("⚠️ Bạn chưa thiết lập Hồ sơ cá nhân. Vui lòng sang tab 'Hồ sơ' để điền thông tin ngành học và upload CV trước khi Match.")
            student_profile = {
                'major': 'N/A',
                'completed_courses': [],
                'skills_from_cv': []
            }
            can_match = False
        else:
            student_profile = st.session_state.student_profile
            st.markdown("**Hồ sơ ứng viên đang sử dụng:**")
            st.caption(f"Chuyên ngành: {student_profile['major']} | Đã học: {len(student_profile['completed_courses'])} môn | Kỹ năng (CV): {', '.join(student_profile['skills_from_cv']) if student_profile['skills_from_cv'] else 'Không có'}")
            can_match = True
    
        if st.button("🚀 Match & Apply Now", type="primary", disabled=not can_match, key="btn_match"):
            # Load the skill mapping DB
            try:
                skill_db = pd.read_csv('ftu_skills_database.csv')
                
                # Execute Matching Algorithm
                result = calculate_match_score(student_profile, row['Job_Description'], skill_db)
                
                # Display output
                st.metric("Tỷ lệ phù hợp (Fit Score)", f"{result['match_score']}%")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"**✅ Kỹ năng đã có (Matched):** {', '.join(result['matched_skills']) if result['matched_skills'] else 'None'}")
                with col2:
                    st.error(f"**❌ Kỹ năng còn thiếu (Missing):** {', '.join(result['missing_skills']) if result['missing_skills'] else 'None'}")
                    
                st.write("---")
                if result['suggestions_ftu'] or result['suggestions_external']:
                    st.markdown("#### 💡 Lộ trình Khuyến nghị Học tập (Learning Paths)")
                    
                    # Render FTU courses
                    if result['suggestions_ftu']:
                        st.markdown("##### 🏫 Môn học nội bộ (ĐH Ngoại Thương)")
                        for sugg in result['suggestions_ftu']:
                            st.info(f"**{sugg['skill']}** ➞ Nên đăng ký học: `{sugg['course']}`")
                    
                    # Render External courses
                    if result['suggestions_external']:
                        st.markdown("##### 🌐 Khóa học thực chiến (Trung tâm ngoài)")
                        for sugg in result['suggestions_external']:
                            # Encode parameters to pass safely via URL
                            encoded_url = urllib.parse.quote(sugg['link'])
                            encoded_course = urllib.parse.quote(sugg['course_name'])
                            encoded_provider = urllib.parse.quote(sugg['provider'])
                            
                            # Generate Redirect Route
                            redirect_href = f"/?redirect_url={encoded_url}&course_name={encoded_course}&provider={encoded_provider}"
                            
                            st.markdown(
                                f"""
                                <div style="padding: 12px; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 12px; background-color: #f9f9f9; transition: box-shadow 0.3s; cursor: pointer;" onmouseover="this.style.boxShadow='0 4px 8px rgba(233,30,99,0.1)'" onmouseout="this.style.boxShadow='none'">
                                    <div style="font-size: 14px; color: #555;"><i class='ph ph-buildings' style='color: #2b3149;'></i> <b>{sugg['provider']}</b> • Bổ sung kỹ năng: <b>{sugg['skill']}</b></div>
                                    <div style="font-size: 16px; font-weight: 600; margin: 8px 0; color: #2b3149;">{sugg['course_name']}</div>
                                    <a href="{redirect_href}" target="_blank" style="text-decoration: none; color: white; background-color: #e91e63; padding: 6px 14px; border-radius: 4px; font-size: 14px; display: inline-block; font-weight: 500;">Đăng ký khóa học</a>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                        
            except FileNotFoundError:
                st.error("Không tìm thấy file 'ftu_skills_database.csv'. Hãy chạy script tạo DB trước.")

def render_job_search(df):
    # CSS injection for FTU Career Hub Identity
    st.markdown("""
        <style>
        /* Primary color overrides */
        .stButton>button {
            background-color: #e91e63 !important;
            color: white !important;
            border-radius: 4px !important;
            border: none !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #c2185b !important;
            box-shadow: 0 4px 8px rgba(233, 30, 99, 0.3) !important;
        }
        /* Custom Header Colors */
        h1, h2, h3, h4, h5, h6 {
            color: #2b3149 !important;
        }
        /* Make the left column scrollable */
        [data-testid="column"]:nth-of-type(1) {
            max-height: 800px;
            overflow-y: auto;
            padding-right: 15px;
        }
        /* Hide default header */
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Hero Banner
    hero_html = """
    <div style="background-image: url('https://images.unsplash.com/photo-1556761175-5973dc0f32e7?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80'); background-size: cover; background-position: center; padding: 40px 20px; text-align: center; color: white; margin-bottom: 30px; position: relative;">
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(26, 35, 126, 0.45);"></div>
        <div style="position: relative; z-index: 1;">
            <div style="background-color: #f05161; border-radius: 50%; width: 160px; height: 160px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 0px; margin-left: -35%; box-shadow: 0 4px 15px rgba(233, 30, 99, 0.5);">
                <span style="font-size: 20px; font-weight: 500; line-height: 1.2;">Looking for<br>your <i style='font-weight: 800; font-style: italic;'>best-fit</i><br>job?</span>
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # Search Bar Section
    st.markdown("<p style='font-size: 18px; font-weight: 700; color: #2b3149; margin-bottom: 5px;'>Find Full and Part Time Jobs. Employment and Career Search</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_keyword = st.text_input("", placeholder="Job title...")
    with col2:
        st.markdown("<div style='padding-top: 5px; font-size: 14px; color: #555;'>Locations:</div>", unsafe_allow_html=True)
        # Fake checkboxes for UI purposes
        st.markdown("<span style='margin-right: 10px;'><input type='checkbox' checked> All</span><span style='margin-right: 10px;'><input type='checkbox'> Hanoi</span><span><input type='checkbox'> Ho Chi Minh City</span>", unsafe_allow_html=True)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        # Search button does nothing functionally different but fits UI
        st.button("Search Jobs", use_container_width=True)
    
    # Filter dataframe based on input
    if search_keyword:
        mask = df['Job_Title'].str.contains(search_keyword, case=False, na=False) | \
               df['Company_Name'].str.contains(search_keyword, case=False, na=False)
        filtered_df = df[mask]
    else:
        filtered_df = df
        
    st.markdown(f"<p style='color: #2b3149; font-weight: 700; font-size: 14px; margin-top: 20px;'>{len(filtered_df)} Jobs Found</p>", unsafe_allow_html=True)
    st.write("---")
    
    # 3-COLUMN LAYOUT
    list_col, detail_col, match_col = st.columns([1, 1.2, 1.2], gap="large")
    
    with list_col:
        # Loop through filtered jobs to render cards
        for idx, row in filtered_df.iterrows():
            # Highlight selected card
            is_selected = st.session_state.get('selected_job_index') == idx
            bg_color = "#fef2f2" if is_selected else "#ffffff"
            border_color = "#e91e63" if is_selected else "#f0f0f0"
            
            with st.container():
                st.markdown(f"""
                <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 6px; padding: 15px; margin-bottom: 15px; cursor: pointer; transition: all 0.2s ease;">
                    <div style="display: flex; justify-content: space-between;">
                        <div style="width: 40px; height: 40px; background-color: #f5f5f5; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #2b3149;">
                            {str(row['Company_Name'])[0].upper()}
                        </div>
                        <div style="flex: 1; margin-left: 15px;">
                            <h5 style="margin: 0; color: #2b3149; font-size: 15px;">{row['Job_Title']}</h5>
                            <div style="font-size: 12px; color: #666; margin-top: 4px;">{row['Company_Name']}</div>
                            <div style="font-size: 11px; color: #999; margin-top: 2px;">{row['Experience_Level']}</div>
                            <div style="font-size: 13px; color: #e91e63; font-weight: 600; margin-top: 4px;">{row['Salary']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Streamlit button to trigger state change
                if st.button("Xem", key=f"view_{idx}", use_container_width=True):
                    st.session_state.selected_job_index = idx
                    st.rerun()
                st.write("") # Spacer

    selected_idx = st.session_state.get('selected_job_index')
    if selected_idx is not None and selected_idx in filtered_df.index:
        render_job_detail(df, selected_idx, detail_col, match_col)
    else:
        with detail_col:
            st.info("👈 Hãy chọn một công việc ở danh sách bên trái để xem chi tiết.")

# -----------------------------------------------------------------------------
# PAGE 2: MARKET INSIGHT DASHBOARD
# -----------------------------------------------------------------------------
def render_market_insight(df):
    st.markdown("<h2 style='text-align: center;'><i class='ph ph-chart-pie-slice'></i> Market Insight Dashboard</h2>", unsafe_allow_html=True)
    
    st.write("") # Spacer
    
    tab_market, tab_traffic = st.tabs(["📊 Market Stats", "🚀 Course Click Analytics"])
    
    with tab_market:
        # Center the selectbox using grid layout
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            job_roles = ['All', 'Data Analyst', 'Business Analyst', 'Marketing', 'Developer']
            selected_role = st.selectbox("Chọn vị trí cần phân tích thị trường:", job_roles)
        
        # Conditional logic to filter dataframe
        if selected_role != 'All':
            filtered_df = df[df['Job_Title'].str.contains(selected_role, case=False, na=False)]
        else:
            filtered_df = df
            
        if filtered_df.empty:
            st.warning(f"Không có dữ liệu cho vị trí: '{selected_role}'. Vui lòng chọn vị trí khác.")
            return
            
        st.write("---")
        
        # --- ROW 1: Metrics ---
        st.markdown("### <i class='ph ph-trend-up'></i> Chỉ số thị trường (Key Metrics)", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3, gap="large")
        
        with col1:
            st.metric(label="Tổng cầu thị trường", value=len(filtered_df))
            
        with col2:
            avg_salary = filtered_df['Parsed_Salary_Million'].mean()
            val = f"{avg_salary:.1f} Triệu VNĐ" if pd.notna(avg_salary) else "N/A"
            st.metric(label="Mức lương trung bình", value=val)
                
        with col3:
            top_exp = filtered_df['Experience_Level'].mode()[0] if not filtered_df['Experience_Level'].empty else "N/A"
            st.metric(label="Kinh nghiệm phổ biến", value=top_exp)
        
        st.write("---")
        
        # --- ROW 2: Donut Chart & Funnel Chart ---
        col_left, col_right = st.columns(2, gap="large")
        
        with col_left:
            st.markdown("#### <i class='ph ph-chart-donut'></i> Phân bổ theo Lĩnh vực (Industry)", unsafe_allow_html=True)
            
            if 'Industry' in filtered_df.columns:
                industry_counts = filtered_df['Industry'].value_counts().reset_index()
                industry_counts.columns = ['Industry', 'Count']
                
                fig_donut = px.pie(
                    industry_counts, 
                    values='Count', 
                    names='Industry', 
                    hole=0.4, 
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
            else:
                # Fallback if the Industry column hasn't been generated yet
                company_counts = filtered_df['Company_Name'].value_counts().reset_index().head(5)
                company_counts.columns = ['Company_Name', 'Count']
                
                fig_donut = px.pie(
                    company_counts, 
                    values='Count', 
                    names='Company_Name', 
                    hole=0.4, 
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            # Tight layout to prevent breaking
            fig_donut.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_donut, use_container_width=True)
            
        with col_right:
            st.markdown("#### <i class='ph ph-funnel'></i> Rào cản gia nhập (Experience Barrier)", unsafe_allow_html=True)
            exp_counts = filtered_df['Experience_Level'].value_counts().reset_index()
            exp_counts.columns = ['Experience_Level', 'Count']
            
            funnel_order = {'Intern/Fresher': 1, 'Junior': 2, 'Mid-Senior': 3, 'Not Specified': 4}
            exp_counts['Order'] = exp_counts['Experience_Level'].map(funnel_order)
            exp_counts = exp_counts.sort_values('Order')
            
            fig_funnel = px.funnel(
                exp_counts,
                x='Count',
                y='Experience_Level',
                color_discrete_sequence=['#00B4D8']
            )
            fig_funnel.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_funnel, use_container_width=True)
            
        st.write("---")
        
        # --- ROW 3: Top Required Skills Horizontal Bar Chart ---
        st.markdown("#### <i class='ph ph-wrench'></i> Kỹ năng được yêu cầu nhiều nhất", unsafe_allow_html=True)
        
        skill_cols = [col for col in filtered_df.columns if col.startswith('Skill_')]
        if skill_cols:
            skill_percentages = (filtered_df[skill_cols].sum() / len(filtered_df)) * 100
            skill_percentages.index = skill_percentages.index.str.replace('Skill_', '')
            skill_df = skill_percentages.reset_index()
            skill_df.columns = ['Skill', 'Percentage']
            skill_df = skill_df.sort_values(by='Percentage', ascending=True)
            skill_df = skill_df[skill_df['Percentage'] > 0]
            
            if not skill_df.empty:
                fig_skills = px.bar(
                    skill_df, 
                    x='Percentage', 
                    y='Skill', 
                    orientation='h',
                    text='Percentage',
                    color='Percentage',
                    color_continuous_scale='Greens'
                )
                fig_skills.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_skills.update_layout(
                    xaxis_title="Percentage of Jobs (%)", 
                    yaxis_title="",
                    coloraxis_showscale=False,
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_skills, use_container_width=True)
            else:
                st.info("Không có kỹ năng cụ thể nào được trích xuất cho lựa chọn này.")
                
    with tab_traffic:
        st.markdown("### 🚀 Traffic Dashboard - Clicks Tracking")
        st.markdown("Dashboard này giúp Product Owner theo dõi lượng truy cập (CTR) chuyển đổi sang các nền tảng đào tạo EduTech.")
        try:
            clicks_df = pd.read_csv('clicks_tracking.csv')
            
            # Key metrics
            col1, col2 = st.columns(2)
            col1.metric("Tổng lượt click (Total Clicks)", len(clicks_df))
            col2.metric("Số lượng khóa học nhận click", clicks_df['Course_Name'].nunique())
            
            st.write("---")
            
            # Analytics by Provider
            st.markdown("#### Phân bổ lượt click theo Trung tâm")
            provider_counts = clicks_df['Provider'].value_counts().reset_index()
            provider_counts.columns = ['Provider', 'Clicks']
            fig_provider = px.pie(provider_counts, values='Clicks', names='Provider', hole=0.4)
            st.plotly_chart(fig_provider, use_container_width=True)
            
            # Analytics by Course
            st.markdown("#### Top Khóa học thu hút nhiều click nhất")
            course_counts = clicks_df['Course_Name'].value_counts().reset_index()
            course_counts.columns = ['Course_Name', 'Clicks']
            fig_course = px.bar(course_counts, x='Clicks', y='Course_Name', orientation='h', color='Clicks', color_continuous_scale='Greens')
            fig_course.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_course, use_container_width=True)
            
            # Raw Data
            with st.expander("Xem dữ liệu log thô (Raw Logs)"):
                st.dataframe(clicks_df.sort_values(by='Timestamp', ascending=False))
                
        except FileNotFoundError:
            st.info("Chưa có lượt click nào được ghi nhận. Hãy thử click vào một khóa học ở màn hình Tìm việc để tạo data log.")

# -----------------------------------------------------------------------------
# PAGE 3: USER PROFILE
# -----------------------------------------------------------------------------
def render_profile():
    st.markdown("<h2 style='text-align: center;'><i class='ph ph-user-circle'></i> Hồ sơ cá nhân</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Thiết lập hồ sơ học vấn và CV để hệ thống có thể đối chiếu (Match) với yêu cầu công việc.</p>", unsafe_allow_html=True)
    
    st.write("---")
    
    # Load skill db to get list of available courses and skills
    try:
        skill_db = pd.read_csv('ftu_skills_database.csv')
        available_courses = skill_db['Course_Name'].unique().tolist()
        master_skills = [s for s in skill_db['Skill_Tag'].dropna().unique() if not str(s).startswith('N/A')]
    except FileNotFoundError:
        available_courses = []
        master_skills = []
        st.warning("Chưa có cơ sở dữ liệu khóa học. Vui lòng chạy script tạo DB trước.")

    if 'student_profile' not in st.session_state:
        st.session_state.student_profile = {
            'name': '',
            'major': '',
            'completed_courses': [],
            'skills_from_cv': []
        }
        
    profile = st.session_state.student_profile

    col1, col2 = st.columns([1, 1], gap="large")
    
    # Load majors list
    try:
        major_db = pd.read_csv('major.csv')
        ftu_programs = major_db['Chương trình đào tạo'].dropna().unique().tolist()
    except FileNotFoundError:
        ftu_programs = ["Chương trình đào tạo Kinh doanh quốc tế"]

    with col1:
        st.markdown("### 📝 Thông tin học vấn")
        name = st.text_input("Họ và tên (*)", value=profile['name'], placeholder="Ví dụ: Nguyễn Văn A")
        
        # Selectbox for Major instead of text input and multiselect
        default_index = ftu_programs.index(profile['major']) if profile['major'] in ftu_programs else 0
        major = st.selectbox(
            "Chương trình đào tạo (Chuyên ngành) (*)", 
            options=ftu_programs,
            index=default_index,
            help="Chọn CTĐT của bạn. Môn học thuộc CTĐT này sẽ tự động được hệ thống gợi ý bên dưới."
        )
        
        # Determine default skills for this major
        if "Kinh doanh quốc tế" in major or "Logistics" in major or "Kinh doanh số" in major:
            # Get all unique valid skills that are taught in the curriculum
            suggested_major_skills = [s for s in skill_db['Skill_Tag'].dropna().unique() if s in master_skills]
        else:
            suggested_major_skills = []
            
        # Reverse translation: check if profile already has courses, what skills do they map to?
        current_profile_skills = []
        for c in profile.get('completed_courses', []):
            skill_tag = skill_db.loc[skill_db['Course_Name'] == c, 'Skill_Tag'].values
            if len(skill_tag) > 0 and pd.notna(skill_tag[0]) and skill_tag[0] in master_skills:
                current_profile_skills.append(skill_tag[0])
        current_profile_skills = list(set(current_profile_skills))
        
        # If the user changed the major dropdown, we reset to suggested. Otherwise keep what they saved.
        default_major_skills = current_profile_skills if profile.get('major') == major else suggested_major_skills
            
        selected_major_skills = st.multiselect(
            "Kỹ năng được đào tạo từ Chuyên ngành (*)",
            options=master_skills,
            default=default_major_skills,
            help="Hệ thống đã gom gọn hàng chục môn học thành các kỹ năng cốt lõi. Hãy XÓA BỎ kỹ năng nào bạn cảm thấy mình học chưa tốt hoặc chưa từng học (vd: SQL, Python)."
        )
        
    with col2:
        st.markdown("### 📄 Tải lên CV & Kỹ năng")
        uploaded_file = st.file_uploader("Tải lên CV (PDF/DOCX) để tự động trích xuất kỹ năng", type=['pdf', 'docx'])
        
        parsed_skills = []
        if uploaded_file is not None:
            if st.session_state.get('last_uploaded_filename') != uploaded_file.name:
                cv_text = ""
                try:
                    if uploaded_file.name.endswith('.pdf'):
                        import PyPDF2
                        reader = PyPDF2.PdfReader(uploaded_file)
                        for page in reader.pages:
                            extracted = page.extract_text()
                            if extracted:
                                cv_text += extracted + " "
                    elif uploaded_file.name.endswith('.docx'):
                        import docx
                        doc = docx.Document(uploaded_file)
                        cv_text = " ".join([para.text for para in doc.paragraphs])
                except Exception as e:
                    st.error(f"Lỗi khi đọc file CV: {e}")
                    
                if cv_text:
                    import re
                    cv_lower = cv_text.lower()
                    for skill in master_skills:
                        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                        if re.search(pattern, cv_lower):
                            parsed_skills.append(skill)
                
                st.session_state.parsed_skills = parsed_skills
                st.session_state.last_uploaded_filename = uploaded_file.name
                if parsed_skills:
                    st.success(f"Phát hiện {len(parsed_skills)} kỹ năng từ CV. Vui lòng kiểm tra lại ở mục bên dưới!")
                else:
                    st.warning("Không nhận diện được kỹ năng tự động từ CV. Vui lòng tự chọn bên dưới.")
            else:
                parsed_skills = st.session_state.get('parsed_skills', [])
        
        # Determine defaults for skills
        default_skills = list(set(profile.get('skills_from_cv', []) + parsed_skills))
        # Keep only skills that exist in master_skills to avoid Streamlit errors
        default_skills = [s for s in default_skills if s in master_skills]
        
        final_skills = st.multiselect(
            "Kỹ năng cá nhân (CV & Tự đánh giá)",
            options=master_skills,
            default=default_skills,
            help="Hệ thống tự tick các kỹ năng quét từ CV. Bạn có thể XÓA kỹ năng bị nhận diện sai hoặc THÊM kỹ năng còn thiếu."
        )
        
    st.write("")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("💾 Lưu Hồ Sơ", type="primary", use_container_width=True):
            if not name or not major:
                st.error("Vui lòng điền Họ tên và Chuyên ngành.")
            else:
                st.session_state.student_profile['name'] = name
                st.session_state.student_profile['major'] = major
                
                # Translate selected major skills back to specific courses so the matching engine can explain "Why"
                assigned_courses = []
                for sk in selected_major_skills:
                    courses_for_skill = skill_db[skill_db['Skill_Tag'] == sk]['Course_Name'].tolist()
                    assigned_courses.extend(courses_for_skill)
                
                st.session_state.student_profile['completed_courses'] = list(set(assigned_courses))
                st.session_state.student_profile['skills_from_cv'] = final_skills
                st.session_state.student_profile['explicit_major_skills'] = selected_major_skills
                st.success("Hồ sơ đã được lưu thành công! Hãy sang tab 'Tìm việc làm' để xem mức độ phù hợp (Fit Score) với các công việc.")

# -----------------------------------------------------------------------------
# MAIN APP ROUTER & CLICK TRACKING HANDLER
# -----------------------------------------------------------------------------
def handle_redirect_route():
    """Handles the query parameters redirect routing to track clicks before sending to destination"""
    if 'redirect_url' in st.query_params:
        target_url = st.query_params['redirect_url']
        course_name = st.query_params.get('course_name', 'Unknown')
        provider = st.query_params.get('provider', 'Unknown')
        
        # Log to clicks_tracking.csv
        log_file = 'clicks_tracking.csv'
        try:
            df = pd.read_csv(log_file)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Timestamp', 'Provider', 'Course_Name', 'Target_URL'])
            
        new_row = {
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Provider': provider,
            'Course_Name': course_name,
            'Target_URL': target_url
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(log_file, index=False)
        
        # Redirect
        st.markdown(f"<h2>Đang chuyển hướng (Redirecting)...</h2>", unsafe_allow_html=True)
        st.write(f"Hệ thống đang điều hướng bạn đến khóa học: **{course_name}** của **{provider}**.")
        st.markdown(f"Vui lòng đợi trong giây lát hoặc [bấm vào đây]({target_url}) nếu trình duyệt không tự chuyển.")
        
        # HTML Meta Refresh to perform actual redirect
        st.markdown(f'<meta http-equiv="refresh" content="1; url={target_url}">', unsafe_allow_html=True)
        return True
    return False

def main():
    # Capture Redirect Route First
    if handle_redirect_route():
        return  # Stop executing the rest of the Streamlit layout
        
    # Initialize Session State for Routing
    if 'selected_job_index' not in st.session_state:
        st.session_state.selected_job_index = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Jobs"

    df = load_data()
    if df.empty:
        return
        
    # CSS for the Custom Radio Navbar
    st.markdown("""
        <style>
        header {visibility: hidden;} /* Hide default streamlit header */
        div[role="radiogroup"] {
            gap: 25px;
            margin-top: 15px;
            margin-bottom: 15px;
        }
        div[role="radiogroup"] > label {
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
            font-weight: 600 !important;
            color: #666 !important;
            cursor: pointer;
        }
        div[role="radiogroup"] > label > div:first-child {
            display: none; /* Hide radio circle */
        }
        div[role="radiogroup"] label p {
            font-size: 15px;
            padding-bottom: 8px;
        }
        div[role="radiogroup"] label[data-checked="true"] p {
            color: #2b3149 !important;
            border-bottom: 2px solid #e91e63;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Render Unified Navigation Bar
    st.write("") # Spacer
    col_logo, col_nav = st.columns([1, 4])
    with col_logo:
        logo_b64 = get_base64_of_bin_file('logo.png')
        logo_html = f"<img src='data:image/png;base64,{logo_b64}' style='height: 48px; margin-top: 5px;'/>" if logo_b64 else "<span style='color: #e91e63; font-size: 34px;'>C</span>areerHub"
        st.markdown(f"<div style='cursor: pointer; display: flex; align-items: center;'>{logo_html}</div>", unsafe_allow_html=True)
    with col_nav:
        pages = ["Jobs", "Market Insight", "Hồ sơ", "FTU Internship", "Companies", "Events", "Resources"]
        default_index = pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0
        selected_page = st.radio("", pages, horizontal=True, label_visibility="collapsed", index=default_index)
        st.session_state.current_page = selected_page
        
    st.write("---")
    
    # Page Routing
    if selected_page == "Jobs":
        render_job_search(df)
    elif selected_page == "Market Insight":
        render_market_insight(df)
    elif selected_page == "Hồ sơ":
        render_profile()
    else:
        st.info(f"🚧 Tính năng **{selected_page}** đang được phát triển. Vui lòng quay lại sau!")

if __name__ == "__main__":
    main()
