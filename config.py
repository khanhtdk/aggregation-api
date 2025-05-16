import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, 'db.sqlite')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_TRACK_MODIFICATIONS = False
