import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import csv
import time

# 1. SETUP
# ---------------------------------------------------------
API_KEY = "AIzaSyAhleJ3ciRmf2n8youN8WjGLJSKDS4QbZg"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. THE SCRAPER (The New Part!)
# ---------------------------------------------------------


def get_website_text(url):
    print(f"🌍 Visiting: {url}")
    try:
        # We need a 'User-Agent' so websites think we are a browser, not a bot
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            # Parse the HTML to just get the text (no code/tags)
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator=' ')

            # Clean up the text (remove extra white space)
            clean_text = ' '.join(text.split())
            return clean_text[:8000]  # Limit to 8000 chars to save AI tokens
        else:
            return f"ERROR: Could not fetch page (Status {response.status_code})"

    except Exception as e:
        return f"ERROR: {str(e)}"

# 3. THE BRAIN (Same as before)
# ---------------------------------------------------------


def analyze_job(job_text):
    prompt = """
    You are an expert technical recruiter.
    CANDIDATE: Full Stack (Java/React), Master's in AI, F-1 Visa (Needs Sponsorship).
    RULES: 
    - REJECT if: Defense/Gov/Clearance, Citizenship Required, Wrong Tech Stack.
    - SUBMIT if: Java/React match, AI/Data Engineering match, Visa friendly.
    
    Output ONLY this format: VERDICT | CONFIDENCE | REASON
    """
    try:
        response = model.generate_content(
            f"{prompt}\n\nJOB CONTENT:\n{job_text}")
        return response.text.strip()
    except Exception as e:
        return f"ERROR | 0% | AI Error: {str(e)}"

# 4. MAIN LOOP
# ---------------------------------------------------------


def process_urls():
    # Read the URLs from file
    with open("urls.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"Found {len(urls)} links to process.\n")

    with open("scraped_results.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["URL", "Verdict", "Confidence", "Reason"])  # Header

        for url in urls:
            # A. SCRAPE
            text_content = get_website_text(url)

            # If scraping failed, log it and skip AI
            if text_content.startswith("ERROR"):
                writer.writerow([url, "SCRAPE_FAIL", "0%", text_content])
                continue

            # B. ANALYZE
            print("   🤖 Analyzing content...")
            result = analyze_job(text_content)

            # C. SAVE
            parts = result.split("|")
            if len(parts) == 3:
                writer.writerow(
                    [url, parts[0].strip(), parts[1].strip(), parts[2].strip()])
            else:
                writer.writerow([url, "AI_FORMAT_ERROR", "0%", result])

            # Be polite to servers, wait 2 seconds between requests
            time.sleep(2)

    print("\n✅ DONE! Check 'scraped_results.csv'")


if __name__ == "__main__":
    process_urls()
