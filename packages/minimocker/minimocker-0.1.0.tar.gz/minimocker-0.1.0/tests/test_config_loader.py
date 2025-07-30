"""
Unit tests-old for config_loader

© 2025 SkillSetPRO – All rights reserved under the MIT License.
"""

import os
import json
import pytest
from minimocker.config_loader import load_config

def test_load_config():
    path = os.path.join(os.path.dirname(__file__), "../examples/mock_config.json")
    config = load_config(path)
    assert "routes" in config
    assert config["jwt_secret"] == "mysecret"
    assert config["routes"][0]["path"] == "/api/user"
