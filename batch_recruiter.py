import google.generativeai as genai
import time
import csv

# 1. SETUP
# ---------------------------------------------------------
API_KEY = "AIzaSyAhleJ3ciRmf2n8youN8WjGLJSKDS4QbZg"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. THE ANALYZER FUNCTION
# ---------------------------------------------------------


def analyze_job(job_text):
    prompt = """
    You are an expert technical recruiter.
    CANDIDATE: Full Stack (Java/React), Master's in AI, F-1 Visa (Needs Sponsorship).
    RULES: 
    - REJECT if: Defense/Gov/Clearance, Citizenship Required, Wrong Tech Stack (e.g., C#, Pure Embedded).
    - SUBMIT if: Java/React match, AI/Data Engineering match, Visa friendly.
    
    Output ONLY this format: VERDICT | CONFIDENCE | SHORT_REASON
    Example: SUBMIT | 90% | Strong match for Java and AI background.
    """
    try:
        response = model.generate_content(f"{prompt}\n\nJOB:\n{job_text}")
        return response.text.strip()
    except Exception as e:
        return f"ERROR | 0% | {str(e)}"

# 3. THE BATCH LOOP
# ---------------------------------------------------------


def process_file():
    print("📂 Reading jobs.txt...")

    # Read the file and split by the separator line
    with open("jobs.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Split into a list of jobs
    job_list = raw_text.split("-----")
    print(f"found {len(job_list)} jobs to process.\n")

    # Prepare the output file (Excel compatible)
    with open("results.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Job ID", "Verdict", "Confidence", "Reason"])  # Header

        # Loop through every job
        for i, job in enumerate(job_list):
            if len(job.strip()) < 50:
                continue  # Skip empty chunks

            print(f"🤖 Processing Job #{i+1}...")
            result = analyze_job(job[:4000])  # Limit text size to save tokens

            # Save to file
            # We expect format: VERDICT | SCORE | REASON
            parts = result.split("|")
            if len(parts) == 3:
                writer.writerow(
                    [f"Job {i+1}", parts[0].strip(), parts[1].strip(), parts[2].strip()])
            else:
                writer.writerow([f"Job {i+1}", "ERROR", "0%", result])

            time.sleep(1)  # Sleep briefly to avoid hitting rate limits

    print("\n✅ DONE! Open 'results.csv' to see your shortlist.")


if __name__ == "__main__":
    process_file()
