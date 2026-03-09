from datetime import date, datetime
import csv, io

from celery_config import celery
from dateutil.relativedelta import relativedelta
from database import db


# ------ helper ------
def slot_time(slot):
    return "8:00 AM - 12:00 PM" if slot == "slot1" else "4:00 PM - 9:00 PM"


# ------ Task 1: Daily reminders (runs 8AM every day) ------

@celery.task(name="task.send_daily_reminders")
def send_daily_reminders():
    from app import app
    from mail import send_email
    from model import User, Appointments

    with app.app_context():
        today = date.today().strftime("%Y-%m-%d")
        appointments = Appointments.query.filter_by(date=today, status="booked").all()

        count = 0
        for appt in appointments:
            patient = User.query.get(appt.user_id)
            doctor  = User.query.get(appt.doctor_id)

            if not patient or not patient.email:
                continue

            doctor_name = f"Dr. {doctor.username}" if doctor else "your doctor"
            time_slot   = slot_time(appt.time)


            # ── Email ──────────────────────────────────────────────────────
            if patient.email:
                send_email(
                    to_email=patient.email,
                    subject="Reminder: Hospital Appointment Today",
                    body=f"""
                        <p>Hi <b>{patient.username}</b>,</p>
                        <p>You have an appointment today with
                        <b>{doctor_name}</b> at <b>{time_slot}</b>.</p>
                        <p>Please arrive on time.</p>
                        <p>— HMS Team</p>
                    """
                )

            count += 1

        print(f"Daily reminders sent: {count}")
        return f"Sent {count} reminders"

            

           

# ------ Task 2: Monthly report for doctors (runs 1st of every month) ------

@celery.task(name="task.send_monthly_reports")
def send_monthly_reports():
    from app import app
    from mail import send_email
    from model import User, Role, Appointments, Treatments

    with app.app_context():
        today = date.today()
        
        last_month = today.replace(day=1) - relativedelta(months=1)
        month, year = last_month.month, last_month.year
        month = today.month - 1 or 12
        year  = today.year if today.month > 1 else today.year - 1
        month_str  = f"{year}-{str(month).zfill(2)}"
        month_name = datetime(year, month, 1).strftime("%B %Y")

        doctors = User.query.join(User.roles).filter(Role.name == "doctor").all()

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
                patient   = User.query.get(appt.user_id)
                treatment = Treatments.query.get(appt.treatment_id) if appt.treatment_id else None
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

            total     = len(appointments)
            completed = sum(1 for a in appointments if a.status == "completed")
            cancelled = sum(1 for a in appointments if a.status == "cancelled")

            send_email(
                to_email=doctor.email,
                subject=f"Monthly Report — {month_name}",
                body=f"""
                    <p>Hi Dr. <b>{doctor.username}</b>,</p>
                    <p>Here's your activity summary for <b>{month_name}</b>:</p>
                    <ul>
                        <li>Total: {total}</li>
                        <li>Completed: {completed}</li>
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


# ------ Task 3: CSV export (user triggered) ------

@celery.task(name="task.export_patient_csv")
def export_patient_csv(patient_id):
    from app import app
    from mail import send_email
    from model import User, Appointments, Treatments

    with app.app_context():
        patient = User.query.get(patient_id)
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
            doctor    = User.query.get(appt.doctor_id)
            treatment = Treatments.query.get(appt.treatment_id) if appt.treatment_id else None
            writer.writerow([
                appt.id,
                patient.username,
                f"Dr. {doctor.username}" if doctor else "-",
                doctor.department.dept_name if doctor and doctor.department else "-",
                appt.date,
                slot_time(appt.time),
                appt.status,
                treatment.diagnosis    if treatment else "-",
                treatment.treatment    if treatment else "-",
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
                <p>— HMS Team</p>
            """,
            attachment=csv_data,
            filename=f"history_{patient.username}.csv"
        )

        print(f"CSV sent to {patient.email}")
        return f"CSV sent to {patient.email}"