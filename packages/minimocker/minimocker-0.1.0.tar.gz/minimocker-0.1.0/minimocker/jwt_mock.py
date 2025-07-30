"""
MiniMocker – Mock JWT token decoder and validator

© 2025 SkillSetPRO – All rights reserved under the MIT License.
"""


from jose import jwt, JWTError

def verify_token(token: str, secret: str):
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except JWTError:
        return None
