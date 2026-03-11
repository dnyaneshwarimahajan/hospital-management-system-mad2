from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS 

from resources.patient_resources import (
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
patient_api = Api(patient_bp)

patient_api.add_resource(PatientDashboard, "/dashboard")
patient_api.add_resource(SearchDoctors, "/doctors/search")
patient_api.add_resource(DoctorDetail, "/doctor/<int:doctor_id>")
patient_api.add_resource(DepartmentDetail, "/department/<int:dept_id>")
patient_api.add_resource(PatientDepartments, "/departments")
patient_api.add_resource(DoctorAvailabilityView, "/doctor/<int:doctor_id>/availability")
patient_api.add_resource(BookAppointment, "/appointment/book")
patient_api.add_resource(RescheduleAppointment, "/appointment/<int:appointment_id>/reschedule")
patient_api.add_resource(CancelAppointment, "/appointment/<int:appointment_id>/cancel")
patient_api.add_resource(PatientHistory, "/history")