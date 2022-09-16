from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}

    with app.app_context():
        db.init_app(app)
        from . import routes
        db.create_all()

    return app
