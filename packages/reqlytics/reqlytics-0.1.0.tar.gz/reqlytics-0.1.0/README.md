# README.md (simplified)

# Reqlytics Python SDK

Reqlytics is a real-time API analytics middleware for Flask and FastAPI.

## Installation
```bash
pip install git+https://github.com/your-github/reqlytics-sdk.git
```

## Usage
### Flask
```python
from flask import Flask
from reqlytics import flask_analytics, flask_start_timer

app = Flask(__name__)
app.before_request(flask_start_timer)
app.after_request(flask_analytics("your_api_key", debug=True))
```

### FastAPI
```python
from fastapi import FastAPI
from reqlytics import fastapi_analytics

app = FastAPI()
app.add_middleware(fastapi_analytics, api_key="your_api_key", debug=True)
```

MIT License © 2025 – Reqlytics Team
