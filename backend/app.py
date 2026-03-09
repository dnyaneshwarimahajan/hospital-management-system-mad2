from flask import Flask
from flask_security import Security, hash_password, auth_required
from flask_restful import Api
from flask_cors import CORS
from extensions import cache          # ✅ import from extensions

from database import db
from config import LocalDevelopementConfig
from user_data import user_database


def create_app():

    app = Flask(__name__)
    app.config.from_object(LocalDevelopementConfig)

    # ✅ Redis cache config
    app.config['CACHE_TYPE']            = 'RedisCache'
    app.config['CACHE_REDIS_HOST']      = 'localhost'
    app.config['CACHE_REDIS_PORT']      = 6379
    app.config['CACHE_REDIS_DB']        = 2
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    app.config['CACHE_KEY_PREFIX']      = 'hms:'

    db.init_app(app)
    cache.init_app(app)               # ✅ MUST be before app_context().push()

    CORS(app,
         resources={r"/api/*": {"origins": "http://localhost:5173"}},
         supports_credentials=True,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authentication-Token"])

    Security(app, user_database)

    app.app_context().push()          # ✅ push AFTER cache is registered

    api = Api(app, prefix="/api")

    with app.app_context():
        db.create_all()

        admin_role   = user_database.find_or_create_role(name="admin",   description="Administrator")
        doctor_role  = user_database.find_or_create_role(name="doctor",  description="Doctor")
        patient_role = user_database.find_or_create_role(name="patient", description="Patient")

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

from celery_config import celery

# -------- APIs -------- #
from auth_apis import LoginAPI, LogoutAPI

api.add_resource(LoginAPI,  "/login")
api.add_resource(LogoutAPI, "/logout")

from admin_route   import admin_bp
from doctor_route  import doctor_bp
from patient_route import patient_bp

app.register_blueprint(admin_bp,   url_prefix="/api/admin")
app.register_blueprint(doctor_bp,  url_prefix="/api/doctor")
app.register_blueprint(patient_bp, url_prefix="/api/patient")

# -------- Celery trigger routes -------- #
@app.route('/api/trigger-reminders', methods=['GET'])
def trigger_reminders():
    from task import send_daily_reminders
    send_daily_reminders.delay()
    return {"message": "Daily reminders triggered!"}, 200

@app.route('/api/trigger-monthly-report', methods=['GET'])
def trigger_monthly():
    from task import send_monthly_reports
    send_monthly_reports.delay()
    return {"message": "Monthly reports triggered!"}, 200

@app.route('/api/export-csv', methods=['POST'])
@auth_required('token')
def export_csv():
    from task import export_patient_csv
    from flask_security import current_user
    task = export_patient_csv.delay(current_user.id)
    return {"message": "Export started! You will receive an email once ready.", "task_id": task.id}, 202


if __name__ == "__main__":
    app.run(debug=True)