import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
TESLA_CLIENT_ID = os.getenv("TESLA_CLIENT_ID")
TESLA_CLIENT_SECRET = os.getenv("TESLA_CLIENT_SECRET")
TESLA_REDIRECT_URI = os.getenv("TESLA_REDIRECT_URI")
TESLA_AUTH_URL = os.getenv("TESLA_AUTH_URL")
TESLA_TOKEN_URL = os.getenv("TESLA_TOKEN_URL")
TESLA_AUDIENCE = os.getenv("TESLA_AUDIENCE")
TESLA_SCOPES = os.getenv("TESLA_SCOPES")