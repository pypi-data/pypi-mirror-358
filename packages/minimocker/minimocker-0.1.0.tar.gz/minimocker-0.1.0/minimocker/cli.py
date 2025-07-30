"""
MiniMocker – CLI entry point for launching the mock server

© 2025 SkillSetPRO – All rights reserved under the MIT License.
"""
import argparse
import os
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="MiniMocker API Mock Server")
    parser.add_argument("--config", required=True, help="Path to routes config file (JSON/YAML)")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--secret", help="Secret key for mock JWT validation")
    parser.add_argument("--reload", action="store_true", help="Enable hot reloading")

    args = parser.parse_args()
    os.environ["MINIMOCKER_CONFIG"] = args.config
    if args.secret:
        os.environ["MINIMOCKER_SECRET"] = args.secret

    uvicorn.run("minimocker.server:create_app", host=args.host, port=args.port, reload=args.reload, factory=True)
