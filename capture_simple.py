from playwright.sync_api import sync_playwright
import time

def run():
    print("Launching browser...")
    with sync_playwright() as p:
        # standard args to avoid crashes in some environments
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        print("Navigating to app...")
        try:
            page.goto("http://localhost:8501", timeout=60000)
            time.sleep(10) # Wait for Streamlit
            
            print("Capturing Dashboard V2...")
            page.screenshot(path="dashboard_v2.png")
            print("Dashboard V2 captured successfully.")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
