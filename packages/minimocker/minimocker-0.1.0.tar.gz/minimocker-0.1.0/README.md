# 🧪 MiniMocker

> A lightweight, no-code mock API server with hot reload and mock JWT validation — perfect for local development, integration testing, and API simulation.

---

## 🚀 Features

- 🔁 Hot-reloads when `mock_config.json` changes
- 🔐 Mock JWT token validation (`Authorization: Bearer ...`)
- ⏱ Simulate network delay
- 🧩 Serve any REST endpoint with static or dynamic responses
- ⚡ Simple CLI to launch in seconds
- 📦 Package-ready for PyPI (`pip install minimocker`)

---

## 📦 Installation

```bash
pip install minimocker
```

## 🧑‍💻 Usage
### 🟢 Start Mock Server
```bash

minimocker examples/mock_config.json --port 8080
```

#### 🔁 Live Reload
Any changes to the config file will auto-reload the routes without restarting the server.

#### 🛠 Configuration Example
```json
{
  "jwt_secret": "mysecret",
  "routes": [
    {
      "path": "/api/user",
      "method": "GET",
      "auth": true,
      "response": {
        "status": 200,
        "body": {
          "name": "Alice",
          "email": "alice@example.com"
        },
        "delay": 300
      }
    }
  ]
}
```

#### Supported Fields
| Field | 	Description |
|-------|---------------|
|path	| URL route |
|method	|HTTP method (GET, POST, etc.) |
|auth	|true to require Bearer token |
|status	|HTTP response code |
|body	|JSON response |
|delay	|Artificial delay in milliseconds |
|jwt_secret|	Secret key to validate incoming JWT tokens |

#### 🔐 JWT Validation
- If a route has "auth": true, requests must include a valid JWT in the Authorization header.

- Uses HS256 algorithm.

- Example header:

```makefile

Authorization: Bearer <your-jwt-token>
```
Generate a token at jwt.io with the secret you provide in mock_config.json.

#### 👥 Contributing
Contributions are welcome! Ideas for dynamic templating, mock headers, and request-based routing are on the roadmap.
