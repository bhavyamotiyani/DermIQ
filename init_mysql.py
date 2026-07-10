import os
import pymysql
from dotenv import load_dotenv

# Explicitly load .env from current directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_NAME = os.getenv('DB_NAME', 'skincare_db')

def initialize_database():
    print("--- Database Initialization ---")
    print(f"Connecting to MySQL Server at {DB_HOST}:{DB_PORT} as '{DB_USER}'...")
    
    try:
        ssl_args = None
        if DB_HOST not in ('localhost', '127.0.0.1'):
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ssl_args = ctx

        # Step 1: Connect to MySQL server and ensure database exists
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            ssl=ssl_args
        )
        cursor = conn.cursor()
        
        print(f"Checking if database '{DB_NAME}' exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Database '{DB_NAME}' verified/created successfully.")
        
    except Exception as e:
        print("\n" + "="*80)
        print("ERROR: Failed to connect to MySQL Server to verify/create database.")
        print(f"Connection details: Host={DB_HOST}, Port={DB_PORT}, User={DB_USER}")
        print("Error details:", e)
        print("="*80 + "\n")
        return False

    try:
        # Step 2: Initialize Flask application context and run db.create_all()
        print("Initializing Flask App context...")
        from app import create_app
        from app.models import db, User
        
        app = create_app()
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("Tables created/verified successfully.")
            
            # Step 3: Seed default admin account
            print("Checking default admin account...")
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                admin = User(
                    email='admin@dermiq.com',
                    name='Admin User',
                    skin_type='normal',
                    role='admin',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Seeded default admin successfully: admin@dermiq.com / admin123")
            else:
                print("Default admin account already exists.")
                
            print("\nDatabase initialization completed successfully!")
            return True
            
    except Exception as e:
        print("\n" + "="*80)
        print("ERROR: Failed to create tables or seed admin account.")
        print("Error details:", e)
        print("="*80 + "\n")
        return False

if __name__ == '__main__':
    initialize_database()
