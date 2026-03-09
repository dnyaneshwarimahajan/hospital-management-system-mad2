from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

from doctor_resources import (
    DoctorDashboard,
    UpdateAppointmentStatus,
    AddTreatment,
    AppointmentDetail,
    UpdateAvailability,
    PatientMedicalHistory
)

doctor_bp = Blueprint("doctor", __name__)
# CORS(doctor_bp,
#      origins="http://localhost:5173",
#      supports_credentials=True,
#      methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#      allow_headers=["Content-Type", "Authentication-Token"])

doctor_api = Api(doctor_bp)

# ---------------- ROUTES ---------------- #

doctor_api.add_resource(DoctorDashboard,          "/dashboard")
doctor_api.add_resource(UpdateAppointmentStatus,  "/appointment/<int:appointment_id>/status")
doctor_api.add_resource(AddTreatment,             "/appointment/<int:appointment_id>/treatment")
doctor_api.add_resource(UpdateAvailability,       "/availability")
doctor_api.add_resource(PatientMedicalHistory,    "/patient/<int:patient_id>/history")
doctor_api.add_resource(AppointmentDetail, "/appointment/<int:appointment_id>/detail")  # ← add this