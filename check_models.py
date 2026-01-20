import google.generativeai as genai

# PASTE YOUR API KEY HERE
API_KEY = "AIzaSyAhleJ3ciRmf2n8youN8WjGLJSKDS4QbZg"
genai.configure(api_key=API_KEY)

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
