import os

class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopementConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///hospital_data.db"
    DEBUG = True
    SECRET_KEY = "this-is-secretkey"
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = "this-is-a-password-salt"
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://")
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-key")
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", "fallback-salt")
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_TOKEN = "Authentication-Token"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    WTF_CSRF_CHECK_DEFAULT = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "None"
    REMEMBER_COOKIE_SAMESITE = "None"
    DEBUG = False
