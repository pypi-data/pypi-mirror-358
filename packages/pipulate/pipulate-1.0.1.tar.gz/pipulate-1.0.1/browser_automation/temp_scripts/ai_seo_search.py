#!/usr/bin/env python3
"""
Disposable script to search Google for "ai seo software"
This is a temp script - not committed to git
"""

import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def simple_google_search(query):
    """Simple Google search without complex DOM processing"""
    
    # Setup Chrome with minimal options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"🔍 Searching Google for: '{query}'")
        
        # Navigate to Google
        driver.get("https://www.google.com")
        time.sleep(3)
        
        # Find search box and enter query
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        
        print("⏳ Waiting for results (may hit captcha)...")
        time.sleep(5)  # Give time for captcha or results
        
        # Check if we got results or captcha
        try:
            results_container = driver.find_element(By.ID, "search")
            print("✅ Search results loaded!")
        except:
            print("🤖 Likely hit a captcha - this is expected with automated searches")
            print("📸 Taking screenshot of current state...")
            driver.save_screenshot("../looking_at/google_captcha_screenshot.png")
            
        # Save page source regardless
        with open("../looking_at/ai_seo_search_source.html", "w") as f:
            f.write(driver.page_source)
        
        print("📁 Page source saved to browser_automation/looking_at/")
        
        # Try to extract results if available
        results = []
        try:
            result_elements = driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            for i, element in enumerate(result_elements[:10]):
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, "h3")
                    link_elem = element.find_element(By.CSS_SELECTOR, "a")
                    
                    title = title_elem.text
                    url = link_elem.get_attribute("href")
                    
                    if title and url:
                        results.append({
                            "position": i + 1,
                            "title": title,
                            "url": url
                        })
                        print(f"{i+1}. {title}")
                        print(f"   {url}")
                        print()
                except:
                    continue
            
            if results:
                with open("../looking_at/ai_seo_search_results.json", "w") as f:
                    json.dump({
                        "query": query,
                        "results_count": len(results),
                        "results": results
                    }, f, indent=2)
                print(f"📊 Found {len(results)} results")
            else:
                print("📝 No results extracted (likely captcha)")
                
        except Exception as e:
            print(f"⚠️ Could not extract results: {e}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    
    finally:
        driver.quit()

if __name__ == "__main__":
    simple_google_search("ai seo software")
