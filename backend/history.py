from flask_restful import Resource
from flask_security import auth_required, roles_required




# ---------------- DOCTOR DASHBOARD ---------------- #
class HistoryDashboard(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self):
        return {"message": "Welcome to History Dashboard"}
