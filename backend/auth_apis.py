from flask_restful import Resource
from flask_security.utils import verify_password, logout_user, hash_password
from flask_security import utils
from flask import current_app as app, jsonify, request

from database import db
from user_data import user_database


@app.route('/api/register', methods=['POST'])
def create_user():
    credentials = request.get_json()
    if not user_database.find_user(email=credentials["email"]):
        user_database.create_user(
            email=credentials["email"],
            username=credentials["username"],
            password=hash_password(credentials["password"]),
            roles=['patient']
        )
        db.session.commit()
        return jsonify({"message": "User created....."}), 201

    return jsonify({"message": "User already exits"}), 400


@app.route('/api/check-email', methods=['POST'])
def check_email():
    data  = request.get_json()
    email = data.get("email", "").strip()

    if not email:
        return jsonify({"available": False}), 400

    exists = user_database.find_user(email=email)
    return jsonify({"available": not bool(exists)}), 200


@app.route('/api/check-username', methods=['POST'])
def check_username():
    data     = request.get_json()
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"available": False}), 400

    exists = user_database.find_user(username=username)
    return jsonify({"available": not bool(exists)}), 200


class LoginAPI(Resource):

    def post(self):
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"message": "Missing credentials"}, 400

        user = user_database.find_user(username=username)

        if not user:
            return {"message": "User not found"}, 404

        if not verify_password(password, user.password):
            return {"message": "Invalid password"}, 401

        if user.blacklist:
            return {"message": "You are blacklisted by admin, contact admin...."}, 403

        utils.login_user(user)
        token = user.get_auth_token()

        return {
            "message": "Login ho gaya",
            "username": user.username,
            "roles": [r.name for r in user.roles],
            "id": user.id,
            "auth_token": token
        }, 200


class LogoutAPI(Resource):

    def post(self):
        logout_user()
        return {"message": "You logged out!"}, 200