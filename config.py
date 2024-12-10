# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'mysql+pymysql://root:Morenoram12@localhost/gestion_estudiantes'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
