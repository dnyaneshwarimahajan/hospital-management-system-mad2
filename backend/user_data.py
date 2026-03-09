from flask_security import SQLAlchemyUserDatastore

from database import db
from model import User, Role

user_database = SQLAlchemyUserDatastore(db,User,Role)
