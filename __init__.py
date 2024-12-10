from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Carga la configuración desde config.py

    db.init_app(app)

    with app.app_context():
        db.create_all()  # Crea las tablas si no existen

    return app
