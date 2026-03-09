from flask import Blueprint
from flask_restful import Api

# Import all admin Resource classes
from admin_resources import (
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



from flask_cors import CORS

admin_bp = Blueprint("admin", __name__)
# CORS(admin_bp,
#      origins="http://localhost:5173",
#      supports_credentials=True,
#      methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#      allow_headers=["Content-Type", "Authentication-Token"])


# 🔹 Attach Api to Blueprint
admin_api = Api(admin_bp)

# ---------------- ROUTES ---------------- #

# Dashboard
admin_api.add_resource(AdminDashboard, "/dashboard")

# Doctor APIs
admin_api.add_resource(CreateDoctor, "/create-doctor", "/departments")
admin_api.add_resource(EditDoctor, "/edit-doctor/<int:user_id>")
admin_api.add_resource(DeleteDoctor, "/delete-doctor/<int:user_id>")

# Patient APIs
admin_api.add_resource(EditPatient, "/edit-patient/<int:user_id>")
admin_api.add_resource(DeletePatient, "/delete-patient/<int:user_id>")
admin_api.add_resource(AdminPatientHistory, "/patient/<int:patient_id>/history") 

# Blacklist APIs
admin_api.add_resource(BlacklistUser, "/blacklist/<int:user_id>")
admin_api.add_resource(UnblacklistUser, "/unblacklist/<int:user_id>")
admin_api.add_resource(AllAppointments, "/appointments/all")
