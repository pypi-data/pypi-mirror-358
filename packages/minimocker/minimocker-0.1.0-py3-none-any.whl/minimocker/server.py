import os
import json
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from .jwt_mock import verify_token
from .utils import log

def create_app():
    config_path = os.environ.get("MINIMOCKER_CONFIG")
    jwt_secret = os.environ.get("MINIMOCKER_SECRET", "")

    if not config_path:
        raise RuntimeError("MINIMOCKER_CONFIG env var is required")

    with open(config_path, "r") as f:
        config = json.load(f)

    if not isinstance(config, dict):
        raise TypeError(f"Config must be a JSON object with a 'routes' key. Got: {type(config)}")

    config["jwt_secret"] = jwt_secret

    app = FastAPI()

    def make_handler(route):
        async def handler(request: Request):
            # Auth Check
            if route.get("auth"):
                token = request.headers.get("Authorization", "").replace("Bearer ", "")
                if not verify_token(token, config["jwt_secret"]):
                    raise HTTPException(status_code=401, detail="Invalid or missing token")

            # Delay simulation
            delay = route["response"].get("delay", 0)
            if delay:
                await asyncio.sleep(delay / 1000.0)

            # Merge context: path, query, body
            context = dict(request.path_params)
            context.update(request.query_params)
            if request.method in ["POST", "PUT"]:
                try:
                    body_data = await request.json()
                    if isinstance(body_data, dict):
                        context.update(body_data)
                except Exception:
                    pass

            # Resolve response body with template
            raw_body = route["response"].get("body", {})
            resolved_body = {
                k: (v.format(**context) if isinstance(v, str) else v)
                for k, v in raw_body.items()
            }

            return JSONResponse(
                status_code=route["response"].get("status", 200),
                content=resolved_body
            )

        return handler

    for route in config.get("routes", []):
        app.add_api_route(route["path"], make_handler(route), methods=[route["method"]])
        log(f"Loaded route {route['method']} {route['path']}")

    return app
