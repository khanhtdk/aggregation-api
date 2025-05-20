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

# Default settings for Flask-Caching
CACHE_TYPE = 'SimpleCache'  # uses python dict
CACHE_DEFAULT_TIMEOUT = 60  # seconds

# Set a secret key for accessing to self API. This value should be replaced when
# being used in production.
API_SECRET_KEY = os.getenv('API_SECRET_KEY', default='0123456789abcdefghijklmnopqrstuvwxyz')
