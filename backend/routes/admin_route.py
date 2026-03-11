from flask import Blueprint
from flask_restful import Api

from resources.admin_resources import (
    AdminDashboard,
    CreateDoctor,
    EditDoctor,
    DeleteDoctor,
    EditPatient,
    DeletePatient,
    BlacklistUser,
    UnblacklistUser,
    AdminPatientHistory,
    AllAppointments
)

admin_bp = Blueprint("admin", __name__)
admin_api = Api(admin_bp)

admin_api.add_resource(AdminDashboard, "/dashboard")

admin_api.add_resource(CreateDoctor, "/create-doctor", "/departments")
admin_api.add_resource(EditDoctor, "/edit-doctor/<int:user_id>")
admin_api.add_resource(DeleteDoctor, "/delete-doctor/<int:user_id>")

admin_api.add_resource(EditPatient, "/edit-patient/<int:user_id>")
admin_api.add_resource(DeletePatient, "/delete-patient/<int:user_id>")
admin_api.add_resource(AdminPatientHistory, "/patient/<int:patient_id>/history")

admin_api.add_resource(BlacklistUser, "/blacklist/<int:user_id>")
admin_api.add_resource(UnblacklistUser, "/unblacklist/<int:user_id>")
admin_api.add_resource(AllAppointments, "/appointments/all")