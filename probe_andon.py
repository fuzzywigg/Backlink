from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def probe_andon_structure():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    print("🕵️ PROBE: Launching Headless Browser to https://andonlabs.com/evals/radio ...")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://andonlabs.com/evals/radio")
        time.sleep(5) # Allow React to hydrate
        
        print("\n--- PAGE TEXT DUMP (First 2000 chars) ---")
        text = driver.find_element(By.TAG_NAME, "body").text
        print(text[:2000])
        print("----------------------------------------\n")
        
        # Try to find common music player elements or just dump all div classes?
        # Let's simple dump the page text to see if the song title is visible in plain text
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    probe_andon_structure()
