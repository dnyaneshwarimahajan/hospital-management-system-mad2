from flask_security import UserMixin, RoleMixin
from datetime import datetime
from database import db

class UserRoles(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

class Role(db.Model, RoleMixin):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer,  primary_key=True)
    username = db.Column(db.String(100), nullable=False,  unique=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    active = db.Column(db.Boolean(), default=True)


    fs_token_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)

    contact_no = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    blacklist = db.Column(db.Boolean, default=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    qualifications = db.Column(db.String(200))
    # specialty = db.Column(db.String(100))
    years_experience = db.Column(db.Integer)
    # years_specialist    = db.Column(db.Integer)
    bio = db.Column(db.Text)
    photo_url = db.Column(db.String(200))

    roles = db.relationship("Role", secondary="user_roles", backref='bearer')
    department = db.relationship("Dept", back_populates="doctors")

    def __repr__(self):
        return f"<User {self.username}>"

class Dept(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(100))

    doctors = db.relationship("User", back_populates="department")

class Appointments(db.Model):
    __tablename__ = "appointment"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='booked')
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.String(20))
    time  = db.Column(db.String(20))
    treatment_id = db.Column(db.Integer, db.ForeignKey("treatment.id"), unique=True)

class Treatments(db.Model):
    __tablename__ = "treatment"
    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.String(50), nullable=False)
    treatment = db.Column(db.String(100), nullable=False)
    prescription = db.Column(db.String(200))

class DoctorAvailability(db.Model):
    __tablename__ = "doctor_availability"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    slot_1 = db.Column(db.Boolean)
    slot_2 = db.Column(db.Boolean)
    doctor = db.relationship("User", backref="availability")