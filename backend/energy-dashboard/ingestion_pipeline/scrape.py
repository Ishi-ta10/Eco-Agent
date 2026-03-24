from playwright.sync_api import sync_playwright
import json

captured_data = []

def capture_api(response):
    try:
        # Capture XHR / fetch requests
        if response.request.resource_type in ["xhr", "fetch"]:
            print("\n📡 API URL:", response.url)

            try:
                data = response.json()

                print("📊 DATA:")
                print(json.dumps(data, indent=2))

                # ✅ Store clean structured data
                captured_data.append({
                    "url": response.url,
                    "data": data
                })

            except:
                print("⚠️ Not JSON response")

    except Exception as e:
        print("Error:", e)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Attach listener BEFORE navigation
    page.on("response", capture_api)

    print("Opening site...")
    page.goto("https://cloud.suryalog.com")

    print("Attempting automatic login...")
    # Wait for login form to appear
    page.wait_for_selector('#loginId', timeout=10000)
    
    # Fill in credentials
    page.fill('#loginId', "MAQ_Software")
    page.wait_for_timeout(500)
    page.fill('#password', "MAQ@1234")
    page.wait_for_timeout(500)
    
    # Click login button using the correct ID
    page.click('#btnlogin')
    print("Login button clicked, waiting for page to load...")
    
    # Wait for page to navigate after login
    page.wait_for_timeout(8000)

    print("Waiting for APIs...")
    page.wait_for_timeout(10000)

    print("Triggering interaction...")
    page.mouse.click(100, 100)
    page.wait_for_timeout(5000)

    print("Reloading...")
    page.reload()
    page.wait_for_timeout(10000)

    # ✅ Save all captured data into separate file
    with open("captured_api_data.json", "w") as f:
        json.dump(captured_data, f, indent=2)

    print("\n✅ Data saved to captured_api_data.json")

    browser.close()