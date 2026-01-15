"""
Configuration management for Pi Home Server.
Loads and validates environment variables.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self):
        # Twilio configuration
        self.twilio_account_sid = self._get_required("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = self._get_required("TWILIO_AUTH_TOKEN")

        # Security - allowed phone numbers
        allowed_numbers_str = self._get_required("ALLOWED_PHONE_NUMBERS")
        self.allowed_phone_numbers = self._parse_phone_numbers(allowed_numbers_str)

        # Avigilon configuration
        self.avigilon_url = self._get_required("AVIGILON_URL")
        self.door_button_text = self._get_required("DOOR_BUTTON_TEXT")

        # Server configuration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))

        # Session storage
        self.cookies_file = "cookies.json"

        # Rate limiting
        self.rate_limit_max_requests = 10  # per hour
        self.rate_limit_window_seconds = 3600  # 1 hour

    @staticmethod
    def _get_required(key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

    @staticmethod
    def _parse_phone_numbers(numbers_str: str) -> List[str]:
        """Parse comma-separated phone numbers into list."""
        numbers = [num.strip() for num in numbers_str.split(",")]

        # Validate E.164 format (basic check)
        for num in numbers:
            if not num.startswith("+"):
                raise ValueError(f"Phone number {num} must be in E.164 format (+1234567890)")
            if not num[1:].isdigit():
                raise ValueError(f"Phone number {num} contains invalid characters")

        return numbers

    def is_phone_allowed(self, phone_number: str) -> bool:
        """Check if phone number is in allowlist."""
        return phone_number in self.allowed_phone_numbers


# Global config instance
config = Config()
