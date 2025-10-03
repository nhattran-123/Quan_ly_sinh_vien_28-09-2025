from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
login_manager = LoginManager()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Qlsv.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['SECRET_KEY'] = "quanlysinhvien2025"  # ← Thêm dòng này
    
    db.init_app(app)
    login_manager.init_app(app)

    # Import và đăng ký blueprint
    from . import models
    from .api.index import auth_bp
    # from .api.student import student_bp
    # from .api.lecturer import lecturer_bp
    # from .api.admin import admin_bp

    with app.app_context():
        if not path.exists(path.join(app.root_path, 'Qlsv.db')):
            db.create_all()
            print('Database Created')

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    # app.register_blueprint(student_bp, url_prefix="/api/student")
    # app.register_blueprint(lecturer_bp, url_prefix="/api/lecturer")
    # app.register_blueprint(admin_bp, url_prefix="/api/admin")

    return app
