from datetime import date, timedelta
from flask_restful import Resource
from flask import request
from flask_security import auth_required, roles_required, current_user

from model import db, User, Appointments, Treatments, DoctorAvailability


class DoctorDashboard(Resource):

    @auth_required('token')
    @roles_required('doctor')
    def get(self):

        doctor_id = current_user.id
        today = date.today().strftime("%Y-%m-%d")
        week_end = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

        # -------- TODAY'S APPOINTMENTS -------- #

        today_appointments = Appointments.query.filter_by(
            doctor_id=doctor_id
        ).filter(Appointments.date == today).all()

        # -------- WEEK APPOINTMENTS -------- #

        week_appointments = Appointments.query.filter_by(
            doctor_id=doctor_id
        ).filter(
            Appointments.date >= today,
            Appointments.date <= week_end
        ).all()

        def format_appointment(appt):
            patient = User.query.get(appt.user_id)
            return {
                "id": appt.id,
                "patient_id": appt.user_id,
                "patient": patient.username if patient else None,
                "date": appt.date,
                "time": appt.time,
                "status": appt.status,
                "treatment_id": appt.treatment_id
            }

        # -------- ASSIGNED PATIENTS -------- #

        patient_ids = db.session.query(Appointments.user_id).filter_by(
            doctor_id=doctor_id
        ).distinct().all()

        patient_ids = [pid[0] for pid in patient_ids]
        patients = User.query.filter(User.id.in_(patient_ids)).all()

        patient_list = [{
            "id": p.id,
            "name": p.username,
            "email": p.email,
            "contact_no": p.contact_no
        } for p in patients]

        # -------- AVAILABILITY (next 7 days) -------- #

        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id
        ).filter(
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= week_end
        ).all()

        availability_list = [{
            "id": a.id,
            "date": a.date,
            "slot_1": a.slot_1,
            "slot_2": a.slot_2
        } for a in availability]

        return {
            "doctor": {
                "id": current_user.id,
                "name": current_user.username,
                "email": current_user.email,
                "department": current_user.department.dept_name if current_user.department else None,
                "specialty": current_user.specialty
            },
            "today_appointments": [format_appointment(a) for a in today_appointments],
            "week_appointments": [format_appointment(a) for a in week_appointments],
            "patients": patient_list,
            "availability": availability_list
        }, 200


class UpdateAppointmentStatus(Resource):

    @auth_required('token')
    @roles_required('doctor')
    def put(self, appointment_id):

        appt = Appointments.query.get(appointment_id)

        if not appt:
            return {"message": "Appointment not found"}, 404

        if appt.doctor_id != current_user.id:
            return {"message": "Unauthorized"}, 403

        data = request.get_json()
        status = data.get("status")

        if status not in ["booked", "completed", "cancelled"]:
            return {"message": "Invalid status. Use: booked, completed, cancelled"}, 400

        appt.status = status
        db.session.commit()

        return {"message": f"Appointment marked as {status}"}, 200


class AddTreatment(Resource):

    @auth_required('token')
    @roles_required('doctor')
    def post(self, appointment_id):

        appt = Appointments.query.get(appointment_id)

        if not appt:
            return {"message": "Appointment not found"}, 404

        if appt.doctor_id != current_user.id:
            return {"message": "Unauthorized"}, 403

        data = request.get_json()
        diagnosis = data.get("diagnosis")
        treatment = data.get("treatment")
        prescription = data.get("prescription", "")

        if not diagnosis or not treatment:
            return {"message": "Diagnosis and treatment are required"}, 400

        # If treatment already exists, update it
        if appt.treatment_id:
            existing = Treatments.query.get(appt.treatment_id)
            if existing:
                existing.diagnosis = diagnosis
                existing.treatment = treatment
                existing.prescription = prescription
                db.session.commit()
                return {"message": "Treatment updated"}, 200

        # Create new treatment
        new_treatment = Treatments(
            diagnosis=diagnosis,
            treatment=treatment,
            prescription=prescription
        )
        db.session.add(new_treatment)
        db.session.flush()  # get ID before commit

        appt.treatment_id = new_treatment.id
        appt.status = "completed"
        db.session.commit()

        return {"message": "Treatment added successfully", "treatment_id": new_treatment.id}, 201


class UpdateAvailability(Resource):

    @auth_required('token')
    @roles_required('doctor')
    def post(self):
        """Set/update availability for next 7 days"""

        data = request.get_json()
        # Expected: [{ "date": "2025-01-01", "slot_1": true, "slot_2": false }, ...]
        availability_data = data.get("availability", [])

        if not availability_data:
            return {"message": "No availability data provided"}, 400

        doctor_id = current_user.id

        for entry in availability_data:
            date_str = entry.get("date")
            slot_1 = entry.get("slot_1", False)
            slot_2 = entry.get("slot_2", False)

            if not date_str:
                continue

            # Check if record exists for this date
            existing = DoctorAvailability.query.filter_by(
                doctor_id=doctor_id,
                date=date_str
            ).first()

            if existing:
                existing.slot_1 = slot_1
                existing.slot_2 = slot_2
            else:
                new_avail = DoctorAvailability(
                    doctor_id=doctor_id,
                    date=date_str,
                    slot_1=slot_1,
                    slot_2=slot_2
                )
                db.session.add(new_avail)

        db.session.commit()
        return {"message": "Availability updated successfully"}, 200


class PatientMedicalHistory(Resource):

    @auth_required('token')
    @roles_required('doctor')
    def get(self, patient_id):

        # Verify this patient has appointments with this doctor
        appt_check = Appointments.query.filter_by(
            doctor_id=current_user.id,
            user_id=patient_id
        ).first()

        if not appt_check:
            return {"message": "Patient not assigned to you"}, 403

        patient = User.query.get(patient_id)
        if not patient:
            return {"message": "Patient not found"}, 404

        # Get all appointments for this patient with this doctor
        appointments = Appointments.query.filter_by(
            doctor_id=current_user.id,
            user_id=patient_id
        ).all()

        history = []
        for appt in appointments:
            treatment = Treatments.query.get(appt.treatment_id) if appt.treatment_id else None
            history.append({
                "appointment_id": appt.id,
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
                "id": patient.id,
                "name": patient.username,
                "email": patient.email,
                "contact_no": patient.contact_no
            },
            "history": history
        }, 200
    
class AppointmentDetail(Resource):

    @auth_required('token')
    @roles_required('doctor')
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
            "patient": patient.username if patient else "-",
            "date":    appt.date,
            "time":    appt.time,
            "status":  appt.status,
            "treatment": {
                "diagnosis":    treatment.diagnosis,
                "treatment":    treatment.treatment,
                "prescription": treatment.prescription
            } if treatment else None
        }, 200