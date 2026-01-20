import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import csv
import random
from pypdf import PdfReader
from urllib.parse import quote

# 1. CONFIGURATION
# ---------------------------------------------------------
API_KEY = "GEMINI_API_KEY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')


def search_linkedin_jobs(driver, keyword, location, max_jobs=10):
    print(f"\n🔎 Searching for '{keyword}' in '{location}'...")

    # 1. CONSTRUCT SEARCH URL
    # We filter by "Date Posted: Past 24 hours" (f_TPR=r86400) to get fresh jobs
    safe_keyword = quote(keyword)
    safe_loc = quote(location)
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={safe_keyword}&location={safe_loc}&f_TPR=r86400"

    driver.get(search_url)
    time.sleep(5)  # Let results load

    collected_urls = set()

    try:
        # 2. FIND THE JOB LIST (The scrollable sidebar)
        # LinkedIn changes class names often, but 'jobs-search-results-list' is common
        # We try to scroll the whole window first, which usually triggers the list load
        print("   📜 Scrolling through search results...")

        last_height = driver.execute_script(
            "return document.body.scrollHeight")

        while len(collected_urls) < max_jobs:
            # Scroll down a bit
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Find all job links visible on screen
            # They usually look like: /jobs/view/123456789/
            links = driver.find_elements(
                By.XPATH, "//a[contains(@href, '/jobs/view/') or contains(@href, '/jobs/collections/recommended/')]")

            for link in links:
                href = link.get_attribute("href")
                # CLEAN THE URL (Remove tracking junk)
                if "currentJobId" in href:
                    # Extract ID from parameter
                    job_id = href.split("currentJobId=")[1].split("&")[0]
                    clean_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
                    collected_urls.add(clean_url)
                elif "/jobs/view/" in href:
                    # Extract ID from path
                    job_id = href.split("/jobs/view/")[1].split("/")[0]
                    clean_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
                    collected_urls.add(clean_url)

            print(f"   👀 Found {len(collected_urls)} unique jobs so far...")

            if len(collected_urls) >= max_jobs:
                break

            # Stop if scrolling doesn't load new stuff
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                print("   ⚠️ End of results reached.")
                break
            last_height = new_height

    except Exception as e:
        print(f"   ❌ Search Error: {e}")

    return list(collected_urls)[:max_jobs]


def get_resume_text(pdf_path="resume.pdf"):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except:
        return "ERROR: Could not read resume.pdf"


def get_selenium_text(url):
    print(f"🚀 Launching Browser for: {url}")
    driver = None

    try:
        # 1. SETUP (Use your Profile!)
        options = webdriver.ChromeOptions()
        user_data_dir = r"C:\Users\easwa\python_app\chrome_bot_profile"
        options.add_argument(f"user-data-dir={user_data_dir}")
        options.add_argument("--remote-debugging-port=9222")
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--profile-directory=Default")
        # options.add_argument("--start-minimized")
        # options.add_argument("--headless=new")
        # Add this line right after the headless line
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)

        # 2. NAVIGATE
        driver.get(url)
        # print("⚠️  ACTION NEEDED: Check the browser!")
        # print("1. If you see a Login screen, Log in manually.")
        # print("2. If a Captcha appears, solve it.")
        # input("👉 Press ENTER in this terminal once the Job Description is visible...")
        time.sleep(random.uniform(3, 5))

        # 3. EXPAND "SEE MORE"
        try:
            # Try multiple selectors for the button
            buttons = driver.find_elements(
                By.CLASS_NAME, "jobs-description__footer-button")
            if buttons:
                driver.execute_script("arguments[0].click();", buttons[0])
                print("   👉 Clicked 'See More'...")
                time.sleep(1)
        except:
            pass

        # 4. THE SNIPER: Extract ONLY the Job Description
        # We try 3 specific strategies to find the Clean Text.

        clean_text = ""

        # Strategy A: Look for the main ID (Most reliable for logged-in users)
        try:
            box = driver.find_element(By.ID, "job-details")
            clean_text = box.text
            print("   🎯 Target Locked: Found 'job-details' container.")
        except:
            # Strategy B: Look for class name used in some views
            try:
                box = driver.find_element(
                    By.CLASS_NAME, "jobs-description__content")
                clean_text = box.text
                print("   🎯 Target Locked: Found 'jobs-description__content'.")
            except:
                # Strategy C: Your Idea -> Find "About the job" header and grab parent
                print(
                    "   ⚠️ specific container not found, falling back to full body search...")
                clean_text = driver.find_element(By.TAG_NAME, "body").text

        # Validate
        clean_text = ' '.join(clean_text.split())
        print(f"   📄 Extracted {len(clean_text)} characters of CLEAN JD.")

        return clean_text[:8000]

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        if driver:
            driver.save_screenshot("crash_error.png")
        return f"ERROR: {str(e)}"

    finally:
        if driver:
            driver.quit()

# 3. THE BRAIN (Standard Logic)
# ---------------------------------------------------------


def analyze_job(job_text, resume_text):
    prompt = f"""
    You are a Senior Technical Recruiter performing a Gap Analysis.
    
    --- INPUT DATA ---
    CANDIDATE RESUME:
    {resume_text}
    
    JOB DESCRIPTION (JD):
    {job_text}
    
    --- INSTRUCTIONS ---
    Step 1: Extract the top 5 HARD SKILLS required by the JD (e.g., Java, AWS, Python, 5+ years exp).
    Step 2: Compare each skill against the Resume.
    Step 3: Check for "Knock-out" factors (Citizenship, Clearance).
    
    --- SCORING LOGIC (Pure Math) ---
    Start with 100 Points.
    - REJECT (-100 pts) if: Security Clearance, US Citizenship Required, or Tech Stack is completely irrelevant (e.g., Embedded C, .NET).
    - DEDUCT 15 pts for each missing KEY technical skill (e.g., JD wants AWS, Resume has none).
    - DEDUCT 20 pts if Experience gap is huge (e.g., JD wants 8 years, Resume has 2).
    - ADD 5 pts if Resume has "Nice to have" skills mentioned in JD.
    - Max score to 100.
    
    --- OUTPUT FORMAT ---
    Output ONLY this single line (no bolding, no markdown):
    VERDICT | SCORE | MATCHING_SKILLS | MISSING_SKILLS
    
    Example Output:
    SUBMIT | 85 | Java, Spring, SQL | AWS, Kubernetes
    REJECT | 0 | None | US Citizenship Required
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"ERROR | 0 | AI Error | {str(e)}"

# 4. MAIN EXECUTION
# ---------------------------------------------------------


def process_urls():
    # 1. SETUP: Create a folder to store the text files
    if not os.path.exists("scraped_jobs"):
        os.makedirs("scraped_jobs")

    # 2. LOAD RESUME
    print("📂 Reading 'resume.pdf'...")
    my_resume = get_resume_text("resume.pdf")

    if "ERROR" in my_resume or len(my_resume) < 100:
        print("❌ CRITICAL: Put your 'resume.pdf' in this folder!")
        return
    print("\nSelect Mode:")
    print("1. Use 'urls.txt' (Manual Mode)")
    print("2. Auto-Search LinkedIn (Auto Mode)")
    choice = input("👉 Enter 1 or 2: ")

    urls = []

    if choice == "1":
        with open("urls.txt", "r") as f:
            urls = [line.strip() for line in f if line.strip()]

    elif choice == "2":
        keyword = input("👉 Enter Job Role (e.g., Java Developer): ")
        location = input("👉 Enter Location (e.g., United States): ")
        limit = int(input("👉 How many jobs to fetch? (Rec: 10-20): "))

        # We need to launch the browser ONCE here to do the searching
        options = webdriver.ChromeOptions()
        user_data_dir = r"C:\Users\easwa\python_app\chrome_bot_profile"
        options.add_argument(f"user-data-dir={user_data_dir}")
        options.add_argument("--start-minimized")
        # Add your other "human" options here (excludeSwitches, etc.)

        search_driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)

        try:
            urls = search_linkedin_jobs(
                search_driver, keyword, location, limit)
        finally:
            search_driver.quit()  # Close search window

        print(f"\n✅ Collected {len(urls)} jobs. Starting Analysis...\n")
    # --------------------------
    # 3. READ URLS
    # with open("urls.txt", "r") as f:
    #     urls = [line.strip() for line in f if line.strip()]

    print(f"Found {len(urls)} links to process.\n")

    # 4. START PROCESSING
    with open("smart_results.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Header includes a reference to the text file now
        writer.writerow(["Job ID", "URL", "Verdict", "Match %",
                        "Matching Skills", "Missing Skills"])

        for i, url in enumerate(urls):

            if i > 0 and i % 10 == 0:
                print("\n☕ Taking a 'Coffee Break' for 2 minutes to stay safe...")
                time.sleep(120)

            job_id = i + 1
            print(f"\nProcessing Job #{job_id}...")

            # A. SCRAPE JD
            jd_text = get_selenium_text(url)

            # --- NEW: SAVE THE TEXT FILE ---
            # We save the raw text so you can review it later
            text_filename = f"scraped_jobs/job_{job_id}.txt"
            with open(text_filename, "w", encoding="utf-8") as text_file:
                text_file.write(f"SOURCE URL: {url}\n\n")
                text_file.write(jd_text)
            print(f"   💾 Text saved to {text_filename}")
            # -------------------------------

            if jd_text.startswith("ERROR"):
                writer.writerow(
                    [job_id, url, "SCRAPE_FAIL", "0", "N/A", jd_text])
                continue

            # B. ANALYZE
            result = analyze_job(jd_text, my_resume)

            parts = result.split("|")
            if len(parts) >= 4:
                verdict = parts[0].strip()
                score = parts[1].strip()
                matching = parts[2].strip()
                missing = parts[3].strip()

                print(f"   ✅ Verdict: {verdict} | Score: {score}%")
                writer.writerow(
                    [job_id, url, verdict, score, matching, missing])
            else:
                writer.writerow(
                    [job_id, url, "FORMAT_ERROR", "0", "N/A", result])

            delay = random.uniform(15, 30)
            print(f"   ⏳ Waiting {int(delay)} seconds before next job...")
            time.sleep(delay)

    print("\n✅ DONE! Check 'smart_results.csv' and the 'scraped_jobs' folder.")


if __name__ == "__main__":
    process_urls()
