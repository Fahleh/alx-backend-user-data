#!/usr/bin/env python3
"""Basic authentication module for the API.
"""
import re
import base64
import binascii
from typing import Tuple, TypeVar

from .auth import Auth
from models.user import User


class BasicAuth(Auth):
    """Basic authentication class.
    """

    def extract_base64_authorization_header(
            self,
            authorization_header: str) -> str:
        """
        Extracts the Base64 part of the Authorization header
        for a Basic Authentication.
        """
        if type(authorization_header) == str:
            pattern = r'Basic (?P<token>.+)'
            auth_token = re.fullmatch(pattern, authorization_header.strip())
            if auth_token is not None:
                return auth_token.group('token')
        return None

    def decode_base64_authorization_header(
            self,
            base64_authorization_header: str,
    ) -> str:
        """Returns the decoded value of a Base64 string.
        """
        if type(base64_authorization_header) == str:
            try:
                token = base64.b64decode(
                    base64_authorization_header,
                    validate=True,
                )
                return token.decode('utf-8')
            except (binascii.Error, UnicodeDecodeError):
                return None

    def extract_user_credentials(
            self,
            decoded_base64_authorization_header: str,
    ) -> Tuple[str, str]:
        """
        Returns the user email and password from the Base64 decoded value.
        """
        if type(decoded_base64_authorization_header) == str:
            auth_details = r'(?P<user>[^:]+):(?P<password>.+)'
            matched = re.fullmatch(
                auth_details,
                decoded_base64_authorization_header.strip(),
            )
            if matched is not None:
                user = matched.group('user')
                password = matched.group('password')
                return user, password
        return None, None

    def user_object_from_credentials(
            self,
            user_email: str,
            user_pwd: str) -> TypeVar('User'):
        """Returns the User instance based on his email and password.
        """
        if type(user_email) == str and type(user_pwd) == str:
            try:
                user_obj = User.search({'email': user_email})
            except Exception:
                return None
            if len(user_obj) <= 0:
                return None
            if user_obj[0].is_valid_password(user_pwd):
                return user_obj[0]
        return None

    def current_user(self, request=None) -> TypeVar('User'):
        """Retrieves the User instance for a request.
        """
        auth_value = self.authorization_header(request)
        b64_token = self.extract_base64_authorization_header(auth_value)
        auth_token = self.decode_base64_authorization_header(b64_token)
        email, password = self.extract_user_credentials(auth_token)
        return self.user_object_from_credentials(email, password)
