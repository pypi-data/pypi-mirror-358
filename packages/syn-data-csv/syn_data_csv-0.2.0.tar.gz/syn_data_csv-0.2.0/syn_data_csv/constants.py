import os
from dotenv import load_dotenv


load_dotenv() 

GROQ_API_KEY = os.getenv("GROQ_API")
HF_API_KEY = os.getenv("HF_API")

DEFAULTS = {
    "groq": {
        "api_key": GROQ_API_KEY,
        "model": "llama3-70b-8192"
    },
    "huggingface": {
        "api_key": HF_API_KEY,
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1"
    }
}

SUPPORTED_PROVIDERS = ["groq", "huggingface"]

MAX_BATCH_SIZE = 100
MAX_DEFAULT_ROWS = 100