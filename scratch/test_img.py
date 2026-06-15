import re
from bs4 import BeautifulSoup

with open('test_neu.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
jobs = soup.select('.twm-jobs-grid-style1')
if jobs:
    first_job = jobs[0]
    img = first_job.select_one('img')
    if img:
        print("IMG tag found:", img)
    else:
        print("No IMG found in the job card.")
        
    print("\n--- HTML snippet ---")
    print(str(first_job)[:1500])
