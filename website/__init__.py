from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = 'Qlsv.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'quanlysinhvien2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # 🔑 Import models trước khi tạo DB
    from . import models  

    with app.app_context():
        if not path.exists(path.join(app.root_path, DB_NAME)):
            db.create_all()
            print('Database Created!')

    # route test
    @app.route('/')
    def home():
        return "Flask đã chạy thành công"

    return app
