class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopementConfig(Config):

    SQLALCHEMY_DATABASE_URI = "sqlite:///hospital_data.db"
    DEBUG = True
    SECRET_KEY = "this-is-secretkey"
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = "this-is-a-password-salt"
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_TOKEN = "Authentication-Token"
