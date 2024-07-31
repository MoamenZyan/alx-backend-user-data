#!/usr/bin/env python3

"""
Hashing Password
"""

import bcrypt


def hash_password(password: str) -> bytes:
    """ Return hashed password """
    encoded = password.encode()
    hashed = bcrypt.hashpw(encoded, bcrypt.gensalt())

    return hashed


def is_valid(hashed_password: bytes, password: str) -> bool:
    """ Check the hash password with the normal text """
    check = False
    encoded = password.encode()
    if bcrypt.checkpw(encoded, hashed_password):
        check = True
    return check
