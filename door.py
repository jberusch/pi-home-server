"""
Door automation using Playwright.
Handles browser interaction with Avigilon to open doors.
"""
import logging
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError
from auth import SessionManager
from config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DoorOpener:
    """Handles door opening automation via browser."""

    def __init__(self):
        self.session_manager = SessionManager()
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None

    def start(self):
        """Initialize browser and load session."""
        if self.browser:
            logger.warning("Browser already started")
            return

        logger.info("Starting browser...")
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()

        # Load saved cookies if they exist
        if self.session_manager.cookies_exist():
            self.session_manager.load_cookies(self.context)
            logger.info("Session loaded from cookies")
        else:
            logger.warning("No saved session found")

    def stop(self):
        """Close browser."""
        if self.browser:
            self.browser.close()
            self.browser = None
            self.context = None
            logger.info("Browser closed")

    def check_session(self) -> bool:
        """Check if current session is valid."""
        if not self.context:
            return False
        return self.session_manager.is_session_valid(self.context)

    def open_door(self) -> tuple[bool, str]:
        """
        Open the door by clicking the button.

        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.browser or not self.context:
            return False, "Browser not initialized"

        page: Page | None = None
        try:
            # Create new page
            page = self.context.new_page()
            logger.info(f"Navigating to {config.avigilon_url}")

            # Navigate to door unlock page
            page.goto(config.avigilon_url, timeout=15000)

            # Check if we got redirected to login (session expired)
            current_url = page.url
            if "login" in current_url.lower() or "signin" in current_url.lower():
                logger.error("Session expired - redirected to login")
                return False, "session_expired"

            # Wait for page to be fully loaded
            page.wait_for_load_state("networkidle", timeout=10000)

            # Find and click the door button (case-insensitive text match)
            logger.info(f"Looking for button with text: {config.door_button_text}")
            button = page.get_by_text(config.door_button_text, exact=False)

            # Check if button exists
            if button.count() == 0:
                logger.error(f"Button '{config.door_button_text}' not found on page")
                return False, "button_not_found"

            # Click the button
            logger.info("Clicking door button...")
            button.first.click()

            # Wait a moment for the action to complete
            page.wait_for_timeout(2000)

            # Check for success indicators (adjust based on actual Avigilon behavior)
            # This might be a success message, button state change, etc.
            # For now, assume success if no error was thrown
            logger.info("Door button clicked successfully")
            return True, "success"

        except TimeoutError as e:
            logger.error(f"Timeout error: {e}")
            return False, "timeout"
        except Exception as e:
            logger.error(f"Unexpected error opening door: {e}")
            return False, f"error: {str(e)}"
        finally:
            if page:
                page.close()


# Global door opener instance
_door_opener: DoorOpener | None = None


def get_door_opener() -> DoorOpener:
    """Get or create global door opener instance."""
    global _door_opener
    if _door_opener is None:
        _door_opener = DoorOpener()
        _door_opener.start()
    return _door_opener


def open_door() -> tuple[bool, str]:
    """
    Convenience function to open the door.

    Returns:
        tuple: (success: bool, message: str)
    """
    opener = get_door_opener()
    return opener.open_door()


def check_status() -> dict:
    """
    Check system status.

    Returns:
        dict: Status information
    """
    opener = get_door_opener()
    session_valid = opener.check_session()

    return {
        "browser_running": opener.browser is not None,
        "session_valid": session_valid,
        "cookies_exist": opener.session_manager.cookies_exist(),
    }


if __name__ == "__main__":
    # Test door opening when run directly
    print("Testing door opener...")
    print("=" * 60)

    status = check_status()
    print(f"Status: {status}")
    print()

    if not status["cookies_exist"]:
        print("No session found. Run 'python auth.py' first to authenticate.")
        exit(1)

    if not status["session_valid"]:
        print("Session is invalid. Run 'python auth.py' to re-authenticate.")
        exit(1)

    print("Attempting to open door...")
    success, message = open_door()

    if success:
        print(f"✓ Success: {message}")
        exit(0)
    else:
        print(f"✗ Failed: {message}")
        exit(1)
