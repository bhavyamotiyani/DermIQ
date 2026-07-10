import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Explicitly load .env from current directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-dermiq')
    
    # Custom session options to prevent cookie collision on localhost:5000
    SESSION_COOKIE_NAME = 'dermiq_session'
    SESSION_REFRESH_EACH_REQUEST = True
    PERMANENT_SESSION_LIFETIME = 2592000  # 30 days in seconds
    
    # Razorpay Details
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
    
    # Startup Debug Logs
    print("--- ENV DEBUG ---")
    print(f"RAZORPAY_KEY_ID found: {bool(RAZORPAY_KEY_ID)}")
    if RAZORPAY_KEY_ID:
        print(f"RAZORPAY_KEY_ID: {RAZORPAY_KEY_ID[:10]}...")
    else:
        print("RAZORPAY_KEY_ID: MISSING")
    print(f"RAZORPAY_KEY_SECRET found: {bool(RAZORPAY_KEY_SECRET)}")
    print("------------------")

    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'skincare_db')
    
    # MySQL only — URL-encode password to handle special characters
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Enable connection pool pre-ping and recycling to prevent dropped connections
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280
    }

    # Enable SSL for remote cloud databases (like Aiven) to bypass certificate verification errors
    if DB_HOST not in ('localhost', '127.0.0.1'):
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {
            "ssl": {
                "ssl_verify_cert": False,
                "ssl_verify_identity": False
            }
        }

