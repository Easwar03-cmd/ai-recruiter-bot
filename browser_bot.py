from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# This command downloads the correct driver for your Chrome automatically
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Go to a website
print("🚀 Opening Browser...")
driver.get("https://www.google.com")

# Wait 3 seconds so you can see it
time.sleep(3)

# Print the title of the page
print(f"I am looking at: {driver.title}")

# Close the browser
driver.quit()
