#!/usr/bin/env python3
""" Session Authentication
"""
from api.v1.auth.auth import Auth
from models.user import User
import uuid


class SessionAuth(Auth):
    """Session Authentication Class"""
    user_id_by_session_id = {}

    def create_session(self, user_id: str = None) -> str:
        """Creates Session ID"""

        if user_id is None or not isinstance(user_id, str):
            return None

        ssid = str(uuid.uuid4())

        self.user_id_by_ssid[ssid] = user_id

        return ssid

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """Returns a User ID"""

        if session_id is None or not isinstance(session_id, str):
            return None

        return self.user_id_by_session_id.get(session_id)

    def current_user(self, request=None):
        """Returns a User instance"""

        ssid = self.session_cookie(request)

        if ssid is None:
            return None

        user_id = self.user_id_for_session_id(ssid)

        return User.get(user_id)

    def destroy_session(self, request=None):
        """Deletes de user session"""

        if request is None:
            return False

        ssid = self.session_cookie(request)
        if ssid is None:
            return False

        user_id = self.user_id_for_session_id(ssid)

        if not user_id:
            return False

        try:
            del self.user_id_by_session_id[ssid]
        except Exception:
            pass

        return True
