from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import random  # <--- Make sure this is here!


def run_debug_test():
    print("🔹 STEP 1: Setting up options...")
    user_data_dir = r"C:\Users\easwa\python_app\chrome_bot_profile"

    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument("--remote-debugging-port=9222")

    driver = None

    try:
        print("🔹 STEP 2: Launching Chrome Driver...")
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)
        print("✅ Driver launched successfully.")

        url = "https://www.linkedin.com/jobs"  # We test with a generic page first
        print(f"🔹 STEP 3: Going to URL: {url}")
        driver.get(url)

        print("🔹 STEP 4: Waiting for page load (5 seconds)...")
        time.sleep(5)

        print("🔹 STEP 5: Attempting to scroll...")
        driver.execute_script("window.scrollTo(0, 500);")
        print("✅ Scroll successful.")

        print("🔹 STEP 6: Looking for the <body /> tag...")
        body = driver.find_element(By.TAG_NAME, "body")
        print(f"✅ Found body tag. Text length: {len(body.text)} characters.")

        print("🎉 SUCCESS! No errors found during execution.")

    except Exception as e:
        print("\n❌ CRITICAL ERROR CAUGHT:")
        print(f"--> {e}")  # This prints the exact error message

        if driver:
            print("📸 Attempting to take emergency screenshot...")
            try:
                driver.save_screenshot("debug_crash.png")
                print("✅ Screenshot saved: debug_crash.png")
            except Exception as screenshot_error:
                print(f"⚠️ Could not save screenshot: {screenshot_error}")

    finally:
        print("🔹 STEP 7: Closing driver...")
        if driver:
            driver.quit()
        print("✅ Done.")


if __name__ == "__main__":
    run_debug_test()
