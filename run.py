from app import create_app
from app.models import db, User

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Seed default admin if not present (tables must exist in MySQL)
        try:
            if not User.query.filter_by(role='admin').first():
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
                print("Default admin created: admin@dermiq.com / admin123")
        except Exception as e:
            print("\n" + "="*80)
            print(f"Seeding warning/error: {e}")
            print("The default admin user could not be seeded. This is normal if tables do not exist yet.")
            print("Please run 'python init_mysql.py' to initialize the database and tables.")
            print("="*80 + "\n")
            
    app.run(debug=True, use_reloader=False)
