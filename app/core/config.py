import os

class Settings:
    PROJECT_NAME: str = "LPG Supply Chain System"
    PROJECT_VERSION: str = "1.0.0"
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "noobu")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "yDhiczH4-4EZAsydz_Wbxg")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "fake-ayeaye-20209.j77.aws-ap-south-1.cockroachlabs.cloud")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "26257")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "defaultdb")
    
    # In a real app, use a strong secret key from env
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey12345") 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
