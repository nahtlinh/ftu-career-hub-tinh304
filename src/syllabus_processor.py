"""
==============================================================================
  FTU Career Hub — Phase 2: Automated Syllabus Processing Pipeline
  File   : src/syllabus_processor.py
  Author : FTU Career Hub Team
  Purpose: Reads all .docx syllabi, extracts structured skill data via the
           Gemini API, and compiles a unified CSV skills database.

  ⚠️  BEFORE RUNNING:
      Set your Gemini API key as an environment variable:
        Windows CMD  : setx GEMINI_API_KEY "your_key_here"
        PowerShell   : $env:GEMINI_API_KEY = "your_key_here"
        Linux / macOS: export GEMINI_API_KEY="your_key_here"
==============================================================================
"""

import os
import json
import time

import pandas as pd
import docx
from google import genai

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Directory containing the raw .docx syllabus files
SYLLABUS_DIR = os.path.join("data", "raw", "syllabi")

# Output path for the compiled skills database
OUTPUT_CSV = os.path.join("data", "processed", "ftu_skills_database.csv")

# Gemini model to use for parsing
GEMINI_MODEL = "gemini-2.5-flash"

# Seconds to wait between successful API calls (keeps us under rate limits)
RATE_LIMIT_DELAY = 4       # seconds between successful calls

# Seconds to wait after a failed API call before moving on
ERROR_RETRY_DELAY = 10     # seconds after an error


# ==============================================================================
# HELPER FUNCTION 1 — Text Extraction
# ==============================================================================

def extract_text(filepath: str) -> str:
    """
    Reads a .docx file and returns all paragraph text as a single string.

    Only textual content is extracted; images, tables (as images), headers/
    footers embedded as pictures, and any embedded objects are ignored.

    Args:
        filepath (str): Absolute or relative path to the .docx file.

    Returns:
        str: The full concatenated text of the document, or an empty string
             if the file cannot be read.
    """
    try:
        document = docx.Document(filepath)

        # Each `paragraph` object contains one block of text.
        # We join all non-empty paragraphs with a newline for readability.
        paragraphs = [para.text for para in document.paragraphs if para.text.strip()]
        full_text = "\n".join(paragraphs)

        return full_text

    except Exception as e:
        print(f"    [ERROR] Could not read file '{filepath}': {e}")
        return ""


# ==============================================================================
# HELPER FUNCTION 2 — Gemini API Call
# ==============================================================================

def extract_skills_with_gemini(text: str, api_key: str) -> str | None:
    """
    Sends syllabus text to the Gemini API and asks it to return structured
    JSON containing skill information extracted from the syllabus.

    Args:
        text    (str): The raw text content of a single syllabus document.
        api_key (str): Your Google Generative AI API key.

    Returns:
        str | None: A raw JSON string from the model, or None if the call fails.
    """
    # Configure the SDK with the user's API key
    client = genai.Client(api_key=api_key)

    # ── Prompt Engineering ──────────────────────────────────────────────────
    # The prompt is explicit about:
    #   1. The exact JSON schema the model must follow.
    #   2. Returning ONLY raw JSON — no markdown fences, no explanations.
    # This makes the response directly parseable with json.loads().
    # ────────────────────────────────────────────────────────────────────────
    prompt = f"""
You are an expert academic curriculum analyst. Analyze the following university syllabus text and extract structured information.

Return ONLY a raw JSON object — do NOT wrap it in markdown code blocks (no ```json), do NOT include any explanation or extra text before or after the JSON.

The JSON object MUST follow this exact schema:
{{
  "course_code": "The official course code, e.g. ECO101 (string)",
  "course_name": "The full official name of the course (string)",
  "domain_knowledge": ["List of key knowledge domains or topics covered in this course"],
  "jd_skills": ["List of practical job-description skills students will gain, suitable for a resume or job posting"],
  "tools": ["List of specific software, programming languages, frameworks, or tools mentioned"]
}}

If a field cannot be found in the text, use an empty list [] for arrays or "N/A" for strings.

SYLLABUS TEXT:
---
{text}
---
"""

    # Send the prompt and return the raw text response
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )
    return response.text


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================

def main():
    """
    Orchestrates the full syllabus processing pipeline:
      1. Reads the GEMINI_API_KEY from environment variables.
      2. Iterates over every .docx file in SYLLABUS_DIR.
      3. Extracts text from each file.
      4. Calls the Gemini API to parse skills into structured JSON.
      5. Collects all results into a Pandas DataFrame.
      6. Saves the DataFrame as a CSV to OUTPUT_CSV.
    """

    # ── 1. Load API Key ──────────────────────────────────────────────────────
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. "
            "Please set it as an environment variable before running this script.\n"
            "  Windows PowerShell: $env:GEMINI_API_KEY = 'your_key_here'\n"
            "  Windows CMD       : setx GEMINI_API_KEY 'your_key_here'\n"
            "  Linux / macOS     : export GEMINI_API_KEY='your_key_here'"
        )

    # ── 2. Validate Input Directory ──────────────────────────────────────────
    if not os.path.isdir(SYLLABUS_DIR):
        raise FileNotFoundError(
            f"Syllabus directory not found: '{SYLLABUS_DIR}'\n"
            "Please place your .docx files in 'data/raw/syllabi/' and try again."
        )

    # Collect all .docx files (case-insensitive extension check)
    docx_files = [
        f for f in os.listdir(SYLLABUS_DIR)
        if f.lower().endswith(".docx")
    ]

    if not docx_files:
        print(f"[WARNING] No .docx files found in '{SYLLABUS_DIR}'. Exiting.")
        return

    total = len(docx_files)
    print(f"\n{'='*60}")
    print(f"  FTU Syllabus Processor — Found {total} file(s) to process")
    print(f"{'='*60}\n")

    # ── 3. Processing Loop ───────────────────────────────────────────────────
    results = []   # Will hold one dict per successfully processed syllabus

    for index, filename in enumerate(docx_files, start=1):
        filepath = os.path.join(SYLLABUS_DIR, filename)
        print(f"[{index}/{total}] Processing: {filename}")

        # Step A: Extract raw text from the .docx file
        text = extract_text(filepath)
        if not text:
            print(f"    [SKIP] Empty or unreadable file — skipping.\n")
            continue

        # Step B: Send text to Gemini and parse the JSON response
        try:
            print(f"    → Calling Gemini API ({GEMINI_MODEL})...")
            raw_json_string = extract_skills_with_gemini(text, api_key)

            # Strip any accidental whitespace around the JSON string
            raw_json_string = raw_json_string.strip()

            # Bổ sung thuật toán "dọn rác" nếu AI vẫn ngoan cố xuất ra markdown
            if raw_json_string.startswith("```json"):
                raw_json_string = raw_json_string.replace("```json", "").replace("```", "").strip()
            elif raw_json_string.startswith("```"):
                raw_json_string = raw_json_string.replace("```", "").strip()

            # Parse the JSON string into a Python dictionary
            skill_data = json.loads(raw_json_string)

            # Tag the result with the source filename for traceability
            skill_data["source_file"] = filename

            results.append(skill_data)
            print(f"    ✓ Successfully parsed — course: {skill_data.get('course_code', 'N/A')}")

            # ── RATE LIMITING ─────────────────────────────────────────────
            # Wait between calls to stay within the Gemini free-tier limit
            print(f"    ⏳ Waiting {RATE_LIMIT_DELAY}s before next call...\n")
            time.sleep(RATE_LIMIT_DELAY)

        except json.JSONDecodeError as e:
            # The model returned something that isn't valid JSON
            print(f"    [ERROR] JSON parsing failed for '{filename}': {e}")
            print(f"    Raw response was: {raw_json_string[:300]}...")  # show first 300 chars
            print(f"    ⏳ Waiting {ERROR_RETRY_DELAY}s then skipping...\n")
            time.sleep(ERROR_RETRY_DELAY)

        except Exception as e:
            # Catches network errors, quota exceeded, invalid API key, etc.
            print(f"    [ERROR] Gemini API call failed for '{filename}': {e}")
            print(f"    ⏳ Waiting {ERROR_RETRY_DELAY}s then skipping...\n")
            time.sleep(ERROR_RETRY_DELAY)

    # ── 4. Aggregation & Export ──────────────────────────────────────────────
    if not results:
        print("[WARNING] No files were successfully processed. No CSV written.")
        return

    print(f"{'='*60}")
    print(f"  Processing complete — {len(results)}/{total} file(s) succeeded.")
    print(f"{'='*60}\n")

    # Convert the list of dicts into a Pandas DataFrame
    df = pd.DataFrame(results)

    # Set course_code as the primary-key index of the DataFrame
    if "course_code" in df.columns:
        df.set_index("course_code", inplace=True)
    else:
        print("[WARNING] 'course_code' column missing — using default integer index.")

    # Ensure the output directory exists before saving
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    # Save to CSV
    df.to_csv(OUTPUT_CSV, encoding="utf-8-sig")   # utf-8-sig for Excel compatibility

    print(f"✅ Skills database saved to: {OUTPUT_CSV}")
    print(f"   Shape: {df.shape[0]} courses × {df.shape[1]} columns\n")
    print("DataFrame Preview:")
    print(df.head())


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    main()