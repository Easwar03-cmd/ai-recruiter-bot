import google.generativeai as genai

# 1. CONFIGURATION
# ---------------------------------------------------------
# Replace this with your actual API Key from Google AI Studio
API_KEY = "AIzaSyAhleJ3ciRmf2n8youN8WjGLJSKDS4QbZg"

genai.configure(api_key=API_KEY)

# We use the 'gemini-1.5-flash' model because it is fast and free/cheap
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. YOUR "MASTER RULES"
# ---------------------------------------------------------
# This is the prompt we have been refining together.
system_rules = """
You are an expert technical recruiter screening jobs for a candidate.
CANDIDATE PROFILE:
- Role: Full Stack Developer (Java/Spring Boot + React).
- Education: Master's in AI (can pivot to AI roles).
- Visa: F-1 OPT (Requires sponsorship eventually).
- Exclusions: NO Defense, NO Government Clearance, NO "Citizenship Required".

INSTRUCTIONS:
Analyze the job description below.
Output ONLY a JSON format with this structure:
{
  "verdict": "SUBMIT" or "REJECT",
  "confidence_score": (0-100),
  "reason": "Short explanation of why."
}
"""

# 3. THE FUNCTION (The Brain)
# ---------------------------------------------------------


def analyze_job(job_text):
    print("🤖 Analyzing job...")

    # Combine rules + the specific job text
    full_prompt = f"{system_rules}\n\nJOB DESCRIPTION:\n{job_text}"

    # Send to Gemini
    response = model.generate_content(full_prompt)

    # Return the AI's answer
    return response.text


# 4. TEST IT
# ---------------------------------------------------------
if __name__ == "__main__":
    # Let's test it with a fake job description
    test_job = """
    We are looking for a Java Developer with React experience.
    Must be a US Citizen due to government clearance requirements.
    Location: Washington DC.
    """

    result = analyze_job(test_job)
    print("\n--- AI RESULT ---")
    print(result)
