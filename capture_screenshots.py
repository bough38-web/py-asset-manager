from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        print("Navigating to app...")
        page.goto("http://localhost:8501", timeout=60000)
        # Streamlit uses websockets which prevents networkidle from firing sometimes
        time.sleep(10) 
        
        # 1. Dashboard
        print("Capturing Dashboard...")
        try:
            page.screenshot(path="img_dashboard.png")
            print("Dashboard captured.")
        except Exception as e:
            print(f"Failed to capture Dashboard: {e}")
        
        # 2. Management Tab
        # Streamlit tabs are often buttons with role="tab"
        print("Switching to Management tab...")
        page.get_by_text("💎 자산 관리/운영").click()
        time.sleep(2)
        page.screenshot(path="img_management.png")
        
        # 3. Registration Tab
        print("Switching to Registration tab...")
        page.get_by_text("⚡ 빠른 등록").click()
        time.sleep(2)
        page.screenshot(path="img_registration.png")
        
        browser.close()
        print("Done!")

if __name__ == "__main__":
    run()
