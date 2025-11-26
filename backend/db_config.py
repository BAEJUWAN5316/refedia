import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./refedia.db")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7일 (7 * 24 * 60)

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", None)

# Frame Cache Configuration
FRAME_CACHE_EXPIRE_SECONDS = int(os.getenv("FRAME_CACHE_EXPIRE_SECONDS", "300"))
