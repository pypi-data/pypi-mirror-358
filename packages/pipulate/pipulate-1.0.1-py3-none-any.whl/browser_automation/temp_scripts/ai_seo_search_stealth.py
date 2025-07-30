#!/usr/bin/env python3
"""
AI SEO Software Search with Enhanced Stealth
Performs Google search using different stealth approaches
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException

# Try importing optional stealth libraries
try:
    import undetected_chromedriver as uc
    UNDETECTED_AVAILABLE = True
except ImportError:
    UNDETECTED_AVAILABLE = False
    print("undetected-chromedriver not available")

try:
    from selenium_stealth import stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    print("selenium-stealth not available")


class GoogleSearchStealth:
    """Performs Google search with different stealth approaches"""
    
    def __init__(self):
        self.search_query = "ai seo software"
        self.results = {}
    
    def human_like_behavior(self, driver):
        """Simulate human-like browsing behavior"""
        # Random mouse movements
        actions = ActionChains(driver)
        
        # Move mouse to random positions
        for _ in range(2):
            x = random.randint(100, 400)
            y = random.randint(100, 300)
            actions.move_by_offset(x, y)
            actions.perform()
            time.sleep(random.uniform(0.3, 0.8))
        
        # Random scrolling
        driver.execute_script(f"window.scrollTo(0, {random.randint(50, 200)});")
        time.sleep(random.uniform(0.5, 1.0))
    
    def perform_google_search(self, driver, approach_name):
        """Perform Google search and capture results"""
        print(f"\n--- {approach_name} Google Search ---")
        
        try:
            # Navigate to Google
            print("Navigating to Google...")
            driver.get("https://www.google.com")
            
            # Add human-like behavior
            self.human_like_behavior(driver)
            
            # Wait for search box and search
            wait = WebDriverWait(driver, 10)
            
            # Try different search box selectors
            search_selectors = [
                "input[name='q']",
                "textarea[name='q']",
                "#APjFqb",
                ".gLFyf"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"Found search box with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not search_box:
                print("❌ Could not find search box")
                return {"status": "FAILED", "reason": "Search box not found"}
            
            # Clear and type search query
            search_box.clear()
            time.sleep(random.uniform(0.2, 0.5))
            
            # Type with human-like delays
            for char in self.search_query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(0.5, 1.0))
            
            # Submit search
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results
            time.sleep(3)
            
            # Check for CAPTCHA or blocking
            page_source = driver.page_source.lower()
            if any(indicator in page_source for indicator in ['captcha', 'unusual traffic', 'blocked']):
                print("🤖 CAPTCHA or blocking detected")
                # Save screenshot for analysis
                screenshot_name = f"{approach_name.lower().replace(' ', '_')}_captcha.png"
                driver.save_screenshot(f"{screenshot_name}")
                return {"status": "BLOCKED", "reason": "CAPTCHA/blocking detected"}
            
            # Extract search results
            results = []
            try:
                # Try different result selectors
                result_selectors = [
                    "div.g",
                    ".g",
                    "[data-sokoban-container]",
                    ".yuRUbf"
                ]
                
                search_results = []
                for selector in result_selectors:
                    try:
                        search_results = driver.find_elements(By.CSS_SELECTOR, selector)
                        if search_results:
                            print(f"Found {len(search_results)} results with selector: {selector}")
                            break
                    except:
                        continue
                
                # Extract result information
                for i, result in enumerate(search_results[:10]):  # Top 10 results
                    try:
                        # Try to extract title and URL
                        title_elem = result.find_element(By.CSS_SELECTOR, "h3")
                        title = title_elem.text if title_elem else "No title"
                        
                        link_elem = result.find_element(By.CSS_SELECTOR, "a")
                        url = link_elem.get_attribute("href") if link_elem else "No URL"
                        
                        results.append({
                            "position": i + 1,
                            "title": title,
                            "url": url
                        })
                    except Exception as e:
                        print(f"Error extracting result {i+1}: {str(e)}")
                        continue
                
                # Save screenshot of results
                screenshot_name = f"{approach_name.lower().replace(' ', '_')}_results.png"
                driver.save_screenshot(f"{screenshot_name}")
                
                # Save page source for analysis
                source_name = f"{approach_name.lower().replace(' ', '_')}_source.html"
                with open(f"{source_name}", 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                
                print(f"✅ Successfully extracted {len(results)} search results")
                return {"status": "SUCCESS", "results": results, "total_results": len(results)}
                
            except Exception as e:
                print(f"❌ Error extracting results: {str(e)}")
                return {"status": "ERROR", "reason": str(e)}
                
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
            return {"status": "ERROR", "reason": str(e)}
    
    def approach_1_pipulate_current(self):
        """Current Pipulate approach - sophisticated CDP-based stealth"""
        print("\n🎭 APPROACH 1: Current Pipulate Method (CDP-based)")
        
        options = webdriver.ChromeOptions()
        
        # Stealth options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Experimental options for stealth
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent spoofing
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=options)
        
        # CDP script injection for advanced stealth
        stealth_script = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        window.chrome = {
            runtime: {},
        };
        
        Object.defineProperty(navigator, 'permissions', {
            get: () => ({
                query: () => Promise.resolve({ state: 'granted' }),
            }),
        });
        """
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_script
        })
        
        try:
            result = self.perform_google_search(driver, "Pipulate Current")
            self.results["pipulate_current"] = result
        finally:
            driver.quit()
    
    def run_search_comparison(self):
        """Run Google search with Pipulate's current stealth approach only"""
        print(f"🔍 GOOGLE SEARCH: '{self.search_query}'")
        print("=" * 50)
        
        # Run Pipulate's current approach
        self.approach_1_pipulate_current()
        
        # Print results
        print("\n📊 SEARCH RESULTS")
        print("=" * 50)
        
        result = self.results.get("pipulate_current", {})
        print(f"Status: {result.get('status', 'UNKNOWN')}")
        
        if result.get('status') == 'SUCCESS':
            print(f"Results Found: {result.get('total_results', 0)}")
            
            # Show all results
            for search_result in result.get('results', []):
                print(f"{search_result.get('position', 0)}. {search_result.get('title', 'No title')}")
                print(f"   {search_result.get('url', 'No URL')}")
                print()
        
        elif result.get('reason'):
            print(f"Reason: {result.get('reason')}")
        
        print("\n📁 Files generated:")
        if result.get('status') in ['SUCCESS', 'BLOCKED']:
            print("  - pipulate_current_results.png (screenshot)")
            print("  - pipulate_current_source.html (page source)")


if __name__ == "__main__":
    searcher = GoogleSearchStealth()
    searcher.run_search_comparison() 