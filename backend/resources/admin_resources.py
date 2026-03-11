from datetime import date, timedelta

from flask import request
from flask_restful import Resource
from flask_security import auth_required, roles_accepted, roles_required, current_user, hash_password

from models.model import db, User, Role, Dept, Appointments, DoctorAvailability, Treatments
from user_data import user_database

def get(user_id, role=None):
    user = db.session.get(User, user_id)
    if not user:
        return None, ({"message": "User not found"}, 404)
    return user, None


def doctor(d):
    return {"id": d.id,"name": d.username,"email": d.email,"contact_no": d.contact_no,"department": d.department.dept_name if d.department else None,"blacklisted": d.blacklist}


def patient(p):
    return {"id": p.id,"name": p.username,"email": p.email,"contact_no": p.contact_no, "blacklisted": p.blacklist}


def appointment(appt):
    doctor = db.session.get(User, appt.doctor_id)
    patient = db.session.get(User, appt.user_id)
    treatment = db.session.get(Treatments, appt.treatment_id) if appt.treatment_id else None
    return {
        "id": appt.id,"doctor": doctor.username ,"patient": patient.username ,
        "patient_id": appt.user_id,"date": appt.date,"time": appt.time,"status": appt.status,
        "department": doctor.department.dept_name if doctor and doctor.department else "-",
        "treatment": {
            "diagnosis": treatment.diagnosis,
            "treatment": treatment.treatment,
            "prescription": treatment.prescription,
        } if treatment else None,
    }


def resolve_or_create_department(department_id, new_department_name):
    if new_department_name:
        dept = Dept(dept_name=new_department_name)
        db.session.add(dept)
        db.session.flush()
        return dept, None
    if department_id:
        dept = db.session.get(Dept, department_id)
        if not dept:
            return None, ({"message": "Department not found"}, 404)
        return dept, None
    return None, ({"message": "Department required"}, 400)

class CreateDoctor(Resource):

    @auth_required("token")
    @roles_required("admin")
    def get(self):
        depts = Dept.query.all()
        return {"departments": [{"id": d.id, "dept_name": d.dept_name} for d in depts]}, 200

    @auth_required("token")
    @roles_required("admin")
    def post(self):
        data     = request.get_json()
        username = data.get("username")
        email    = data.get("email")
        password = data.get("password")

        if not all([username, email, password]):
            return {"message": "Username, email and password are required"}, 400
        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists"}, 400
        if User.query.filter_by(username=username).first():
            return {"message": "Username already exists"}, 400

        dept_id = data.get("department_id")
        if dept_id:
            dept = db.session.get(Dept, dept_id)
            if not dept:
                return {"message": "Department not found"}, 404
        elif data.get("new_department_name"):
            dept = Dept(dept_name=data["new_department_name"])
            db.session.add(dept)
            db.session.flush()
        else:
            return {"message": "Department is required"}, 400

        doctor_role = Role.query.filter_by(name="doctor").first()
        new_user = user_database.create_user(
            username=username,
            email=email,
            password=hash_password(password),
            contact_no=data.get("contact_no"),
            department_id=dept.id,
            roles=[doctor_role],
        )
        db.session.commit()
        return {"message": "Doctor created successfully"}, 201


class EditDoctor(Resource):

    @auth_required("token")
    @roles_required("admin")
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"message": "doctor not found"}, 404
        return {
            "id": user.id,"username": user.username,"email": user.email,"contact_no": user.contact_no,"qualifications": user.qualifications,"years_experience": user.years_experience,
            "department": user.department.dept_name if user.department else None,
            "department_id": user.department_id,
        }, 200
    @auth_required("token")
    @roles_required("admin")
    def put(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"message": "doctor not found"}, 404

        data = request.get_json()
        user.username = data.get("username", user.username)
        user.email = data.get("email",  user.email)
        user.contact_no = data.get("contact_no", user.contact_no)
        user.qualifications = data.get("qualifications", user.qualifications)
        user.years_experience = data.get("years_experience", user.years_experience)

        if data.get("password"):
            user.password = hash_password(data["password"])

        if data.get("department_id"):
            dept = db.session.get(Dept, data["department_id"])
            if not dept:
                return {"message": "Department not found"}, 404
            user.department_id = dept.id

        elif data.get("new_department_name"): 
            dept = Dept(dept_name=data["new_department_name"])
            db.session.add(dept)
            db.session.flush()
            user.department_id = dept.id

        db.session.commit()
        return {"message": "Doctor updated successfully"}, 200

class DeleteDoctor(Resource):

    @auth_required("token")
    @roles_required("admin")
    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"message": "doctor not found"}, 404


        Appointments.query.filter_by(doctor_id=user.id).delete()
        DoctorAvailability.query.filter_by(doctor_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        return {"message": "Doctor deleted successfully"}, 200
    

class EditPatient(Resource):
    @auth_required("token")
    @roles_accepted("admin", "patient")
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"message": "Patient not found"}, 404

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "contact_no": user.contact_no,
        }, 200

    @auth_required("token")
    @roles_accepted("admin", "patient")
    def put(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"message": "Patient not found"}, 404

        data = request.get_json()
        user.username = data.get("username",user.username)
        user.email = data.get("email", user.email)
        user.contact_no = data.get("contact_no", user.contact_no)

        if data.get("password"):
            user.password = hash_password(data["password"])

        db.session.commit()
        return {"message": "Patient updated successfully"}, 200

class DeletePatient(Resource):

    @auth_required("token")
    @roles_required("admin")
    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"message": "Patient not found"}, 404

        Appointments.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        return {"message": "Patient deleted successfully"}, 200

class BlacklistUser(Resource):

    @auth_required("token")
    @roles_required("admin")
    def put(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"message": "User not found"}, 404
        user.blacklist = True
        db.session.commit()
        return {"message": "User blacklisted"}, 200


class UnblacklistUser(Resource):

    @auth_required("token")
    @roles_required("admin")
    def put(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"message": "User not found"}, 404
        user.blacklist = False
        db.session.commit()
        return {"message": "User unblacklisted"}, 200
    
class AdminDashboard(Resource):

    @auth_required("token")
    @roles_required("admin")
    def get(self):
        today = date.today().strftime("%Y-%m-%d")
        week_end = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

        all_doctors  = User.query.filter(User.roles.any(name="doctor")).all()
        all_patients = User.query.filter(User.roles.any(name="patient")).all()

        upcoming = Appointments.query.filter(
            Appointments.date >= today,
            Appointments.date <= week_end,
            Appointments.status == "booked",
        ).all()

        return {
            "summary": {
                "totalDoctors": len(all_doctors),
                "totalPatients": len(all_patients),
                "totalDepartments": Dept.query.count(),
                "activeAppointments": Appointments.query.filter_by(date=today, status="booked").count(),
            },
            "doctors":      [doctor(d) for d in all_doctors],
            "patients":     [patient(p) for p in all_patients],
            "appointments": [appointment(a) for a in upcoming],
        }, 200

class AdminPatientHistory(Resource):

    @auth_required("token")
    @roles_required("admin")
    def get(self, patient_id):
        patient = db.session.get(User, patient_id)
        if not patient:
            return {"message": "Patient not found"}, 404

        history = [appointment(a) for a in Appointments.query.filter_by(user_id=patient_id).all()]

        return {
            "patient": {
                "id": patient.id,
                "name": patient.username,
                "email": patient.email,
                "contact_no": patient.contact_no,
            },
            "history": history,
        }, 200


class AllAppointments(Resource):

    @auth_required("token")
    @roles_required("admin")
    def get(self):
        appointments = Appointments.query.order_by(Appointments.date.desc()).all()
        return {"appointments": [appointment(a) for a in appointments]}, 200