import schedule
import time
import os
import sys

# Fix Windows terminal Unicode print errors
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure the src directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.scraper.job_scraper import crawl_neu_jobs
from src.scraper.data_cleaner import process_and_save_data
from src.scraper.market_insights import MarketInsights

def run_pipeline():
    print("="*50)
    print("[INFO] STARTING DAILY NEU JOBS DATA PIPELINE")
    print("="*50)
    
    # 1. Crawl Data
    print("\n>>> Phase 1: Crawling Data...")
    raw_data = crawl_neu_jobs()
    
    if not raw_data:
        print("[WARNING] No data scraped. Pipeline aborted.")
        return
        
    # 2. Clean and Save Data
    print("\n>>> Phase 2: Cleaning Data...")
    df_clean = process_and_save_data(raw_data)
    
    # 3. Generate Market Insights
    print("\n>>> Phase 3: Generating Market Insights...")
    csv_path = os.path.join("data", "processed", "neu_jobs_clean.csv")
    insight = MarketInsights(csv_path)
    report = insight.generate_full_report()
    
    print("\n[INSIGHTS SUMMARY]")
    print(f"Total jobs by family: {report.get('Job_Counts_By_Family')}")
    print(f"Top 5 Skills: {list(report.get('Top_10_Skills', {}).keys())[:5]}")
    print("\n[INFO] PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*50)

def start_scheduler():
    print("[INFO] Automation Scheduler Started. Press Ctrl+C to exit.")
    print("[INFO] The pipeline is scheduled to run every day at 02:00 AM.")
    
    # Schedule the pipeline to run every day at 2:00 AM
    schedule.every().day.at("02:00").do(run_pipeline)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # If user passes --run-now, we run it immediately instead of waiting for scheduler
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        run_pipeline()
    else:
        # Run once immediately for the first time, then start scheduler
        print("[INFO] Running initial pipeline before starting scheduler...")
        run_pipeline()
        start_scheduler()
