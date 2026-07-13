from dotenv import load_dotenv
load_dotenv()

import os

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER")
EMERGENCY_CONTACT = os.environ.get("EMERGENCY_CONTACT")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_GEOCODING_API_KEY = os.environ.get("GOOGLE_GEOCODING_API_KEY")
GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")