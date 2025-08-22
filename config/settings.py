"""
settings.py
Configuration settings for API keys, credentials, and constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CREDENTIALS_JSON_PATH = os.getenv("GOOGLE_CREDENTIALS_JSON_PATH")
GEMENI_API_KEY = os.getenv("GEMENI_API_KEY")

# Add other constants as needed
