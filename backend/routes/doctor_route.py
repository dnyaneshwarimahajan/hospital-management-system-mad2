from flask import Blueprint
from flask_restful import Api

from resources.doctor_resources import (
    DoctorDashboard,
    UpdateAppointmentStatus,
    AddTreatment,
    AppointmentDetail,
    UpdateAvailability,
    PatientMedicalHistory
)

doctor_bp = Blueprint("doctor", __name__)
doctor_api = Api(doctor_bp)

doctor_api.add_resource(DoctorDashboard, "/dashboard")
doctor_api.add_resource(UpdateAppointmentStatus, "/appointment/<int:appointment_id>/status")
doctor_api.add_resource(AddTreatment, "/appointment/<int:appointment_id>/treatment")
doctor_api.add_resource(UpdateAvailability, "/availability")
doctor_api.add_resource(PatientMedicalHistory,"/patient/<int:patient_id>/history")
doctor_api.add_resource(AppointmentDetail,"/appointment/<int:appointment_id>/detail")