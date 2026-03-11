from datetime import date
from flask import request
from flask_restful import Resource
from flask_security import auth_required, roles_required, current_user

from models.model import db, User, Role, Dept, Appointments, Treatments, DoctorAvailability


VALID_SLOTS = {"slot1", "slot2"}

SLOT_LABELS = {
    "slot1": "8:00 AM - 12:00 PM",
    "slot2": "4:00 PM - 9:00 PM",
}

def today_str():
    return date.today().strftime("%Y-%m-%d")


def get_appointment(appointment_id):
    appt = db.session.get(Appointments, appointment_id)
    if not appt:
        return None, ({"message": "Appointment not found"}, 404)
    if appt.user_id != current_user.id:
        return None, ({"message": "Unauthorized"}, 403)
    return appt, None


def format_appointment(appt, include_treatment=False):
    doctor = db.session.get(User, appt.doctor_id)
    result = {
        "id": appt.id,
        "doctor_id": appt.doctor_id,
        "doctor": doctor.username,
        "department": doctor.department.dept_name if doctor.department else None,
        "date": appt.date,
        "time": appt.time,
        "status": appt.status,
    }
    if include_treatment and appt.treatment_id:
        t = db.session.get(Treatments, appt.treatment_id)
        result["treatment"] = {
            "diagnosis": t.diagnosis,
            "treatment": t.treatment,
            "prescription": t.prescription,
        } if t else None
    return result

def slot_available(availability, slot):
    slot_field = "slot_1" if slot == "slot1" else "slot_2"
    if not getattr(availability, slot_field):
        label = "1" if slot == "slot1" else "2"
        return {"message": f"Slot {label} is not available"}, 400
    return None


def _current_patient():
    return {
        "id": current_user.id,
        "name": current_user.username,
        "email": current_user.email,
        "contact_no": current_user.contact_no,
    }


class PatientDashboard(Resource):

    @auth_required("token")
    @roles_required("patient")
    def get(self):
        today = today_str()
        base = Appointments.query.filter_by(user_id=current_user.id)

        upcoming = base.filter(Appointments.date >= today, Appointments.status == "booked").all()
        past = base.filter(Appointments.date < today).all()

        return {
            "patient": _current_patient(),
            "upcoming_appointments": [format_appointment(a) for a in upcoming],
            "past_appointments": [format_appointment(a, include_treatment=True) for a in past],
        }, 200


class PatientHistory(Resource):

    @auth_required("token")
    @roles_required("patient")
    def get(self):
        appointments = Appointments.query.filter_by(user_id=current_user.id).all()
        return {
            "patient": _current_patient(),
            "history": [format_appointment(a, include_treatment=True) for a in appointments],
        }, 200


class PatientDepartments(Resource):

    @auth_required("token")
    @roles_required("patient")
    def get(self):
        depts = Dept.query.all()
        return {
            "departments": [
                {"id": d.id, "dept_name": d.dept_name, "description": d.description}
                for d in depts
            ]
        }, 200


class DepartmentDetail(Resource):

    @auth_required("token")
    @roles_required("patient")
    def get(self, dept_id):
        dept = db.session.get(Dept, dept_id)
        if not dept:
            return {"message": "Department not found"}, 404

        doctor_role = Role.query.filter_by(name="doctor").first()
        doctors = User.query.filter(
            User.department_id == dept_id,
            User.roles.any(id=doctor_role.id)
        ).all() if doctor_role else []

        return {
            "department": {"id": dept.id, "dept_name": dept.dept_name, "description": dept.description},
            "doctors": [
                {
                    "id": d.id,
                    "name": d.username,
                    "email": d.email,
                    "contact_no": d.contact_no,
                    "qualifications": d.qualifications,
                    "blacklisted": d.blacklist,
                }
                for d in doctors
            ],
        }, 200


class SearchDoctors(Resource):

    @auth_required("token")
    @roles_required("patient")
    def get(self):
        query = request.args.get("q", "").lower().strip()
        doctors = User.query.join(User.roles).filter(Role.name == "doctor").all()

        def matches(d):
            if not query:
                return True
            dept = d.department.dept_name if d.department else ""
            return any(query in field.lower() for field in [d.username, d.qualifications or "", dept])

        return {
            "doctors": [
                {
                    "id": d.id,
                    "name": d.username,
                    "department": d.department.dept_name if d.department else None,
                    "qualifications": d.qualifications,
                    "years_experience": d.years_experience,
                    "photo_url": d.photo_url,
                }
                for d in doctors if matches(d)
            ]
        }, 200


class DoctorDetail(Resource):

    @auth_required("token")
    @roles_required("patient")
    def get(self, doctor_id):
        doctor = db.session.get(User, doctor_id)
        if not doctor:
            return {"message": "Doctor not found"}, 404

        return {
            "id": doctor.id,
            "name": doctor.username,
            "qualifications": doctor.qualifications,
            "department": doctor.department.dept_name if doctor.department else None,
            "years_experience": doctor.years_experience,
            "bio": doctor.bio,
            "photo_url": doctor.photo_url,
        }, 200


class DoctorAvailabilityView(Resource):

    @auth_required("token")
    @roles_required("patient")
    def get(self, doctor_id):
        today = today_str()
        availability = DoctorAvailability.query.filter_by(doctor_id=doctor_id).filter(
            DoctorAvailability.date >= today
        ).all()

        available_slots = [
            {"date": a.date, "slot": slot, "label": SLOT_LABELS[slot]}
            for a in availability
            for slot, flag in [("slot1", a.slot_1), ("slot2", a.slot_2)]
            if flag
        ]

        booked_slots = [
            {"date": b.date, "slot": b.time}
            for b in Appointments.query.filter_by(
                doctor_id=doctor_id, status="booked"
            ).filter(Appointments.date >= today).all()
        ]

        return {"available_slots": available_slots, "booked_slots": booked_slots}, 200


class BookAppointment(Resource):

    @auth_required("token")
    @roles_required("patient")
    def post(self):
        data = request.get_json()
        doctor_id = data.get("doctor_id")
        date_str  = data.get("date")
        slot = data.get("slot")

        if not all([doctor_id, date_str, slot]):
            return {"message": "doctor_id, date and slot are required"}, 400
        if slot not in VALID_SLOTS:
            return {"message": "Invalid slot. Use slot1 or slot2"}, 400
        if not db.session.get(User, doctor_id):
            return {"message": "Doctor not found"}, 404

        availability = DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=date_str).first()
        if not availability:
            return {"message": "Doctor is not available on this date"}, 400

        err = slot_available(availability, slot)
        if err:
            return err

        if Appointments.query.filter_by(
            doctor_id=doctor_id, user_id=current_user.id,
            date=date_str, time=slot, status="booked"
        ).first():
            return {"message": "You already have an appointment in this slot"}, 400

        if Appointments.query.filter_by(
            doctor_id=doctor_id, date=date_str, time=slot, status="booked"
        ).first():
            return {"message": "This slot is already fully booked. Please choose another."}, 400

        new_appt = Appointments(
            doctor_id=doctor_id,
            user_id=current_user.id,
            date=date_str,
            time=slot,
            status="booked",
        )
        db.session.add(new_appt)
        db.session.commit()
        return {"message": "Appointment booked successfully", "appointment_id": new_appt.id}, 201


class RescheduleAppointment(Resource):

    @auth_required("token")
    @roles_required("patient")
    def put(self, appointment_id):
        appt, err = get_appointment(appointment_id)
        if err:
            return err
        if appt.status != "booked":
            return {"message": "Only booked appointments can be rescheduled"}, 400

        data = request.get_json()
        new_date = data.get("date")
        new_slot = data.get("slot")

        if not new_date or not new_slot:
            return {"message": "date and slot are required"}, 400
        if new_slot not in VALID_SLOTS:
            return {"message": "Invalid slot. Use slot1 or slot2"}, 400

        availability = DoctorAvailability.query.filter_by(
            doctor_id=appt.doctor_id, date=new_date
        ).first()
        if not availability:
            return {"message": "Doctor is not available on this date"}, 400

        err = slot_available(availability, new_slot)
        if err:
            return err

        appt.date = new_date
        appt.time = new_slot
        db.session.commit()
        return {"message": "Appointment rescheduled successfully"}, 200


class CancelAppointment(Resource):

    @auth_required("token")
    @roles_required("patient")
    def put(self, appointment_id):
        appt, err = get_appointment(appointment_id)
        if err:
            return err
        if appt.status != "booked":
            return {"message": "Only booked appointments can be cancelled"}, 400

        appt.status = "cancelled"
        db.session.commit()
        return {"message": "Appointment cancelled successfully"}, 200
