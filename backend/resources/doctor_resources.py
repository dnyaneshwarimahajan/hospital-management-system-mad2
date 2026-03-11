from datetime import date, timedelta

from flask import request
from flask_restful import Resource
from flask_security import auth_required, roles_required, current_user
from models.model import db, User, Appointments, Treatments, DoctorAvailability

VALID_STATUSES = {"booked", "completed", "cancelled"}

def get_appointment(appointment_id):
    appt = db.session.get(Appointments, appointment_id)
    if not appt:
        return None, ({"message": "Appointment not found"}, 404)
    if appt.doctor_id != current_user.id:
        return None, ({"message": "Unauthorized"}, 403)
    return appt, None


def appointment(appt):
    patient = db.session.get(User, appt.user_id)
    return {
        "id": appt.id,"patient_id": appt.user_id,"patient": patient.username if patient else None,"date": appt.date, "time": appt.time,"status": appt.status,"treatment_id": appt.treatment_id,
    }


def treatment(treatment):
    if not treatment:
        return None
    return {
        "diagnosis": treatment.diagnosis,
        "treatment": treatment.treatment,
        "prescription": treatment.prescription,
    }
class DoctorDashboard(Resource):

    @auth_required("token")
    @roles_required("doctor")
    def get(self):
        today    = date.today().strftime("%Y-%m-%d")
        week_end = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

        today_appointments = Appointments.query.filter_by(
            doctor_id=current_user.id, status="booked", date=today
        ).all()

        week_appointments = Appointments.query.filter(
            Appointments.doctor_id == current_user.id,
            Appointments.status == "booked",
            Appointments.date >= today,
            Appointments.date <= week_end,
        ).all()

        patients = User.query.filter(
            User.id.in_(
                db.session.query(Appointments.user_id)
                .filter_by(doctor_id=current_user.id)
                .distinct()
            )
        ).all()

        availability = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == current_user.id,
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= week_end,
        ).all()

        return {
            "doctor": {
                "id":current_user.id,
                "name": current_user.username,
                "email": current_user.email,
                "department": current_user.department.dept_name if current_user.department else None,
            },
            "today_appointments": [appointment(a) for a in today_appointments],
            "week_appointments":  [appointment(a) for a in week_appointments],
            "patients": [
                {"id": p.id, "name": p.username, "email": p.email, "contact_no": p.contact_no}
                for p in patients
            ],
            "availability": [
                {"id": a.id, "date": a.date, "slot_1": a.slot_1, "slot_2": a.slot_2}
                for a in availability
            ],
        }, 200
    
class UpdateAppointmentStatus(Resource):

    @auth_required("token")
    @roles_required("doctor")
    def put(self, appointment_id):
        appt = db.session.get(Appointments, appointment_id)
        if not appt:
            return {"message": "Appointment not found"}, 404
        if appt.doctor_id != current_user.id:
            return {"message": "Unauthorized"}, 403

        status = request.get_json().get("status")
        if status not in VALID_STATUSES:
            return {"message": "Invalid status. Use: VALID_STATUSES"}, 400

        appt.status = status
        db.session.commit()
        return {"message": f"Appointment marked as {status}"}, 200
    
class AddTreatment(Resource):

    @auth_required("token")
    @roles_required("doctor")
    def post(self, appointment_id):
        appt = db.session.get(Appointments, appointment_id)
        if not appt:
            return {"message": "Appointment not found"}, 404
        if appt.doctor_id != current_user.id:
            return {"message": "Unauthorized"}, 403

        data         = request.get_json()
        diagnosis    = data.get("diagnosis")
        treatment    = data.get("treatment")
        prescription = data.get("prescription", "")

        if not diagnosis or not treatment:
            return {"message": "Diagnosis and treatment are required"}, 400

        if appt.treatment_id:
            t = db.session.get(Treatments, appt.treatment_id)
            t.diagnosis = diagnosis
            t.treatment = treatment
            t.prescription = prescription
            db.session.commit()
            return {"message": "Treatment updated"}, 200

        t = Treatments(diagnosis=diagnosis, treatment=treatment, prescription=prescription)
        db.session.add(t)
        db.session.flush()

        appt.treatment_id = t.id
        appt.status = "completed"
        db.session.commit()
        return {"message": "Treatment added successfully"}, 201

class UpdateAvailability(Resource):

    @auth_required("token")
    @roles_required("doctor")
    def post(self):
        availability_data = request.get_json().get("availability", [])
        if not availability_data:
            return {"message": "No availability data provided"}, 400

        doctor_id = current_user.id

        for entry in availability_data:
            date_str = entry.get("date")
            if not date_str:
                continue

            existing = DoctorAvailability.query.filter_by(
                doctor_id=doctor_id, date=date_str
            ).first()

            if existing:
                existing.slot_1 = entry.get("slot_1", False)
                existing.slot_2 = entry.get("slot_2", False)
            else:
                db.session.add(DoctorAvailability(
                    doctor_id=doctor_id,
                    date=date_str,
                    slot_1=entry.get("slot_1", False),
                    slot_2=entry.get("slot_2", False),
                ))

        db.session.commit()
        return {"message": "Availability updated successfully"}, 200


class PatientMedicalHistory(Resource):

    @auth_required("token")
    @roles_required("doctor")
    def get(self, patient_id):
        if not Appointments.query.filter_by(
            doctor_id=current_user.id, user_id=patient_id
        ).first():
            return {"message": "Patient not assigned to you"}, 403

        patient = db.session.get(User, patient_id)
        if not patient:
            return {"message": "Patient not found"}, 404

        appointments = Appointments.query.filter_by(
            doctor_id=current_user.id, user_id=patient_id
        ).all()

        history = [
            {
                "appointment_id": appt.id,
                "date": appt.date,
                "time": appt.time,
                "status": appt.status,
                "treatment": treatment(
                    db.session.get(Treatments, appt.treatment_id) if appt.treatment_id else None
                ),
            }
            for appt in appointments
        ]

        return {
            "patient": {
                "id": patient.id,
                "name": patient.username,
                "email": patient.email,
                "contact_no": patient.contact_no,
            },
            "history": history,
        }, 200


class AppointmentDetail(Resource):

    @auth_required("token")
    @roles_required("doctor")
    def get(self, appointment_id):
        appt = db.session.get(Appointments, appointment_id)
        if not appt:
            return {"message": "Appointment not found"}, 404
        if appt.doctor_id != current_user.id:
            return {"message": "Unauthorized"}, 403

        patient   = db.session.get(User, appt.user_id)
        treatment = db.session.get(Treatments, appt.treatment_id) if appt.treatment_id else None

        return {
            "id":      appt.id,
            "patient": patient.username,
            "date":    appt.date,
            "time":    appt.time,
            "status":  appt.status,
            "treatment": {
                "diagnosis":    treatment.diagnosis,
                "treatment":    treatment.treatment,
                "prescription": treatment.prescription,
            } if treatment else None,
        }, 200