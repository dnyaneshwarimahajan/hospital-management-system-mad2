from datetime import date
from flask_restful import Resource
from flask import request
from flask_security import auth_required, roles_required, current_user
from extensions import cache 

from model import db, User, Role, Dept, Appointments, Treatments, DoctorAvailability


class PatientDashboard(Resource):

    @auth_required('token')
    @roles_required('patient')

    def get(self):

        today = date.today().strftime("%Y-%m-%d")

        upcoming = Appointments.query.filter_by(user_id=current_user.id).filter(
            Appointments.date >= today,
            Appointments.status == "booked"
        ).all()

        upcoming_list = []
        for appt in upcoming:
            doctor = User.query.get(appt.doctor_id)
            upcoming_list.append({
                "id": appt.id,
                "doctor_id": appt.doctor_id,
                "doctor": doctor.username if doctor else None,
                "department": doctor.department.dept_name if doctor and doctor.department else None,
                "date": appt.date,
                "time": appt.time,
                "status": appt.status
            })

        past = Appointments.query.filter_by(
            user_id=current_user.id
        ).filter(
            Appointments.date < today
        ).all()

        past_list = []
        for appt in past:
            doctor = User.query.get(appt.doctor_id)
            treatment = Treatments.query.get(appt.treatment_id) if appt.treatment_id else None
            past_list.append({
                "id": appt.id,
                "doctor": doctor.username if doctor else None,
                "department": doctor.department.dept_name if doctor and doctor.department else None,
                "date": appt.date,
                "time": appt.time,
                "status": appt.status,
                "treatment": {
                    "diagnosis": treatment.diagnosis,
                    "treatment": treatment.treatment,
                    "prescription": treatment.prescription
                } if treatment else None
            })

        return {
            "patient": {
                "id": current_user.id,
                "name": current_user.username,
                "email": current_user.email,
                "contact_no": current_user.contact_no
            },
            "upcoming_appointments": upcoming_list,
            "past_appointments": past_list
        }, 200


class PatientDepartments(Resource):

    @auth_required('token')
    @roles_required('patient')
    def get(self):
        depts = Dept.query.all()
        result = {
            "departments": [
                {"id": d.id, 
                "dept_name": d.dept_name, 
                "description": d.description
                }
                for d in depts
            ]
        }
        return result, 200

# class PatientDepartments(Resource):

#     @auth_required('token')
#     @roles_required('patient')
#     def get(self):
#         cache_key = "departments:all"

#         cached = cache.get(cache_key)
#         if cached:
#             print("[CACHE HIT] departments:all")
#             return cached, 200

#         print("[CACHE MISS] departments:all")
#         depts = Dept.query.all()
#         result = {
#             "departments": [
#                 {"id": d.id, "dept_name": d.dept_name, "description": d.description}
#                 for d in depts
#             ]
#         }

#         cache.set(cache_key, result, timeout=3600)
#         return result, 200


# class DepartmentDetail(Resource):

#     @auth_required('token')
#     @roles_required('patient')
#     def get(self, dept_id):
#         cache_key = f"department:{dept_id}"

#         cached = cache.get(cache_key)
#         if cached:
#             print(f"[CACHE HIT] department:{dept_id}")
#             return cached, 200

#         print(f"[CACHE MISS] department:{dept_id}")
#         dept = Dept.query.get(dept_id)
#         if not dept:
#             return {"message": "Department not found"}, 404

#         doctors = User.query.join(User.roles).filter(
#             Role.name == "doctor",
#             User.department_id == dept_id
#         ).all()

#         result = {
#             "department": {
#                 "id": dept.id,
#                 "dept_name": dept.dept_name,
#                 "description": dept.description
#             },
#             "doctors": [{
#                 "id": d.id,
#                 "name": d.username,
#                 "email": d.email,
#                 "contact_no": d.contact_no,
#                 "specialty": d.specialty,
#                 "blacklisted": d.blacklist
#             } for d in doctors]
#         }
#         cache.set(cache_key, result, timeout=600)
#         return result, 200
    
class DepartmentDetail(Resource):

    @auth_required('token')
    @roles_required('patient')
    def get(self, dept_id):
        dept = Dept.query.get(dept_id)
        if not dept:
            return {"message": "Department not found"}, 404

        doctors = User.query.join(User.roles).filter(
            Role.name == "doctor",
            User.department_id == dept_id
        ).all()

        return {
            "department": {
                "id": dept.id,
                "dept_name": dept.dept_name,
                "description": dept.description
            },
            "doctors": [{
                "id": d.id,
                "name": d.username,
                "email": d.email,
                "contact_no": d.contact_no,
                "specialty": d.specialty,
                "blacklisted": d.blacklist
            } for d in doctors]
        }, 200


# class SearchDoctors(Resource):

#     @auth_required('token')
#     @roles_required('patient')
#     def get(self):
#         query     = request.args.get("q", "").lower().strip()
#         cache_key = f"doctors:search:{query}"

#         cached = cache.get(cache_key)
#         if cached:
#             print(f"[CACHE HIT] doctors:search:{query}")
#             return cached, 200

#         print(f"[CACHE MISS] doctors:search:{query}")
#         doctors = User.query.join(User.roles).filter(Role.name == "doctor").all()

#         results = []
#         for d in doctors:
#             name_match = query in d.username.lower()
#             spec_match = query in (d.specialty or "").lower()
#             dept_match = query in (d.department.dept_name if d.department else "").lower()

#             if not query or name_match or spec_match or dept_match:
#                 results.append({
#                     "id": d.id,
#                     "name": d.username,
#                     "specialty": d.specialty,
#                     "department": d.department.dept_name if d.department else None,
#                     "qualifications": d.qualifications,
#                     "years_experience": d.years_experience,
#                     "photo_url": d.photo_url
#                 })

#         result = {"doctors": results}

#         cache.set(cache_key, result, timeout=120)
#         return result, 200


# class DoctorAvailabilityView(Resource):

#     @auth_required('token')
#     @roles_required('patient')
#     def get(self, doctor_id):
#         today     = date.today().strftime("%Y-%m-%d")
#         cache_key = f"availability:{doctor_id}:{today}"

#         cached = cache.get(cache_key)
#         if cached:
#             print(f"[CACHE HIT] availability:{doctor_id}:{today}")
#             return cached, 200

#         print(f"[CACHE MISS] availability:{doctor_id}:{today}")

#         availability = DoctorAvailability.query.filter_by(
#             doctor_id=doctor_id
#         ).filter(DoctorAvailability.date >= today).all()

#         slots = []
#         for a in availability:
#             if a.slot_1:
#                 slots.append({"date": a.date, "slot": "slot1", "label": "8:00 AM - 12:00 PM"})
#             if a.slot_2:
#                 slots.append({"date": a.date, "slot": "slot2", "label": "4:00 PM - 9:00 PM"})

#         booked = Appointments.query.filter_by(
#             doctor_id=doctor_id,
#             status="booked"
#         ).filter(Appointments.date >= today).all()

#         booked_slots = [{"date": b.date, "slot": b.time} for b in booked]

#         result = {
#             "available_slots": slots,
#             "booked_slots": booked_slots
#         }

#         cache.set(cache_key, result, timeout=180)
#         return result, 200

class SearchDoctors(Resource):

    @auth_required('token')
    @roles_required('patient')
    def get(self):
        query = request.args.get("q", "").lower().strip()

        doctors = User.query.join(User.roles).filter(Role.name == "doctor").all()

        results = []
        for d in doctors:
            name_match = query in d.username.lower()
            spec_match = query in (d.specialty or "").lower()
            dept_match = query in (d.department.dept_name if d.department else "").lower()

            if not query or name_match or spec_match or dept_match:
                results.append({
                    "id": d.id,
                    "name": d.username,
                    "specialty": d.specialty,
                    "department": d.department.dept_name if d.department else None,
                    "qualifications": d.qualifications,
                    "years_experience": d.years_experience,
                    "photo_url": d.photo_url
                })

        return {"doctors": results}, 200


class DoctorAvailabilityView(Resource):

    @auth_required('token')
    @roles_required('patient')
    def get(self, doctor_id):
        today = date.today().strftime("%Y-%m-%d")

        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id
        ).filter(DoctorAvailability.date >= today).all()

        slots = []
        for a in availability:
            if a.slot_1:
                slots.append({"date": a.date, "slot": "slot1", "label": "8:00 AM - 12:00 PM"})
            if a.slot_2:
                slots.append({"date": a.date, "slot": "slot2", "label": "4:00 PM - 9:00 PM"})

        booked = Appointments.query.filter_by(
            doctor_id=doctor_id,
            status="booked"
        ).filter(Appointments.date >= today).all()

        booked_slots = [{"date": b.date, "slot": b.time} for b in booked]

        return {
            "available_slots": slots,
            "booked_slots": booked_slots
        }, 200

# class BookAppointment(Resource):

#     @auth_required('token')
#     @roles_required('patient')
#     def post(self):
#         data      = request.get_json()
#         doctor_id = data.get("doctor_id")
#         date_str  = data.get("date")
#         slot      = data.get("slot")

#         if not doctor_id or not date_str or not slot:
#             return {"message": "doctor_id, date and slot are required"}, 400

#         if slot not in ["slot1", "slot2"]:
#             return {"message": "Invalid slot. Use slot1 or slot2"}, 400

#         doctor = User.query.get(doctor_id)
#         if not doctor:
#             return {"message": "Doctor not found"}, 404

#         availability = DoctorAvailability.query.filter_by(
#             doctor_id=doctor_id,
#             date=date_str
#         ).first()

#         if not availability:
#             return {"message": "Doctor is not available on this date"}, 400

#         if slot == "slot1" and not availability.slot_1:
#             return {"message": "Slot 1 is not available"}, 400

#         if slot == "slot2" and not availability.slot_2:
#             return {"message": "Slot 2 is not available"}, 400

#         existing = Appointments.query.filter_by(
#             doctor_id=doctor_id,
#             user_id=current_user.id,
#             date=date_str,
#             time=slot,
#             status="booked"
#         ).first()

#         if existing:
#             return {"message": "You already have an appointment in this slot"}, 400

#         doctor_conflict = Appointments.query.filter_by(
#             doctor_id=doctor_id,
#             date=date_str,
#             time=slot,
#             status="booked"
#         ).first()

#         if doctor_conflict:
#             return {"message": "This slot is already fully booked. Please choose another."}, 400

#         new_appt = Appointments(
#             doctor_id=doctor_id,
#             user_id=current_user.id,
#             date=date_str,
#             time=slot,
#             status="booked"
#         )
#         db.session.add(new_appt)
#         db.session.commit()

#         today = date.today().strftime("%Y-%m-%d")
#         cache.delete(f"availability:{doctor_id}:{today}")
#         print(f"[CACHE INVALIDATED] availability:{doctor_id}:{today}")

#         return {"message": "Appointment booked successfully", "appointment_id": new_appt.id}, 201


# class RescheduleAppointment(Resource):

#     @auth_required('token')
#     @roles_required('patient')
#     def put(self, appointment_id):
#         appt = Appointments.query.get(appointment_id)

#         if not appt:
#             return {"message": "Appointment not found"}, 404

#         if appt.user_id != current_user.id:
#             return {"message": "Unauthorized"}, 403

#         if appt.status != "booked":
#             return {"message": "Only booked appointments can be rescheduled"}, 400

#         data     = request.get_json()
#         new_date = data.get("date")
#         new_slot = data.get("slot")

#         if not new_date or not new_slot:
#             return {"message": "date and slot are required"}, 400

#         if new_slot not in ["slot1", "slot2"]:
#             return {"message": "Invalid slot. Use slot1 or slot2"}, 400

#         availability = DoctorAvailability.query.filter_by(
#             doctor_id=appt.doctor_id,
#             date=new_date
#         ).first()

#         if not availability:
#             return {"message": "Doctor is not available on this date"}, 400

#         if new_slot == "slot1" and not availability.slot_1:
#             return {"message": "Slot 1 is not available on this date"}, 400

#         if new_slot == "slot2" and not availability.slot_2:
#             return {"message": "Slot 2 is not available on this date"}, 400

#         appt.date = new_date
#         appt.time = new_slot
#         db.session.commit()

#         today = date.today().strftime("%Y-%m-%d")
#         cache.delete(f"availability:{appt.doctor_id}:{today}")
#         print(f"[CACHE INVALIDATED] availability:{appt.doctor_id}:{today}")

#         return {"message": "Appointment rescheduled successfully"}, 200


# class CancelAppointment(Resource):

#     @auth_required('token')
#     @roles_required('patient')
#     def put(self, appointment_id):
#         appt = Appointments.query.get(appointment_id)

#         if not appt:
#             return {"message": "Appointment not found"}, 404

#         if appt.user_id != current_user.id:
#             return {"message": "Unauthorized"}, 403

#         if appt.status != "booked":
#             return {"message": "Only booked appointments can be cancelled"}, 400

#         appt.status = "cancelled"
#         db.session.commit()

#         today = date.today().strftime("%Y-%m-%d")
#         cache.delete(f"availability:{appt.doctor_id}:{today}")
#         print(f"[CACHE INVALIDATED] availability:{appt.doctor_id}:{today}")

#         return {"message": "Appointment cancelled successfully"}, 200


# class PatientHistory(Resource):

#     @auth_required('token')
#     @roles_required('patient')
#     def get(self):
#         cache_key = f"patient:history:{current_user.id}"

#         cached = cache.get(cache_key)
#         if cached:
#             print(f"[CACHE HIT] patient:history:{current_user.id}")
#             return cached, 200

#         print(f"[CACHE MISS] patient:history:{current_user.id}")

#         appointments = Appointments.query.filter_by(
#             user_id=current_user.id
#         ).all()

#         history = []
#         for appt in appointments:
#             doctor    = User.query.get(appt.doctor_id)
#             treatment = Treatments.query.get(appt.treatment_id) if appt.treatment_id else None
#             history.append({
#                 "appointment_id": appt.id,
#                 "doctor_name": doctor.username if doctor else None,
#                 "department_name": doctor.department.dept_name if doctor and doctor.department else None,
#                 "date": appt.date,
#                 "time": appt.time,
#                 "status": appt.status,
#                 "treatment": {
#                     "diagnosis": treatment.diagnosis,
#                     "treatment": treatment.treatment,
#                     "prescription": treatment.prescription
#                 } if treatment else None
#             })

#         result = {
#             "patient": {
#                 "id": current_user.id,
#                 "name": current_user.username,
#                 "email": current_user.email,
#                 "contact_no": current_user.contact_no
#             },
#             "history": history
#         }

#         # 5 min TTL
#         cache.set(cache_key, result, timeout=300)
#         return result, 200


# class DoctorDetail(Resource):

#     @auth_required('token')
#     @roles_required('patient')
#     def get(self, doctor_id):
#         cache_key = f"doctor:detail:{doctor_id}"

#         cached = cache.get(cache_key)
#         if cached:
#             print(f"[CACHE HIT] doctor:detail:{doctor_id}")
#             return cached, 200

#         print(f"[CACHE MISS] doctor:detail:{doctor_id}")
#         doctor = User.query.get(doctor_id)
#         if not doctor:
#             return {"message": "Doctor not found"}, 404

#         result = {
#             "id": doctor.id,
#             "name": doctor.username,
#             "qualifications": doctor.qualifications,
#             "specialty": doctor.specialty,
#             "department": doctor.department.dept_name if doctor.department else None,
#             "years_experience": doctor.years_experience,
#             "years_specialist": doctor.years_specialist,
#             "bio": doctor.bio,
#             "photo_url": doctor.photo_url
#         }

#         # 10 min TTL
#         cache.set(cache_key, result, timeout=600)
#         return result, 200

class BookAppointment(Resource):

    @auth_required('token')
    @roles_required('patient')
    def post(self):
        data      = request.get_json()
        doctor_id = data.get("doctor_id")
        date_str  = data.get("date")
        slot      = data.get("slot")

        if not doctor_id or not date_str or not slot:
            return {"message": "doctor_id, date and slot are required"}, 400

        if slot not in ["slot1", "slot2"]:
            return {"message": "Invalid slot. Use slot1 or slot2"}, 400

        doctor = User.query.get(doctor_id)
        if not doctor:
            return {"message": "Doctor not found"}, 404

        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=date_str
        ).first()

        if not availability:
            return {"message": "Doctor is not available on this date"}, 400

        if slot == "slot1" and not availability.slot_1:
            return {"message": "Slot 1 is not available"}, 400

        if slot == "slot2" and not availability.slot_2:
            return {"message": "Slot 2 is not available"}, 400

        existing = Appointments.query.filter_by(
            doctor_id=doctor_id,
            user_id=current_user.id,
            date=date_str,
            time=slot,
            status="booked"
        ).first()

        if existing:
            return {"message": "You already have an appointment in this slot"}, 400

        doctor_conflict = Appointments.query.filter_by(
            doctor_id=doctor_id,
            date=date_str,
            time=slot,
            status="booked"
        ).first()

        if doctor_conflict:
            return {"message": "This slot is already fully booked. Please choose another."}, 400

        new_appt = Appointments(
            doctor_id=doctor_id,
            user_id=current_user.id,
            date=date_str,
            time=slot,
            status="booked"
        )
        db.session.add(new_appt)
        db.session.commit()

        return {"message": "Appointment booked successfully", "appointment_id": new_appt.id}, 201


class RescheduleAppointment(Resource):

    @auth_required('token')
    @roles_required('patient')
    def put(self, appointment_id):
        appt = Appointments.query.get(appointment_id)

        if not appt:
            return {"message": "Appointment not found"}, 404

        if appt.user_id != current_user.id:
            return {"message": "Unauthorized"}, 403

        if appt.status != "booked":
            return {"message": "Only booked appointments can be rescheduled"}, 400

        data     = request.get_json()
        new_date = data.get("date")
        new_slot = data.get("slot")

        if not new_date or not new_slot:
            return {"message": "date and slot are required"}, 400

        if new_slot not in ["slot1", "slot2"]:
            return {"message": "Invalid slot. Use slot1 or slot2"}, 400

        availability = DoctorAvailability.query.filter_by(
            doctor_id=appt.doctor_id,
            date=new_date
        ).first()

        if not availability:
            return {"message": "Doctor is not available on this date"}, 400

        if new_slot == "slot1" and not availability.slot_1:
            return {"message": "Slot 1 is not available on this date"}, 400

        if new_slot == "slot2" and not availability.slot_2:
            return {"message": "Slot 2 is not available on this date"}, 400

        appt.date = new_date
        appt.time = new_slot
        db.session.commit()

        return {"message": "Appointment rescheduled successfully"}, 200


class CancelAppointment(Resource):

    @auth_required('token')
    @roles_required('patient')
    def put(self, appointment_id):
        appt = Appointments.query.get(appointment_id)

        if not appt:
            return {"message": "Appointment not found"}, 404

        if appt.user_id != current_user.id:
            return {"message": "Unauthorized"}, 403

        if appt.status != "booked":
            return {"message": "Only booked appointments can be cancelled"}, 400

        appt.status = "cancelled"
        db.session.commit()

        return {"message": "Appointment cancelled successfully"}, 200


class PatientHistory(Resource):

    @auth_required('token')
    @roles_required('patient')
    def get(self):
        appointments = Appointments.query.filter_by(user_id=current_user.id).all()

        history = []
        for appt in appointments:
            doctor    = User.query.get(appt.doctor_id)
            treatment = Treatments.query.get(appt.treatment_id) if appt.treatment_id else None
            history.append({
                "appointment_id": appt.id,
                "doctor_name": doctor.username if doctor else None,
                "department_name": doctor.department.dept_name if doctor and doctor.department else None,
                "date": appt.date,
                "time": appt.time,
                "status": appt.status,
                "treatment": {
                    "diagnosis": treatment.diagnosis,
                    "treatment": treatment.treatment,
                    "prescription": treatment.prescription
                } if treatment else None
            })

        return {
            "patient": {
                "id": current_user.id,
                "name": current_user.username,
                "email": current_user.email,
                "contact_no": current_user.contact_no
            },
            "history": history
        }, 200


class DoctorDetail(Resource):

    @auth_required('token')
    @roles_required('patient')
    def get(self, doctor_id):
        doctor = User.query.get(doctor_id)
        if not doctor:
            return {"message": "Doctor not found"}, 404

        return {
            "id": doctor.id,
            "name": doctor.username,
            "qualifications": doctor.qualifications,
            "specialty": doctor.specialty,
            "department": doctor.department.dept_name if doctor.department else None,
            "years_experience": doctor.years_experience,
            "years_specialist": doctor.years_specialist,
            "bio": doctor.bio,
            "photo_url": doctor.photo_url
        }, 200