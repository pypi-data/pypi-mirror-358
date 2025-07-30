"""
Unit tests-old for jwt_mock

© 2025 SkillSetPRO – All rights reserved under the MIT License.
"""

from minimocker.jwt_mock import verify_token
from jose import jwt

def test_verify_token():
    secret = "testsecret"
    token = jwt.encode({"user": "alice"}, secret, algorithm="HS256")
    decoded = verify_token(token, secret)
    assert decoded["user"] == "alice"


def test_invalid_token():
    invalid_token = "invalid.jwt.token"
    result = verify_token(invalid_token, "wrongsecret")
    assert result is None
