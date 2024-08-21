import os
from dotenv import load_dotenv

load_dotenv()
print(f"Config file location: {os.path.abspath(__file__)}")

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    # Other configuration variables...

print(f"Loaded DATABASE_URL: {Config.SQLALCHEMY_DATABASE_URI}")