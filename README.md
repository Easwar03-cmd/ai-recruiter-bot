# 🤖 AI Recruiter: Automated Job Screening Bot

This Python bot automates the job application process by scraping LinkedIn, parsing Job Descriptions (JDs), and performing a "Gap Analysis" against your actual PDF Resume using Google Gemini AI.

## 🚀 Features
* **Smart Scraping:** Bypasses "See More" buttons and extracts clean JD text.
* **Resume Matching:** Uses LLM (Gemini 1.5) to compare your local `resume.pdf` against the JD.
* **Auto-Login:** Saves session cookies so you don't have to log in every time.
* **Stealth Mode:** Mimics human behavior to avoid detection.
* **Reporting:** Generates a CSV report with "Match Score" and "Missing Skills".

## 🛠️ Setup
1.  **Clone the repo**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/ai-recruiter-bot.git](https://github.com/YOUR_USERNAME/ai-recruiter-bot.git)
    cd ai-recruiter-bot
    ```
2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Add your Resume**
    * Rename your resume to `resume.pdf` and place it in the project folder.
4.  **Configure API Key**
    * Open `selenium_recruiter.py` and add your Gemini API Key.

## 🏃 Usage
Run the script:
```bash
python selenium_recruiter.py