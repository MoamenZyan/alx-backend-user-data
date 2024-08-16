#!/usr/bin/env python3
"""
My flask app
"""

from flask import Flask, abort, jsonify, request, redirect, url_for
from auth import Auth

app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.url_map.strict_slashes = False
AUTH = Auth()


@app.route("/")
def home() -> str:
    """ Home API
        Return:
            - Logout message JSON
    """
    return jsonify({"message": "Bienvenue"})


@app.route("/sessions", methods=["POST"])
def login():
    """ Login API
        Form fields:
            - email
            - password
        Return:
            - user email and login message JSON
            - 401 if credential are invalid
    """
    email = request.form.get("email")
    password = request.form.get("password")
    if not AUTH.valid_login(email, password):
        abort(401)
    ssid = AUTH.create_session(email)
    response = jsonify({"email": email, "message": "logged in"})
    response.set_cookie("session_id", ssid)
    return response


@app.route("/sessions", methods=["DELETE"])
def logout():
    """ Logout API
        Return:
            - redirect to home page
    """
    ssid = request.cookies.get("session_id")
    user = AUTH.get_user_from_ssid(ssid)
    if not user:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect(url_for("home"))


@app.route("/users", methods=["POST"])
def users():
    """ New user signup API
        Form fields:
            - email
            - password
    """
    email = request.form.get("email")
    password = request.form.get("password")
    try:
        AUTH.register_user(email, password)
        return jsonify({"email": email, "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route("/profile")
def profile() -> str:
    """ User profile API
        Return:
            - user email JSON represented
            - 403 if session_id is not linked to any user
    """
    ssid = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(ssid)
    if not user:
        abort(403)
    return jsonify({"email": user.email})


@app.route("/reset_password", methods=["POST"])
def get_reset_password_token() -> str:
    """ Reset password token API
        Form fields:
            - email
        Return:
            - email and reset token JSON represented
            - 403 if email is not associated with any user
    """
    email = request.form.get("email")
    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)

    return jsonify({"email": email, "reset_token": reset_token})


@app.route("/reset_password", methods=["PUT"])
def update_password():
    """ Password update API
        Form fields:
            - email
            - reset_token
            - new_password
        Return:
            - user email and password update message JSON represented
            - 403 if reset token is not provided or not linked to any user
    """
    email = request.form.get("email")
    new_password = request.form.get("new_password")
    reset_token = request.form.get("reset_token")

    try:
        AUTH.update_password(reset_token, new_password)
    except ValueError:
        abort(403)
    return jsonify({"email": email, "message": "Password updated"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
