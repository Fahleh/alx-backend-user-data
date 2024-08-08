#!/usr/bin/env python3
"""Session authentication with expiration module for the API.
"""
import os
from flask import request
from datetime import datetime, timedelta

from .session_auth import SessionAuth


class SessionExpAuth(SessionAuth):
    """Session authentication class with expiration.
    """

    def __init__(self) -> None:
        """Initializes a new SessionExpAuth instance.
        """
        super().__init__()
        try:
            self.session_duration = int(os.getenv('SESSION_DURATION', '0'))
        except Exception:
            self.session_duration = 0

    def create_session(self, user_id=None):
        """Creates a user session id.
        """
        session_id = super().create_session(user_id)
        if type(session_id) != str:
            return None
        self.user_id_by_session_id[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
        }
        return session_id

    def user_id_for_session_id(self, session_id=None) -> str:
        """Retrieves the user's session id."""
        if session_id in self.user_id_by_session_id:
            session = self.user_id_by_session_id[session_id]
            if self.session_duration <= 0:
                return session['user_id']
            if 'created_at' not in session:
                return None
            start = datetime.now()
            duration = timedelta(seconds=self.session_duration)
            end = session['created_at'] + duration
            if end < start:
                return None
            return session['user_id']
        return None
        