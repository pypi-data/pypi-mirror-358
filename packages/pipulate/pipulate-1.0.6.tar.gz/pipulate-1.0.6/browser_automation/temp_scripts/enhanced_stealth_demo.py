#!/usr/bin/env python3
"""
Enhanced Stealth Browser Automation Demo
Comparing different stealth approaches for bot detection evasion
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
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


class StealthBrowserDemo:
    """Demonstrates different stealth approaches for browser automation"""
    
    def __init__(self):
        self.results = {}
    
    def human_like_behavior(self, driver):
        """Simulate human-like browsing behavior"""
        # Random mouse movements
        actions = ActionChains(driver)
        
        # Move mouse to random positions
        for _ in range(3):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            actions.move_by_offset(x, y)
            actions.perform()
            time.sleep(random.uniform(0.5, 1.5))
        
        # Random scrolling
        driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)});")
        time.sleep(random.uniform(1, 2))
        
        # Random page interactions
        try:
            # Try to find and hover over a random element
            elements = driver.find_elements(By.TAG_NAME, "a")[:5]
            if elements:
                element = random.choice(elements)
                ActionChains(driver).move_to_element(element).perform()
                time.sleep(random.uniform(0.5, 1))
        except:
            pass
    
    def test_detection_site(self, driver, approach_name):
        """Test the browser against bot detection sites"""
        print(f"\n--- Testing {approach_name} ---")
        
        detection_sites = [
            "https://bot.sannysoft.com/",
            "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html",
            "https://arh.antoinevastel.com/bots/areyouheadless"
        ]
        
        results = {}
        
        for site in detection_sites:
            try:
                print(f"Testing: {site}")
                driver.get(site)
                
                # Add human-like behavior
                self.human_like_behavior(driver)
                
                # Wait for page to load
                time.sleep(3)
                
                # Take screenshot for analysis
                screenshot_name = f"{approach_name.lower().replace(' ', '_')}_{site.split('/')[-1]}.png"
                driver.save_screenshot(f"pipulate/browser_automation/temp_scripts/{screenshot_name}")
                
                # Check page source for detection indicators
                page_source = driver.page_source.lower()
                
                detection_indicators = [
                    "headless",
                    "automation",
                    "webdriver",
                    "selenium",
                    "bot detected",
                    "suspicious"
                ]
                
                detected = any(indicator in page_source for indicator in detection_indicators)
                results[site] = "DETECTED" if detected else "PASSED"
                
                print(f"  Result: {results[site]}")
                
            except Exception as e:
                print(f"  Error testing {site}: {str(e)}")
                results[site] = f"ERROR: {str(e)}"
            
            time.sleep(random.uniform(2, 4))
        
        return results
    
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
            results = self.test_detection_site(driver, "Pipulate Current")
            self.results["pipulate_current"] = results
        finally:
            driver.quit()
    
    def approach_2_undetected_chromedriver(self):
        """Undetected ChromeDriver approach"""
        if not UNDETECTED_AVAILABLE:
            print("\n❌ APPROACH 2: Undetected ChromeDriver (Not Available)")
            return
        
        print("\n🤖 APPROACH 2: Undetected ChromeDriver")
        
        options = uc.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")
        
        driver = uc.Chrome(options=options, version_main=None)
        
        try:
            results = self.test_detection_site(driver, "Undetected ChromeDriver")
            self.results["undetected_chromedriver"] = results
        finally:
            driver.quit()
    
    def approach_3_selenium_stealth(self):
        """Selenium-stealth library approach"""
        if not STEALTH_AVAILABLE:
            print("\n❌ APPROACH 3: Selenium-Stealth (Not Available)")
            return
        
        print("\n🥷 APPROACH 3: Selenium-Stealth Library")
        
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        
        # Apply stealth settings
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Linux",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
        )
        
        try:
            results = self.test_detection_site(driver, "Selenium-Stealth")
            self.results["selenium_stealth"] = results
        finally:
            driver.quit()
    
    def run_comparison(self):
        """Run all available stealth approaches and compare results"""
        print("🔍 STEALTH BROWSER AUTOMATION COMPARISON")
        print("=" * 50)
        
        # Run all available approaches
        self.approach_1_pipulate_current()
        self.approach_2_undetected_chromedriver()
        self.approach_3_selenium_stealth()
        
        # Print comparison results
        print("\n📊 COMPARISON RESULTS")
        print("=" * 50)
        
        for approach, results in self.results.items():
            print(f"\n{approach.upper()}:")
            for site, result in results.items():
                print(f"  {site}: {result}")
        
        # Calculate success rates
        print("\n🏆 SUCCESS RATES")
        print("-" * 30)
        
        for approach, results in self.results.items():
            passed = sum(1 for result in results.values() if result == "PASSED")
            total = len(results)
            rate = (passed / total) * 100 if total > 0 else 0
            print(f"{approach}: {passed}/{total} ({rate:.1f}%)")


if __name__ == "__main__":
    demo = StealthBrowserDemo()
    demo.run_comparison() 