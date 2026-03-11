from flask_security import SQLAlchemyUserDatastore

from database import db
from models.model import User, Role

user_database = SQLAlchemyUserDatastore(db, User, Role)
