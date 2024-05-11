import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Base configuration."""

    # Ensure the SECRET_KEY is set in the environment, otherwise raise an exception.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if SECRET_KEY is None:
        raise ValueError("No SECRET_KEY set for Flask application")

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries to the console (helpful for development)

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite database for tests

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
