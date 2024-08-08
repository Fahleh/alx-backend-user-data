#!/usr/bin/env python3
"""Module of session authenticating views.
"""
import os
from typing import Tuple
from flask import abort, jsonify, request

from models.user import User
from api.v1.views import app_views


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def login() -> Tuple[str, int]:
    """
    POST method that returns JSON representation of a User object.
    """
    email = request.form.get('email')
    if email is None or len(email.strip()) == 0:
        return jsonify({"error": "email missing"}), 400
    pwrd = request.form.get('password')
    if pwrd is None or len(pwrd.strip()) == 0:
        return jsonify({"error": "password missing"}), 400
    try:
        user = User.search({'email': email})
    except Exception:
        return jsonify({"error": "no user found for this email"}), 404
    if len(user) <= 0:
        return jsonify({"error": "no user found for this email"}), 404
    if user[0].is_valid_password(pwrd):
        from api.v1.app import auth
        sessiond_id = auth.create_session(getattr(user[0], 'id'))
        result = jsonify(user[0].to_json())
        result.set_cookie(os.getenv("SESSION_NAME"), sessiond_id)
        return result
    return jsonify({"error": "wrong password"}), 401


@app_views.route(
    '/auth_session/logout', methods=['DELETE'], strict_slashes=False)
def logout() -> Tuple[str, int]:
    """Deletes the user's session."""
    from api.v1.app import auth
    destroyed = auth.destroy_session(request)
    if not destroyed:
        abort(404)
    return jsonify({})
