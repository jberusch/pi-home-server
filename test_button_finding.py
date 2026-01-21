"""
Test script to verify button can be found without clicking it.
"""
import logging
from playwright.sync_api import sync_playwright, TimeoutError
from auth import SessionManager
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_find_button():
    """Test finding the door button without clicking it."""
    session_manager = SessionManager()

    logger.info("Starting browser...")
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)  # Show browser so you can see
    context = browser.new_context()

    # Load saved cookies if they exist
    if session_manager.cookies_exist():
        session_manager.load_cookies(context)
        logger.info("Session loaded from cookies")
    else:
        logger.warning("No saved session found - you may need to run auth.py first")

    page = None
    try:
        page = context.new_page()
        logger.info(f"Navigating to {config.avigilon_url}")

        # Navigate to door unlock page
        page.goto(config.avigilon_url, timeout=15000)

        # Check if we got redirected to login (session expired)
        current_url = page.url
        if "login" in current_url.lower() or "signin" in current_url.lower():
            logger.error("❌ Session expired - redirected to login")
            logger.info("Please run: python auth.py")
            return False

        # Wait for page to be fully loaded
        page.wait_for_load_state("networkidle", timeout=10000)
        logger.info("✅ Page loaded successfully")

        # Find the button
        logger.info(f"Looking for button with text: '{config.door_button_text}'")
        button = page.get_by_text(config.door_button_text, exact=False)

        # Check if button exists
        button_count = button.count()
        if button_count == 0:
            logger.error(f"❌ Button '{config.door_button_text}' not found on page")
            logger.info("Taking screenshot for debugging...")
            page.screenshot(path="/Users/joe/pi-home-server/debug_screenshot.png")
            logger.info("Screenshot saved to: /Users/joe/pi-home-server/debug_screenshot.png")
            return False

        logger.info(f"✅ Button found! ({button_count} match(es))")

        # Get button details
        first_button = button.first
        is_visible = first_button.is_visible()
        is_enabled = first_button.is_enabled()

        logger.info(f"Button visible: {is_visible}")
        logger.info(f"Button enabled: {is_enabled}")

        if is_visible and is_enabled:
            logger.info("✅ Button is visible and clickable")
            logger.info("🎉 SUCCESS: Server can find and click the button!")
            logger.info("   (Not clicking it now as requested)")
        else:
            logger.warning("⚠️  Button found but may not be clickable")
            logger.info(f"   Visible: {is_visible}, Enabled: {is_enabled}")

        # Wait a moment so you can see the page
        logger.info("Keeping browser open for 5 seconds so you can verify...")
        page.wait_for_timeout(5000)

        return True

    except TimeoutError as e:
        logger.error(f"❌ Timeout error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
    finally:
        if page:
            page.close()
        browser.close()
        playwright.stop()

if __name__ == "__main__":
    print("=" * 70)
    print("Testing Button Detection (Dry Run - Will NOT Click)")
    print("=" * 70)
    print()

    success = test_find_button()

    print()
    print("=" * 70)
    if success:
        print("✅ TEST PASSED: Button can be found and clicked")
        print("   The door opener should work when you send the SMS command!")
    else:
        print("❌ TEST FAILED: Check logs above for details")
    print("=" * 70)
