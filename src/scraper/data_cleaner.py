import pandas as pd
import os
import re

def normalize_level(level_str):
    """
    Quy chuẩn các cấp bậc hỗn hợp về các nhãn chuẩn: 
    ['Intern', 'Fresher', 'Junior', 'Mid-level', 'Senior', 'Manager'].
    """
    if not isinstance(level_str, str):
        return "Unknown"
        
    level_lower = level_str.lower()
    
    if any(kw in level_lower for kw in ["thực tập sinh", "intern", "internship"]):
        return "Intern"
    if any(kw in level_lower for kw in ["mới ra trường", "fresher", "không yêu cầu kinh nghiệm", "chưa có kinh nghiệm"]):
        return "Fresher"
    if any(kw in level_lower for kw in ["junior", "nhân viên", "chuyên viên", "kinh nghiệm 1 năm", "1 năm"]):
        return "Junior"
    if any(kw in level_lower for kw in ["mid-level", "mid", "kinh nghiệm 2 năm", "2 năm", "3 năm"]):
        return "Mid-level"
    if any(kw in level_lower for kw in ["senior", "kinh nghiệm lâu năm", "kinh nghiệm 4 năm", "5 năm"]):
        return "Senior"
    if any(kw in level_lower for kw in ["manager", "quản lý", "trưởng phòng", "giám đốc", "leader", "trưởng nhóm"]):
        return "Manager"
        
    return "Unknown"

def clean_salary(salary_str):
    """
    Tách cột Salary_Range thành Min_Salary và Max_Salary.
    Nếu là "Thỏa thuận" thì gán -1.
    Ví dụ: "10.000.000 - 15.000.000" -> 10, 15 (triệu VND)
           "Từ 10.000.000" -> 10, None
           "Đến 20.000.000" -> None, 20
    """
    if not isinstance(salary_str, str) or "thỏa thuận" in salary_str.lower() or "thoả thuận" in salary_str.lower():
        return -1.0, -1.0
        
    # Loại bỏ các ký tự không cần thiết, chuyển về số thập phân triệu VNĐ
    clean_str = salary_str.lower().replace(",", ".").replace(" vnđ", "").replace(" vnd", "").replace(" đ", "")
    
    # Tìm tất cả các con số trong chuỗi (ví dụ: 10.000.000 -> 10000000)
    numbers = re.findall(r'\d+(?:\.\d+)*', clean_str)
    
    parsed_nums = []
    for num in numbers:
        # Nếu chuỗi dạng 10.000.000, xóa dấu chấm để thành số nguyên
        if num.count('.') >= 2 or (num.count('.') == 1 and len(num.split('.')[-1]) == 3):
            val = float(num.replace('.', ''))
        else:
            val = float(num)
            
        # Quy đổi về đơn vị triệu VND nếu giá trị quá lớn
        if val >= 1000000:
            val = val / 1000000.0
        elif val >= 1000:
            val = val / 1000.0
            
        parsed_nums.append(val)
        
    if len(parsed_nums) == 2:
        return min(parsed_nums), max(parsed_nums)
    elif len(parsed_nums) == 1:
        if "từ" in clean_str or "trên" in clean_str or "min" in clean_str:
            return parsed_nums[0], -1.0
        elif "đến" in clean_str or "dưới" in clean_str or "max" in clean_str or "lên tới" in clean_str:
            return -1.0, parsed_nums[0]
        else:
            return parsed_nums[0], parsed_nums[0]
            
    return -1.0, -1.0

def process_and_save_data(scraped_data):
    """
    Nhận dữ liệu thô (List of dicts), xử lý và lưu vào CSV.
    Kết hợp với file cũ để tránh trùng lặp.
    """
    raw_dir = os.path.join("data", "raw")
    proc_dir = os.path.join("data", "processed")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)
    
    raw_path = os.path.join(raw_dir, "neu_jobs_raw.csv")
    clean_path = os.path.join(proc_dir, "neu_jobs_clean.csv")
    
    if not scraped_data:
        print("[INFO] No new data to process.")
        return
        
    df_new = pd.DataFrame(scraped_data)
    
    # Lưu raw data (Append or Create)
    if os.path.exists(raw_path):
        df_old_raw = pd.read_csv(raw_path)
        df_raw_combined = pd.concat([df_old_raw, df_new], ignore_index=True)
        # Drop duplicates in raw based on Title and Company
        df_raw_combined.drop_duplicates(subset=["Job Title", "Company"], keep="last", inplace=True)
        df_raw_combined.to_csv(raw_path, index=False, encoding="utf-8-sig")
    else:
        df_new.to_csv(raw_path, index=False, encoding="utf-8-sig")
        
    print(f"[INFO] Saved raw data to {raw_path}")
    
    # Bắt đầu làm sạch dữ liệu
    df_clean = df_new.copy()
    
    # Normalize Level
    df_clean['Level_Clean'] = df_clean['Level'].apply(normalize_level)
    
    # Clean Salary
    df_clean[['Min_Salary', 'Max_Salary']] = df_clean.apply(
        lambda row: pd.Series(clean_salary(row['Salary_Range'])), axis=1
    )
    
    # Nếu file clean đã tồn tại, merge và drop duplicates
    if os.path.exists(clean_path):
        df_old_clean = pd.read_csv(clean_path)
        df_clean_combined = pd.concat([df_old_clean, df_clean], ignore_index=True)
        df_clean_combined.drop_duplicates(subset=["Job Title", "Company"], keep="last", inplace=True)
        df_clean = df_clean_combined
        
    df_clean.to_csv(clean_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] Saved clean data to {clean_path}. Total clean records: {len(df_clean)}")
    
    return df_clean
