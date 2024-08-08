#!/usr/bin/env python3
"""Session authentication with expiration
and storage support module for the API.
"""
from flask import request
from datetime import datetime, timedelta

from models.user_session import UserSession
from .session_exp_auth import SessionExpAuth


class SessionDBAuth(SessionExpAuth):
    """Session authentication with db storage support.
    """

    def create_session(self, user_id=None) -> str:
        """Creates and stores a new instance of UserSession.
        """
        session_id = super().create_session(user_id)
        if type(session_id) == str:
            kwargs = {
                'user_id': user_id,
                'session_id': session_id,
            }
            session = UserSession(**kwargs)
            session.save()
            return session_id
        return None

    def user_id_for_session_id(self, session_id=None):
        """
        Returns the user id associated with a given session id.
        """
        try:
            session = UserSession.search({'session_id': session_id})
        except Exception:
            return None
        if len(session) <= 0:
            return None
        start = datetime.now()
        duration = timedelta(seconds=self.session_duration)
        end = session[0].created_at + duration
        if end < start:
            return None
        return session[0].user_id

    def destroy_session(self, request=None) -> bool:
        """Destroys a user session.
        """
        session_id = self.session_cookie(request)
        try:
            sessions = UserSession.search({'session_id': session_id})
        except Exception:
            return False
        if len(sessions) <= 0:
            return False
        sessions[0].remove()
        return True
