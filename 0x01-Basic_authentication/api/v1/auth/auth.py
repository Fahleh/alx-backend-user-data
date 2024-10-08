#!/usr/bin/env python3
"""Authentication module for the API.
"""
import re
import os
from typing import List, TypeVar
from flask import request


class Auth:
    """Authentication class.
    """

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """Checks the authentication requirements of a path.
        """
        if path is not None and excluded_paths is not None:
            for path_excluded in map(lambda x: x.strip(), excluded_paths):
                matched = ""
                if path_excluded[-1] == "*":
                    matched = f"{path_excluded[0:-1]}.*"
                elif path_excluded[-1] == "/":
                    matched = f"{path_excluded[0:-1]}/*"
                else:
                    matched = f"{path_excluded}/*"
                if re.match(matched, path):
                    return False
        return True

    def authorization_header(self, request=None) -> str:
        """Gets the authorization header from the request.
        """
        if request is not None:
            return request.headers.get('Authorization', None)
        return None

    def current_user(self, request=None) -> TypeVar('User'):
        """Gets the current user.
        """
        return None

    def session_cookie(self, request=None) -> str:
        """Gets the value of the cookie named SESSION_NAME.
        """
        if request is not None:
            cookie = os.getenv('SESSION_NAME')
            return request.cookies.get(cookie)
        return None
