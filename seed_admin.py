from website import create_app, db
from website.models import User, Admin

app = create_app()

with app.app_context():
    if not User.query.filter_by(role="admin").first():
        admin_user = User(
            id="admin01",
            email="admin@example.com",
            role="admin",
            full_name="System Administrator"
        )
        admin_user.set_password("Admin123")
        db.session.add(admin_user)
        db.session.flush()  # Lấy admin_user.id

        db.session.add(Admin(user_id=admin_user.id))
        db.session.commit()
        print("Admin account created.")
    else:
        print("Admin account already exists.")