"""
Unit tests-old for FastAPI server routes

© 2025 SkillSetPRO – All rights reserved under the MIT License.
"""

import pytest
from fastapi.testclient import TestClient
from minimocker.server import app, load_routes
import os
import json
from jose import jwt

@pytest.fixture(scope="module")
def client():
    config_path = os.path.join(os.path.dirname(__file__), "../examples/mock_config.json")
    with open(config_path) as f:
        config = json.load(f)
    load_routes(config)
    return TestClient(app)

def generate_token():
    return jwt.encode({"user": "Alice"}, "mysecret", algorithm="HS256")

def test_get_user_success(client):
    token = generate_token()
    response = client.get("/api/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"

def test_get_user_unauthorized(client):
    response = client.get("/api/user")  # No token
    assert response.status_code == 401
