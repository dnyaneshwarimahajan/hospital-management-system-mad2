from datetime import date
from flask_security import current_user
from flask_restful import Resource
from flask import request
from flask_security import auth_required, roles_required
from flask_security import auth_required, roles_accepted, current_user
from flask_security import hash_password
from user_data import user_database

from model import db, User, Role, Dept, Appointments, DoctorAvailability, Treatments


class CreateDoctor(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self):
        depts = Dept.query.all()
        return { "departments": [{"id": d.id, "dept_name": d.dept_name} for d in depts]}, 200


    @auth_required('token')
    @roles_required('admin')
    def post(self):

        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        contact = data.get("contact_no")
        department_id = data.get("department_id")
        new_department_name = data.get("new_department_name")

        if not username or not email or not password:
            return {"message": "Username, Email and Password required"}, 400

   
        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists"}, 400

        if User.query.filter_by(username=username).first():
            return {"message": "Username already exists"}, 400


        department = None

        if department_id:
            department = Dept.query.get(department_id)
            if not department:
                return {"message": "Department not found"}, 404

        elif new_department_name:
            department = Dept(
                dept_name=new_department_name
            )
            db.session.add(department)
            db.session.commit()

        else:
            return {"message": "Department required"}, 400
        
        new_user = user_database.create_user(
            username=username,
            email=email,
            password=hash_password(password),
            contact_no=contact,
            department_id=department.id,
            blacklist=False
        )

        doctor_role = Role.query.filter_by(name="doctor").first()
        new_user.roles.append(doctor_role)
        db.session.commit()

        return {
            "message": "Doctor created successfully",
            "doctor_id": new_user.id
        }, 201


class AdminDashboard(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self):

        total_doctors = User.query.join(User.roles).filter(Role.name == "doctor").count()
        total_patients = User.query.join(User.roles).filter(Role.name == "patient").count()
        total_departments = Dept.query.count()

        today = date.today().strftime("%Y-%m-%d")

        active_appointments = Appointments.query.filter(
            Appointments.date == today,
            Appointments.status == "booked"
        ).count()

        doctors = User.query.join(User.roles).filter(Role.name == "doctor").all()

        doctor_list = [{
            "id": d.id,
            "name": d.username,
            "email": d.email,
            "contact_no": d.contact_no,
            "department": d.department.dept_name if d.department else None,
            "blacklisted": d.blacklist
        } for d in doctors]

        patients = User.query.join(User.roles).filter(Role.name == "patient").all()

        patient_list = [{
            "id": p.id,
            "email": p.email,
            "contact_no": p.contact_no,
            "name": p.username,
            "blacklisted": p.blacklist
        } for p in patients]


        today_appointments = Appointments.query.filter(
            Appointments.date == today
        ).all()

        appointment_list = []

        for appt in today_appointments:

            doctor = User.query.get(appt.doctor_id)
            patient = User.query.get(appt.user_id)

            appointment_list.append({
                "id": appt.id,
                "doctor": doctor.username if doctor else None,
                "patient": patient.username if patient else None,
                "patient_id": appt.user_id,
                "status": appt.status,
                "date": appt.date,
                "time": appt.time
            })

        return {
            "summary": {
                "totalDoctors": total_doctors,
                "totalPatients": total_patients,
                "totalDepartments": total_departments,
                "activeAppointments": active_appointments
            },
            "doctors": doctor_list,
            "patients": patient_list,
            "appointments": appointment_list
        }, 200

class BlacklistUser(Resource):

    @auth_required('token')
    @roles_required('admin')
    def put(self, user_id):

        user = User.query.get(user_id)

        if not user:
            return {"message": "User not found"}, 404

        user.blacklist = True
        db.session.commit()

        return {"message": "User blacklisted"}, 200

class UnblacklistUser(Resource):

    @auth_required('token')
    @roles_required('admin')
    def put(self, user_id):

        user = User.query.get(user_id)

        if not user:
            return {"message": "User not found"}, 404

        user.blacklist = False
        db.session.commit()

        return {"message": "User unblacklisted"}, 200

class EditDoctor(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self, user_id):          
        user = User.query.get(user_id)

        if not user:
            return {"message": "Doctor not found"}, 404

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "contact_no": user.contact_no,
            "qualifications": user.qualifications,
            # "specialty": user.specialty,
            "years_experience": user.years_experience,
            # "years_specialist": user.years_specialist,
            # "bio": user.bio,
            # "photo_url": user.photo_url,
            # "department_id": user.department_id,
            "department": user.department.dept_name if user.department else None
        }, 200

    @auth_required('token')
    @roles_required('admin')
    def put(self, user_id):

        user = User.query.get(user_id)

        if not user:
            return {"message": "Doctor not found"}, 404

        if not any(role.name == "doctor" for role in user.roles):
            return {"message": "User is not a doctor"}, 400

        data = request.get_json()

        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.contact_no = data.get("contact_no", user.contact_no)
        user.qualifications = data.get("qualifications", user.qualifications)
        # user.specialty = data.get("specialty", user.specialty)
        user.years_experience = data.get("years_experience", user.years_experience)
        # user.years_specialist = data.get("years_specialist", user.years_specialist)
        # user.bio = data.get("bio", user.bio)
        # user.photo_url = data.get("photo_url", user.photo_url)

        # Update department
        department_id = data.get("department_id")
        if department_id:
            dept = Dept.query.get(department_id)
            if not dept:
                return {"message": "Department not found"}, 404
            user.department_id = dept.id

        user.password = hash_password(data.get("password"))

        db.session.commit()

        return {"message": "Doctor updated successfully"}, 200
    


class EditPatient(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'patient')
    def get(self, user_id):
        # Patient can only view their own profile
        if 'patient' in [r.name for r in current_user.roles]:
            if current_user.id != user_id:
                return {"message": "Unauthorized"}, 403

        user = User.query.get(user_id)

        if not user:
            return {"message": "Patient not found"}, 404

        if not any(role.name == "patient" for role in user.roles):
            return {"message": "User is not a patient"}, 400

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "contact_no": user.contact_no,
        }, 200

    @auth_required('token')
    @roles_accepted('admin', 'patient')
    def put(self, user_id):
        if 'patient' in [r.name for r in current_user.roles]:
            if current_user.id != user_id:
                return {"message": "Unauthorized"}, 403

        user = User.query.get(user_id)

        if not user:
            return {"message": "Patient not found"}, 404

        if not any(role.name == "patient" for role in user.roles):
            return {"message": "User is not a patient"}, 400

        data = request.get_json()

        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.contact_no = data.get("contact_no", user.contact_no)

        if data.get("password"):
          
            user.password = hash_password(data.get("password"))

        db.session.commit()

        return {"message": "Patient updated successfully"}, 200

class DeleteDoctor(Resource):

    @auth_required('token')
    @roles_required('admin')
    def delete(self, user_id):

        user = User.query.get(user_id)

        if not user:
            return {"message": "Doctor not found"}, 404

        if not any(role.name == "doctor" for role in user.roles):
            return {"message": "User is not a doctor"}, 400

        Appointments.query.filter_by(doctor_id=user.id).delete()

        DoctorAvailability.query.filter_by(doctor_id=user.id).delete()

        db.session.delete(user)
        db.session.commit()

        return {"message": "Doctor deleted successfully"}, 200
    

class DeletePatient(Resource):

    @auth_required('token')
    @roles_required('admin')
    def delete(self, user_id):

        user = User.query.get(user_id)

        if not user:
            return {"message": "Patient not found"}, 404

        if not any(role.name == "patient" for role in user.roles):
            return {"message": "User is not a patient"}, 400

        Appointments.query.filter_by(user_id=user.id).delete()

        db.session.delete(user)
        db.session.commit()

        return {"message": "Patient deleted successfully"}, 200
    
class AdminPatientHistory(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self, patient_id):
        patient = db.session.get(User, patient_id)
        if not patient:
            return {"message": "Patient not found"}, 404

        appointments = Appointments.query.filter_by(user_id=patient_id).all()

        history = []
        for appt in appointments:
            doctor    = db.session.get(User, appt.doctor_id)
            treatment = db.session.get(Treatments, appt.treatment_id) if appt.treatment_id else None
            history.append({
                "appointment_id": appt.id,
                "doctor_name":    doctor.username if doctor else "-",
                "department":     doctor.department.dept_name if doctor and doctor.department else "-",
                "date":           appt.date,
                "time":           appt.time,
                "status":         appt.status,
                "treatment": {
                    "diagnosis":    treatment.diagnosis,
                    "treatment":    treatment.treatment,
                    "prescription": treatment.prescription
                } if treatment else None
            })

        return {
            "patient": {
                "id":         patient.id,
                "name":       patient.username,
                "email":      patient.email,
                "contact_no": patient.contact_no
            },
            "history": history
        }, 200

class AllAppointments(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self):
        appointments = Appointments.query.order_by(
            Appointments.date.desc()
        ).all()

        result = []
        for appt in appointments:
            doctor    = db.session.get(User, appt.doctor_id)
            patient   = db.session.get(User, appt.user_id)
            treatment = db.session.get(Treatments, appt.treatment_id) if appt.treatment_id else None
            result.append({
                "id":         appt.id,
                "doctor":     doctor.username if doctor else "-",
                "patient":    patient.username if patient else "-",
                "patient_id": appt.user_id,
                "date":       appt.date,
                "time":       "8:00 AM - 12:00 PM" if appt.time == "slot1" else "4:00 PM - 9:00 PM",
                "status":     appt.status,
                "diagnosis":  treatment.diagnosis if treatment else "-",
                "treatment":  treatment.treatment if treatment else "-",
            })

        return {"appointments": result}, 200
    

