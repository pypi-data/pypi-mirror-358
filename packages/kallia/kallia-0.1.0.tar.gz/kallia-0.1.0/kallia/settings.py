import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY", "ollama")
BASE_URL = os.getenv("BASE_URL", "http://localhost:11434/v1")
MODEL = os.getenv("MODEL", "qwen2.5vl:32b")
