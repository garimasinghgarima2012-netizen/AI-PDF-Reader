from dotenv import load_dotenv
import os

load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")