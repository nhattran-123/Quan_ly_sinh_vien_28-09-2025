import urllib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
from flask_cors import CORS # <<< THÊM DÒNG NÀY

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # <<< THÊM CẤU HÌNH CORS NGAY SAU KHI TẠO APP >>>
    # Cho phép origin cụ thể (frontend 5500) truy cập API và hỗ trợ credentials (cookies)
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})

    app.config['SQLALCHEMY_DATABASE_URI'] = r'mssql+pyodbc://NHATTRAN\CLCCSDLPTNHOM11/Qlsv?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "quanlysinhvien2025"

    db.init_app(app)
    login_manager.init_app(app)

    # Import và đăng ký blueprint (giữ nguyên)
    from . import models
    from .api.index import auth_bp
    from .api.student import student_bp
    from .api.lecturer import lecturer_bp
    from .api.admin import admin_bp

    with app.app_context():
        # db.create_all() # Có thể comment dòng này đi sau lần chạy đầu tiên
        print('Database Checked/Created')

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(lecturer_bp, url_prefix="/api/lecturer")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    return app