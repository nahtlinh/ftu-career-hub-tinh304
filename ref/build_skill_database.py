import os
import json
import csv
import re
from collections import defaultdict, Counter

# Thư viện xử lý Word và PDF
# Cần cài đặt: pip install python-docx PyPDF2
try:
    import docx
except ImportError:
    print("Vui lòng cài đặt python-docx: pip install python-docx")
    
try:
    import PyPDF2
except ImportError:
    print("Vui lòng cài đặt PyPDF2: pip install PyPDF2")

# ==========================================
# PHẦN 1: TRÍCH XUẤT VĂN BẢN (DATA EXTRACTION)
# ==========================================

def extract_text_from_docx(file_path):
    """Đọc văn bản từ file .docx"""
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Lỗi khi đọc file DOCX {file_path}: {e}")
        return ""

def extract_text_from_pdf(file_path):
    """Đọc văn bản từ file .pdf"""
    try:
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    except Exception as e:
        print(f"Lỗi khi đọc file PDF {file_path}: {e}")
        return ""

def process_syllabi(folder_path, output_json):
    """Duyệt thư mục và trích xuất text lưu vào file JSON trung gian"""
    extracted_data = []
    
    if not os.path.exists(folder_path):
        print(f"Thư mục '{folder_path}' không tồn tại. Đã tạo mới, vui lòng bỏ file vào và chạy lại.")
        os.makedirs(folder_path, exist_ok=True)
        return extracted_data

    files = [f for f in os.listdir(folder_path) if f.endswith(('.docx', '.pdf'))]
    if not files:
        print(f"Không tìm thấy file .docx hoặc .pdf nào trong '{folder_path}'.")
        return extracted_data

    for filename in files:
        file_path = os.path.join(folder_path, filename)
        content = ""
        
        if filename.lower().endswith('.docx'):
            content = extract_text_from_docx(file_path)
        elif filename.lower().endswith('.pdf'):
            content = extract_text_from_pdf(file_path)
            
        extracted_data.append({
            'file_name': filename,
            'content': content.strip()
        })
        
    # Lưu ra file JSON trung gian
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)
        
    print(f"[+] Đã trích xuất thành công {len(extracted_data)} files và lưu vào {output_json}")
    return extracted_data

# ==========================================
# PHẦN 2: XÂY DỰNG TỪ ĐIỂN KỸ NĂNG
# ==========================================

def generate_skill_database(extracted_data, output_csv):
    """Phân tích văn bản để gán tag kỹ năng và đánh trọng số"""
    
    # Master Skill List do người dùng cung cấp
    master_skills = [
        'Data Analysis', 'SQL', 'Python', 'Financial Modeling', 
        'Market Research', 'Logistics', 'Strategic Planning', 
        'Content Marketing', 'Digital Marketing', 'Presentation', 'Problem Solving'
    ]
    
    # Tạo Regex pattern cho từng kỹ năng (không phân biệt hoa/thường)
    # Dùng \b để chỉ bắt từ hoàn chỉnh (tránh bắt nhầm, vd 'Python' trong 'Pythonic')
    skill_patterns = {skill: re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE) for skill in master_skills}
    
    final_database = []
    
    for item in extracted_data:
        course_name = item['file_name']
        text = item['content']
        
        if not text:
            continue
            
        skill_counts = defaultdict(int)
        
        # Analyze & Standardize: Đếm số lần xuất hiện của các kỹ năng chuẩn trong văn bản
        for skill, pattern in skill_patterns.items():
            matches = pattern.findall(text)
            if matches:
                skill_counts[skill] = len(matches)
                
        # Trích xuất các Keyword đặc trưng cho nội dung môn học (TF extraction cơ bản)
        # Loại bỏ các từ dừng (stopwords) phổ biến trong đề cương đại học
        stopwords = set([
            "students", "course", "learning", "week", "chapter", "student", "this", "that", "with", "from",
            "sinh", "viên", "môn", "học", "tuần", "chương", "phần", "giáo", "trình", "đánh", "giá", 
            "kiểm", "tra", "nghiên", "cứu", "thực", "hiện", "cung", "cấp", "hiểu", "biết", "kiến", "thức",
            "nội", "dung", "giảng", "dạy", "bài", "tập", "thảo", "luận", "trình", "bày", "phương", "pháp",
            "mục", "tiêu", "yêu", "cầu", "tài", "liệu", "tham", "khảo", "chuyên", "ngành", "năng", "lực",
            "điểm", "thi", "học", "phần", "thông", "tin", "sinh", "hoạt", "chính", "sách", "quy", "định", "phát", "triển"
        ])
        
        # Tìm các từ có độ dài >= 4 để làm từ khóa
        words = re.findall(r'\b[a-zA-Zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]{4,}\b', text.lower())
        meaningful_words = [w for w in words if w not in stopwords]
        
        # Lấy top 5 từ khoá xuất hiện nhiều nhất làm Context Keyword
        word_counts = Counter(meaningful_words)
        top_keywords = ", ".join([w for w, c in word_counts.most_common(7)])
        
        # Nếu môn học không map được skill nào trong danh sách, ta vẫn lưu lại Course với Keyword của nó
        if not skill_counts:
            final_database.append({
                'Course_Name': course_name,
                'Skill_Tag': 'N/A (Chưa có trong Master List)',
                'Weight': 0,
                'Course_Keywords': top_keywords
            })
        else:
            # Đánh trọng số (1 đến 10)
            for skill, count in skill_counts.items():
                weight = min(10, count * 2) 
                final_database.append({
                    'Course_Name': course_name,
                    'Skill_Tag': skill,
                    'Weight': weight,
                    'Course_Keywords': top_keywords
                })
            
    # Lưu kết quả ra CSV
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Course_Name', 'Skill_Tag', 'Weight', 'Course_Keywords'])
        writer.writeheader()
        writer.writerows(final_database)
        
    print(f"[+] Cơ sở dữ liệu kỹ năng đã được lưu tại {output_csv}")
    print(f"[!] Gợi ý kỹ năng mới: Hiện tại script sử dụng Regex trên Master List. Để phát hiện kỹ năng mới (Out of vocabulary), bạn có thể cần tích hợp NLP/LLM (ví dụ: OpenAI API).")

if __name__ == "__main__":
    folder_name = "syllabus_folder"
    intermediate_json = "extracted_syllabi.json"
    final_csv = "ftu_skills_database.csv"
    
    print("--- BƯỚC 1: TRÍCH XUẤT VĂN BẢN ĐỀ CƯƠNG ---")
    data = process_syllabi(folder_name, intermediate_json)
    
    if data:
        print("\n--- BƯỚC 2: PHÂN TÍCH VÀ ĐÁNH TRỌNG SỐ KỸ NĂNG ---")
        generate_skill_database(data, final_csv)
    else:
        print("\n[!] Không có dữ liệu để phân tích. Hãy đảm bảo file đã được copy vào thư mục 'syllabus_folder'.")
