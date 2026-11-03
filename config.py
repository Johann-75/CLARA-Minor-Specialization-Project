import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
# Default: duckdb:///clara.db (local development)
DATABASE_URL = os.getenv("DATABASE_URL", "duckdb:///clara.db")

# Google Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Data generator settings
SYNTHETIC_INSTANCE_COUNT = int(os.getenv("SYNTHETIC_INSTANCE_COUNT", "300"))
SYNTHETIC_DAYS_OF_METRICS = int(os.getenv("SYNTHETIC_DAYS_OF_METRICS", "90"))
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

# Recommendation and Model Settings
RECOMMENDATION_THRESHOLD = float(os.getenv("RECOMMENDATION_THRESHOLD", "50.0"))
TOP_N_RECOMMENDATIONS = int(os.getenv("TOP_N_RECOMMENDATIONS", "10"))
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")

