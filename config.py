import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'a_secure_random_secret_key'
    # 연결하고자하는 DB의 File 위치
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'UserAnswer.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
