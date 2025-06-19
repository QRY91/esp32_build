"""
Secrets Configuration Template for Uroboro Stats Meter
====================================================

Copy this file to secrets.py and fill in your actual values.
DO NOT commit secrets.py to version control!
Add secrets.py to your .gitignore file.

Author: QRY
Date: June 19, 2025
"""

# WiFi Configuration
WIFI_SSID = "your_wifi_network_name"
WIFI_PASSWORD = "your_wifi_password"

# PostHog Configuration
POSTHOG_HOST = "https://eu.posthog.com"  # or your PostHog instance URL
POSTHOG_PROJECT_ID = "your_project_id"
POSTHOG_PERSONAL_API_KEY = "your_personal_api_key_here"
POSTHOG_API_KEY = "your_project_api_key_here"  # Project API key (phc_*)
