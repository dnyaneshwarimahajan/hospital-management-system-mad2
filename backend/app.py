from flask import Flask
from flask_security import Security, hash_password, auth_required
from flask_restful import Api
from flask_cors import CORS
from database import db
from config import LocalDevelopementConfig
from user_data import user_database


def create_app():

    app = Flask(__name__)
    app.config.from_object(LocalDevelopementConfig)

    db.init_app(app)
    CORS(app,
     origins="http://localhost:5173",
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authentication-Token"])

    Security(app, user_database)

    api = Api(app, prefix="/api")

    with app.app_context():
        db.create_all()

        admin_role   = user_database.find_or_create_role(name="admin", description="Administrator")
        user_database.find_or_create_role(name="doctor",  description="Doctor")
        user_database.find_or_create_role(name="patient", description="Patient")

        if not user_database.find_user(email="admin@gmail.com"):
            user_database.create_user(
                username="admin",
                email="admin@gmail.com",
                password=hash_password("admin123"),
                roles=[admin_role]
            )
        db.session.commit()

    return app, api


app, api = create_app()

app.app_context().push()

from backend_jobs.celery_config import celery
from auth_apis import LoginAPI, LogoutAPI

api.add_resource(LoginAPI,  "/login")

api.add_resource(LogoutAPI, "/logout")

from routes.admin_route import admin_bp
from routes.doctor_route import doctor_bp
from routes.patient_route import patient_bp

app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(doctor_bp,url_prefix="/api/doctor")
app.register_blueprint(patient_bp, url_prefix="/api/patient")

@app.route('/api/trigger-reminders', methods=['GET'])
def trigger_reminders():
    from backend_jobs.task import send_daily_reminders
    send_daily_reminders.delay()
    return {"message": "Daily reaminder trigger ho gaya"}, 200

@app.route('/api/trigger-monthly-report', methods=['GET'])
def trigger_monthly():
    from backend_jobs.task import send_monthly_reports
    send_monthly_reports.delay()
    return {"message": "Monthly remainder trigger ho gaya"}, 200

@app.route('/api/export-csv', methods=['POST'])
@auth_required('token')
def export_csv():
    from backend_jobs.task import export_patient_csv
    from flask_security import current_user
    task = export_patient_csv.delay(current_user.id)
    return {"message": "Export started! You will receive an email after some time", "task_id": task.id}, 202


if __name__ == "__main__":
    app.run(debug=True)