import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
    # Better error handling for missing credentials
    if not DB_USERNAME or not DB_PASSWORD:
        raise ValueError("DB_USERNAME and DB_PASSWORD environment variables are required")
    
    MONGO_URI = f'mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@securityfunded.v19tawj.mongodb.net/'
    DB_NAME = 'security_funded'
    COLLECTION_NAME = 'SecurityFunded'
    
    # Flask Configuration
    FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "8000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # Streamlit Configuration
    STREAMLIT_HOST = os.getenv("STREAMLIT_HOST", "127.0.0.1")
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # API Configuration - Fixed for Docker and local environments
    API_BASE_URL = os.getenv("API_BASE_URL")
    if not API_BASE_URL:
        # Default based on environment
        if os.getenv("DOCKER_ENV", "false").lower() == "true":
            API_BASE_URL = "http://security-funded-app:8000"
        else:
            API_BASE_URL = f"http://{FLASK_HOST}:{FLASK_PORT}"
    
    # Scraping Configuration
    SCRAPE_URL = "https://www.returnonsecurity.com/posts"
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    
    # Pagination
    DEFAULT_PAGE_SIZE = 12
    MAX_PAGE_SIZE = 100
    
    # Scheduler
    SCHEDULER_INTERVAL_HOURS = 4