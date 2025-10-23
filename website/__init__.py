import urllib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    # ĐÃ SỬA: Thêm 'r' vào trước chuỗi để xử lý các ký tự gạch chéo ngược (\) trong tên server MSSQL
    # Điều này ngăn Python hiểu nhầm '\C' và '\S' là các ký tự thoát.
    # app.config['SQLALCHEMY_DATABASE_URI'] = r'mssql+pyodbc://NHATTRAN\CLCCSDLPTNHOM11/Qlsv?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "quanlysinhvien2025" 
    
    db.init_app(app)
    login_manager.init_app(app)

    # Import và đăng ký blueprint
    from . import models
    from .api.index import auth_bp
    from .api.student import student_bp
    from .api.lecturer import lecturer_bp
    from .api.admin import admin_bp

    with app.app_context():
        db.create_all()
        print('Database Created')

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(lecturer_bp, url_prefix="/api/lecturer")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    return app