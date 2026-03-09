from functools import wraps
from flask_security import current_user
from flask import jsonify


# -------- AUTH CHECK -------- #
def auth_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:
            return jsonify({"message": "Login required"}), 401

        return fn(*args, **kwargs)

    return wrapper


# -------- ROLE CHECK -------- #
def role_required(role_name):

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:
                return jsonify({"message": "Login required"}), 401

            roles = [r.name for r in current_user.roles]

            if role_name not in roles:
                return jsonify({"message": "Unauthorized"}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


# -------- ADMIN SHORTCUT -------- #
def admin_required(fn):
    return role_required("admin")(fn)

