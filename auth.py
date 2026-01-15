"""
Session management for Avigilon authentication.
Handles saving/loading browser cookies for persistent sessions.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext
from config import config


class SessionManager:
    """Manages persistent browser sessions with Avigilon."""

    def __init__(self):
        self.cookies_file = Path(config.cookies_file)

    def cookies_exist(self) -> bool:
        """Check if saved cookies file exists."""
        return self.cookies_file.exists()

    def save_cookies(self, context: BrowserContext):
        """Save browser cookies to file."""
        cookies = context.cookies()
        with open(self.cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)
        # Set restrictive file permissions (owner read/write only)
        os.chmod(self.cookies_file, 0o600)
        print(f"Cookies saved to {self.cookies_file}")

    def load_cookies(self, context: BrowserContext):
        """Load browser cookies from file."""
        if not self.cookies_exist():
            return False

        try:
            with open(self.cookies_file, "r") as f:
                cookies = json.load(f)
            context.add_cookies(cookies)
            print(f"Cookies loaded from {self.cookies_file}")
            return True
        except Exception as e:
            print(f"Failed to load cookies: {e}")
            return False

    def clear_cookies(self):
        """Delete saved cookies file."""
        if self.cookies_exist():
            self.cookies_file.unlink()
            print("Cookies cleared")

    def is_session_valid(self, context: BrowserContext) -> bool:
        """
        Check if current session is valid by navigating to Avigilon URL.
        Returns True if we can access the page, False if redirected to login.
        """
        try:
            page = context.new_page()
            page.goto(config.avigilon_url, timeout=10000)

            # Check if we're on the login page or have access
            # This is a heuristic - adjust based on actual Avigilon behavior
            current_url = page.url
            title = page.title()

            page.close()

            # If we're redirected to login page, session is invalid
            if "login" in current_url.lower() or "signin" in current_url.lower():
                return False

            # If page loaded successfully with expected content, session is valid
            return True

        except Exception as e:
            print(f"Error checking session validity: {e}")
            return False


def manual_authenticate():
    """
    Interactive authentication flow for initial setup.
    Opens a browser window for user to log in, then saves cookies.
    """
    print("Starting manual authentication...")
    print(f"You will need to log in to: {config.avigilon_url}")

    session_manager = SessionManager()

    with sync_playwright() as p:
        # Launch browser in headed mode (not headless) for manual login
        browser: Browser = p.chromium.launch(headless=False)
        context: BrowserContext = browser.new_context()

        # Navigate to Avigilon URL
        page = context.new_page()
        page.goto(config.avigilon_url)

        print("\n" + "=" * 60)
        print("Please log in to Avigilon in the browser window.")
        print("Once you're logged in and can see the door controls,")
        print("press ENTER in this terminal to save the session.")
        print("=" * 60 + "\n")

        input("Press ENTER when logged in...")

        # Verify we can see the door button before saving
        try:
            # Try to find the door button to confirm we're authenticated
            button = page.get_by_text(config.door_button_text, exact=False)
            if button.count() > 0:
                print(f"✓ Found '{config.door_button_text}' button")
            else:
                print(f"⚠ Warning: Could not find '{config.door_button_text}' button")
                response = input("Save session anyway? (y/n): ")
                if response.lower() != "y":
                    print("Authentication cancelled")
                    browser.close()
                    return False
        except Exception as e:
            print(f"⚠ Error verifying button: {e}")
            print("Saving session anyway...")

        # Save cookies
        session_manager.save_cookies(context)
        print("✓ Session saved successfully")

        browser.close()
        return True


if __name__ == "__main__":
    # Run manual authentication when script is executed directly
    success = manual_authenticate()
    exit(0 if success else 1)
