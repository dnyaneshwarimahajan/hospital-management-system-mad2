from datetime import date, datetime
import csv, io
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from backend_jobs.celery_config import celery
from database import db


def slot_time(slot):
    return "8:00 AM - 12:00 PM" if slot == "slot1" else "4:00 PM - 9:00 PM"


@celery.task(name="backend_jobs.task.send_daily_reminders")
def send_daily_reminders():
    from backend_jobs.mail import send_email
    from models.model import User, Appointments

    with app.app_context():
        today = date.today().strftime("%Y-%m-%d")
        appointments = Appointments.query.filter_by(date=today, status="booked").all()

        count = 0
        for appt in appointments:
            patient = db.session.get(User, appt.user_id)    
            doctor  = db.session.get(User, appt.doctor_id)  

            if not patient or not patient.email:
                continue

            doctor_name = f"Dr. {doctor.username}" if doctor else "Doctor"
            time_slot = slot_time(appt.time)

            send_email(
                to_email=patient.email,
                subject="Reminder: You have a Hospital Appointment Today",
                body=f"""
                    <p>Hello <b>{patient.username}</b>,</p>
                    <p>You have an appointment today with
                    <b>{doctor_name}</b> at <b>{time_slot}</b>.</p>
                    <p>Please be present on time.</p>
                """
            )
            count += 1

        print(f"Daily reminders sent: {count}")
        return f"Sent {count} reminders"


@celery.task(name="backend_jobs.task.send_monthly_reports")
def send_monthly_reports():
    from backend_jobs.mail import send_email
    from models.model import User, Appointments, Treatments

    with app.app_context():
        today = date.today()
        month = today.month - 1 or 12
        year = today.year if today.month > 1 else today.year - 1
        month_str  = f"{year}-{str(month).zfill(2)}"
        month_name = datetime(year, month, 1).strftime("%B %Y")

        doctors = User.query.filter(User.roles.any(name="doctor")).all()

        count = 0
        for doctor in doctors:
            if not doctor.email:
                continue

            appointments = Appointments.query.filter(
                Appointments.doctor_id == doctor.id,
                Appointments.date.like(f"{month_str}%")
            ).all()

            rows = ""
            for i, appt in enumerate(appointments):
                patient = db.session.get(User, appt.user_id)                                              
                treatment = db.session.get(Treatments, appt.treatment_id) if appt.treatment_id else None    

                rows += f"""<tr>
                    <td>{i+1}</td>
                    <td>{patient.username if patient else '-'}</td>
                    <td>{appt.date}</td>
                    <td>{slot_time(appt.time)}</td>
                    <td>{appt.status}</td>
                    <td>{treatment.diagnosis if treatment else '-'}</td>
                    <td>{treatment.treatment if treatment else '-'}</td>
                    <td>{treatment.prescription if treatment else '-'}</td>
                </tr>"""

            total = len(appointments)
            completed = sum(1 for a in appointments if a.status == "completed")
            cancelled = sum(1 for a in appointments if a.status == "cancelled")

            send_email(
                to_email=doctor.email,
                subject=f"Monthly Report — {month_name}",
                body=f"""
                    <p>Hi Dr. <b>{doctor.username}</b>,</p>
                    <p>Here is your activity for <b>{month_name}</b>:</p>
                    <ul>
                        <li>Total: {total}</li>
                        <li>Completed:{completed}</li>
                        <li>Cancelled: {cancelled}</li>
                    </ul>
                    <table border="1" cellpadding="6" cellspacing="0"
                        style="border-collapse:collapse; width:100%;">
                        <thead style="background:#eafaf7;">
                            <tr>
                                <th>#</th><th>Patient</th><th>Date</th><th>Time</th>
                                <th>Status</th><th>Diagnosis</th><th>Treatment</th><th>Prescription</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows if rows else '<tr><td colspan="8">No appointments this month.</td></tr>'}
                        </tbody>
                    </table>
                    <p>— HMS Team</p>
                """
            )
            count += 1

        print(f"Monthly reports sent: {count}")
        return f"Sent {count} reports"


@celery.task(name="backend_jobs.task.export_patient_csv")
def export_patient_csv(patient_id):
    from backend_jobs.mail import send_email
    from models.model import User, Appointments, Treatments

    with app.app_context():
        patient = db.session.get(User, patient_id)  
        if not patient:
            return "Patient not found"

        appointments = Appointments.query.filter_by(user_id=patient_id).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Appointment ID", "Patient", "Doctor", "Department",
            "Date", "Time", "Status", "Diagnosis", "Treatment", "Prescription"
        ])

        for appt in appointments:
            doctor = db.session.get(User, appt.doctor_id)                                           
            treatment = db.session.get(Treatments, appt.treatment_id) if appt.treatment_id else None    

            writer.writerow([
                appt.id,
                patient.username,
                f"Dr. {doctor.username}" if doctor else "-",
                doctor.department.dept_name if doctor and doctor.department else "-",
                appt.date,
                slot_time(appt.time),
                appt.status,
                treatment.diagnosis if treatment else "-",
                treatment.treatment if treatment else "-",
                treatment.prescription if treatment else "-",
            ])

        csv_data = output.getvalue()
        output.close()

        send_email(
            to_email=patient.email,
            subject="Your Treatment History Export",
            body=f"""
                <p>Hi <b>{patient.username}</b>,</p>
                <p>Your treatment history export is ready.
                Please find the CSV file attached.</p>
            """,
            attachment=csv_data,
            filename=f"history_{patient.username}.csv"
        )

        print(f"CSV sent to {patient.email}")
        return f"CSV sent to {patient.email}"