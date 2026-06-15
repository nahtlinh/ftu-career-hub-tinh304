import pandas as pd
import numpy as np
import re
import plotly.express as px

def load_and_clean_data(file_path):
    """
    Loads raw CSV data and performs initial cleaning.
    """
    # Load data
    df = pd.read_csv(file_path)
    
    # Handle NaN values gracefully to prevent crashes
    df['Job_Description'] = df['Job_Description'].fillna('')
    df['Salary'] = df['Salary'].fillna('Thỏa thuận')
    df['Job_Title'] = df['Job_Title'].fillna('Unknown')
    
    # Preprocess text columns: convert to lowercase for case-insensitive matching
    # Storing these in temporary columns to preserve original formatting for the final output
    df['Job_Description_Lower'] = df['Job_Description'].str.lower()
    df['Job_Title_Lower'] = df['Job_Title'].str.lower()
    
    return df

# Task 1: Market Demand Metric
def calculate_market_demand(df, keyword):
    """
    Counts the total number of jobs available based on a user-defined keyword.
    Uses pandas vectorization for efficient string matching.
    """
    # Convert keyword to lowercase
    kw = keyword.lower()
    
    # Vectorized boolean mask checking if keyword exists in title or description
    mask = df['Job_Title_Lower'].str.contains(kw, na=False) | \
           df['Job_Description_Lower'].str.contains(kw, na=False)
           
    total_jobs = mask.sum()
    return total_jobs, df[mask].copy()

# Task 2: Experience Barrier Funnel
def classify_experience(text):
    """
    Infers the experience level from raw text using regex patterns.
    Categorizes into: 'Intern/Fresher', 'Junior', 'Mid-Senior'.
    """
    text_str = str(text)
    
    # Regex patterns for different experience levels
    intern_pattern = r'\b(intern|fresher|thực tập|thuc tap|mới ra trường|chưa có kinh nghiệm|0 kinh nghiệm|0 year|no experience)\b'
    senior_pattern = r'\b(senior|manager|lead|trưởng phòng|quản lý|trưởng nhóm|chuyên gia|từ 3 năm|từ 4 năm|từ 5 năm|> 3 years|> 3 năm|3\+ years|4\+ years|5\+ years)\b'
    junior_pattern = r'\b(junior|1 năm|2 năm|1-2 năm|1 - 2 năm|1 to 2 years|1 year|2 years|1 yr|2 yrs)\b'
    
    if re.search(intern_pattern, text_str):
        return 'Intern/Fresher'
    elif re.search(senior_pattern, text_str):
        return 'Mid-Senior'
    elif re.search(junior_pattern, text_str):
        return 'Junior'
    else:
        # Default fallback if no specific keywords are found
        return 'Not Specified'

# Task X: Industry Classification
def classify_industry(text):
    """
    Infers the industry from raw text using regex patterns.
    """
    text_str = str(text).lower()
    
    if re.search(r'\b(ngân hàng|bank|tài chính|finance|chứng khoán|securities|bảo hiểm|fintech|thanh toán|payment|vnpay|urbox|mcredit)\b', text_str):
        return 'Tài chính / Fintech'
    elif re.search(r'\b(game|studio|giải trí|entertainment|esports)\b', text_str):
        return 'Game / Giải trí'
    elif re.search(r'\b(ecommerce|thương mại điện tử|shopee|tiki|lazada|retail|bán lẻ|fmcg|chuỗi|kamereo)\b', text_str):
        return 'Bán lẻ / E-commerce'
    elif re.search(r'\b(giáo dục|education|edtech|trường|đại học|academy|datapot)\b', text_str):
        return 'Giáo dục / EdTech'
    elif re.search(r'\b(y tế|healthcare|hospital|bệnh viện|dược|clinic)\b', text_str):
        return 'Y tế / Sức khỏe'
    elif re.search(r'\b(phần mềm|software|công nghệ|it|tech|technology|outsourcing|fpt|basevn|prox|gear inc)\b', text_str):
        return 'Công nghệ thông tin'
    elif re.search(r'\b(logistics|vận tải|supply chain|chuỗi cung ứng)\b', text_str):
        return 'Logistics / Vận tải'
    else:
        return 'Dịch vụ / Khác'

def create_experience_funnel(df):
    """
    Applies the classification to create the Experience column 
    and calculates percentage distribution.
    """
    # Combine title and description to maximize chances of finding the experience requirement
    combined_text = df['Job_Title_Lower'] + " " + df['Job_Description_Lower']
    
    # Apply our custom classifier
    df['Experience_Level'] = combined_text.apply(classify_experience)
    
    # value_counts(normalize=True) computes percentages directly
    exp_distribution = df['Experience_Level'].value_counts(normalize=True) * 100
    return exp_distribution.round(2)

# Task 3: Salary Distribution
def parse_salary(salary_text):
    """
    Extracts numeric salary values (in millions VND) from messy text.
    Handles single values and ranges (returns the mean).
    """
    text = str(salary_text).lower()
    
    # Return NaN for negotiable salaries or if no digits exist
    if 'thỏa thuận' in text or 'thuong luong' in text or 'cạnh tranh' in text or not any(char.isdigit() for char in text):
        return np.nan
        
    # Remove dots and commas used as thousand separators (e.g., 20.000.000 -> 20000000)
    clean_text = text.replace('.', '').replace(',', '')
    
    # Find all contiguous digit blocks
    numbers = re.findall(r'\d+', clean_text)
    
    if not numbers:
        return np.nan
        
    # Convert to floats
    numbers = [float(n) for n in numbers]
    
    # Normalize absolute values to millions (e.g., 20000000 -> 20.0)
    numbers = [n / 1000000 if n >= 1000000 else n for n in numbers]
    
    if len(numbers) == 1:
        return numbers[0]
    elif len(numbers) >= 2:
        # Calculate mean for a salary range (e.g., 10 - 15)
        return (numbers[0] + numbers[1]) / 2
    
    return np.nan

def calculate_salary_distribution(df):
    """
    Calculates average parsed salary for each experience level.
    """
    # Apply parsing function to create a clean numeric salary column
    df['Parsed_Salary_Million'] = df['Salary'].apply(parse_salary)
    
    # Group by Experience Level, calculate mean, and ignore NaNs implicitly
    salary_by_exp = df.groupby('Experience_Level')['Parsed_Salary_Million'].mean().round(2)
    return salary_by_exp

# Task 4: Top Required Skills
def extract_skills(df):
    """
    Scans Job_Description for predefined skills, creates binary columns,
    and calculates the percentage of jobs requiring each skill.
    """
    # Predefined dictionary of skills and their regex boundaries \b
    skills_dict = {
        'SQL': r'\bsql\b|\bmysql\b|\bpostgresql\b|\bsql server\b',
        'Python': r'\bpython\b',
        'Excel': r'\bexcel\b|\bgoogle sheets\b',
        'Power BI': r'\bpower bi\b|\bpowerbi\b',
        'Tableau': r'\btableau\b',
        'Machine Learning': r'\bmachine learning\b|\bml\b|\bhọc máy\b',
        'Statistics': r'\bstatistics\b|\bthống kê\b|\btoán thống kê\b',
        'ETL': r'\betl\b'
    }
    
    # Efficiently loop and create binary columns using numpy.where and vectorized string matching
    for skill_name, pattern in skills_dict.items():
        # 1 if skill is present in description, 0 otherwise
        df[f'Skill_{skill_name}'] = np.where(
            df['Job_Description_Lower'].str.contains(pattern, regex=True, na=False), 
            1, 
            0
        )
        
    # Isolate newly created skill columns
    skill_cols = [col for col in df.columns if col.startswith('Skill_')]
    
    # Calculate percentage: sum of 1s divided by total rows
    skill_percentages = (df[skill_cols].sum() / len(df)) * 100
    
    # Clean index for readability ('Skill_Python' -> 'Python')
    skill_percentages.index = skill_percentages.index.str.replace('Skill_', '')
    
    # Sort descending for the "Top" required skills
    skill_percentages = skill_percentages.sort_values(ascending=False).round(2)
    
    return skill_percentages

# Bonus: Plotly Visualization Snippet
def visualize_skills(skill_percentages):
    """
    Bonus: Visualizes the Top Required Skills as a Horizontal Bar Chart.
    """
    # Convert pandas Series to DataFrame for Plotly
    viz_df = skill_percentages.reset_index()
    viz_df.columns = ['Skill', 'Percentage']
    
    # Sort ascending so the largest bar appears at the top in Plotly's horizontal layout
    viz_df = viz_df.sort_values(by='Percentage', ascending=True)
    
    fig = px.bar(
        viz_df, 
        x='Percentage', 
        y='Skill', 
        orientation='h',
        title='Top Required Skills for Data Professionals',
        labels={'Percentage': 'Percentage of Jobs (%)', 'Skill': 'Skill Name'},
        text='Percentage' # Show percentage value on the bars
    )
    
    # Format the text on the bars
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    
    # Keep this commented out so the script doesn't hang waiting for the browser to close
    # fig.show()
    return fig

def main():
    input_file = 'neu_jobs_raw.csv'
    output_file = 'market_insight_ready.csv'
    keyword = 'data analyst'
    
    print("1. Loading and cleaning data...")
    df = load_and_clean_data(input_file)
    
    print(f"\n2. Calculating Market Demand for keyword: '{keyword}'...")
    total_jobs, filtered_df = calculate_market_demand(df, keyword)
    print(f"Total jobs matching '{keyword}': {total_jobs}")
    
    print("\n3. Processing Experience Funnel...")
    exp_distribution = create_experience_funnel(df)
    print("Experience Barrier Funnel (%):")
    print(exp_distribution)
    
    print("\n4. Processing Salary Distribution...")
    salary_by_exp = calculate_salary_distribution(df)
    print("Average Salary by Experience (Millions VND):")
    print(salary_by_exp)
    
    print("\n5. Extracting Top Required Skills...")
    skill_percentages = extract_skills(df)
    print("Top Required Skills (%):")
    print(skill_percentages)
    
    print("\n5.5. Classifying Industries...")
    combined_text_industry = df['Job_Title_Lower'] + " " + df['Company_Name'].fillna('').str.lower() + " " + df['Job_Description_Lower']
    df['Industry'] = combined_text_industry.apply(classify_industry)
    
    # Drop intermediate lowercased helper columns to keep the final CSV clean
    df.drop(columns=['Job_Description_Lower', 'Job_Title_Lower'], inplace=True, errors='ignore')
    
    print(f"\n6. Saving processed data to '{output_file}'...")
    # Use utf-8-sig to preserve Vietnamese characters in Excel
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print("Data saved successfully!")
    
    print("\n[Bonus] Preparing Visualization snippet (Plotly)...")
    fig = visualize_skills(skill_percentages)
    print("Visualization logic executed. (Uncomment fig.show() inside the script to render)")

if __name__ == '__main__':
    main()
