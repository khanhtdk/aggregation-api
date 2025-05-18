import os

# Project path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Absolute path to database file
DATABASE_FILE = os.path.join(BASE_DIR, 'db.sqlite')

# Database settings for SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Which year in the ingested dataset is treated as current year? If not
# specifying, it is calculated using current time.
CURRENT_YEAR_CONTEXT = 2025
