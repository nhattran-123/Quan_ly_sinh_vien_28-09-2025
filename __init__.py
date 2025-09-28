from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = 'database.sqlite3'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'cai nay de gi cung duoc'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    with app.app_context():
        if not path.exists(path.join(app.root_path, DB_NAME)):
            db.create_all()
            print('Database Created')

    return app