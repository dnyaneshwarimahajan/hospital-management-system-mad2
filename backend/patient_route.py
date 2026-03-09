from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

from patient_resources import (
    PatientDashboard,
    SearchDoctors,
    DoctorAvailabilityView,
    BookAppointment,
    RescheduleAppointment,
    CancelAppointment,
    PatientHistory,
    PatientDepartments,
    DepartmentDetail,
    DoctorDetail
)

patient_bp = Blueprint("patient", __name__)
# CORS(patient_bp,
#      origins="http://localhost:5173",
#      supports_credentials=True,
#      methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#      allow_headers=["Content-Type", "Authentication-Token"])

patient_api = Api(patient_bp)

# ---------------- ROUTES ---------------- #

patient_api.add_resource(PatientDashboard,       "/dashboard")
patient_api.add_resource(SearchDoctors,          "/doctors/search")
patient_api.add_resource(DoctorDetail, "/doctor/<int:doctor_id>")
patient_api.add_resource(DepartmentDetail, "/department/<int:dept_id>")
patient_api.add_resource(PatientDepartments, "/departments")
patient_api.add_resource(DoctorAvailabilityView, "/doctor/<int:doctor_id>/availability")
patient_api.add_resource(BookAppointment,        "/appointment/book")
patient_api.add_resource(RescheduleAppointment,  "/appointment/<int:appointment_id>/reschedule")
patient_api.add_resource(CancelAppointment,      "/appointment/<int:appointment_id>/cancel")
patient_api.add_resource(PatientHistory,         "/history")
# from csv_export_api import ExportCSV, ExportCSVStatus

# patient_api.add_resource(ExportCSV,       "/export-csv")
# patient_api.add_resource(ExportCSVStatus, "/export-csv/status/<task_id>")