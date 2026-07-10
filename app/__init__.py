from flask import Flask
from config import Config
from .models import db, User

# Flask-Login replaced by custom session-based isolated authentication

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    @app.context_processor
    def inject_current_user():
        from app.auth import current_user
        return dict(current_user=current_user)

    with app.app_context():
        # Startup connection validation
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("MySQL connection verified successfully.")
        except Exception as e:
            print("\n" + "="*80)
            print("DATABASE CONNECTION ERROR:")
            print(f"Failed to connect to the MySQL database at {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            print("Error details:", e)
            print("Please make sure MySQL is running and credentials in .env are correct.")
            print("="*80 + "\n")
            # Do NOT raise or exit, allowing the application to start up and preventing crash

        # Import routes here to avoid circular imports
        from .routes.auth_routes import auth_bp
        from .routes.user_routes import user_bp
        from .routes.admin_routes import admin_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
