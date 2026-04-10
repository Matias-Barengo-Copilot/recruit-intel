import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    TAVILY_API_KEY: str = os.environ.get("TAVILY_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o-mini"
    ASSUMED_INCOME: float = 250_000.0
    DEFAULT_MAX_DISTANCE: float = 300.0
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")

    DEFAULT_WEIGHTS = {
        "proximity": 25,
        "alumni": 20,
        "family": 20,
        "tax": 15,
        "geographic_ties": 10,
        "career_stage": 10,
    }
